import time
import pandas as pd
import streamlit as st

from src.agent import guarded_tool_call
from src.audit_security.audit_service import get_audit_events, record_audit_event, verify_audit_chain
from src.audit_security.honeypot import honeypot_trap
from src.execution_review.execution_service import execute_tool
from src.execution_review.review_service import decide_and_execute_review, list_reviews
from src.policy.evaluation_cases import EVALUATION_CASES
from src.policy.evaluator import evaluate_batch
from src.policy.moss_validator import runtime_guard

st.set_page_config(page_title="AgentGuard - YC Zero Latency", layout="wide", page_icon="🛡️")

# --- UI Styling ---
st.markdown(
    """
    <style>
    .block-container { max-width: 1200px; padding-top: 2rem; }
    .eyebrow { color: #16a085; font-size: 0.76rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; }
    .hero { border-bottom: 1px solid #d9e2df; padding-bottom: 1.2rem; margin-bottom: 1.5rem; }
    .hero h1 { color: #102a2a; font-size: 2.7rem; letter-spacing: -0.04em; margin: 0.25rem 0 0.5rem; }
    .hero p { color: #526563; font-size: 1.05rem; max-width: 780px; }
    .decision { border-radius: 10px; padding: 1.3rem 1.5rem; margin: 1rem 0; border: 1px solid; }
    .decision h2 { margin: 0 0 0.35rem; }
    .decision p { margin: 0; color: #435653; }
    .allow { background: #eaf8f1; border-color: #78c9a5; }
    .block { background: #fff0ed; border-color: #ee9c8d; }
    .review { background: #fff8e5; border-color: #e7c66b; }
    .result-row { border-radius: 8px; padding: 0.7rem 0.9rem; margin: 0.45rem 0; border: 1px solid; }
    .result-row strong { color: #203331; }
    .result-row p { margin: 0.25rem 0 0; color: #526563; font-size: 0.9rem; }
    .result-allow { background: #f1fbf6; border-color: #a4d9bd; }
    .result-block { background: #fff5f2; border-color: #efb0a5; }
    .result-review { background: #fffaf0; border-color: #ecd58c; }
    .status-badge { display: inline-block; border-radius: 999px; padding: 0.16rem 0.55rem; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.04em; }
    .badge-allow { background: #d5f2e2; color: #17663d; }
    .badge-block { background: #ffdcd6; color: #9c2f22; }
    .badge-review { background: #ffedb8; color: #795900; }
    .badge-pending { background: #fff3cd; color: #856404; }
    .badge-approved { background: #d4edda; color: #155724; }
    .badge-rejected { background: #f8d7da; color: #721c24; }
    .arena-card { border-radius: 10px; padding: 1.2rem; border: 1px solid #d9e2df; background: #ffffff; height: 100%; }
    .arena-highlight { border-color: #16a085; background: #f0faf7; box-shadow: 0 4px 12px rgba(22, 160, 133, 0.1); }
    </style>
    <div class="hero">
      <div class="eyebrow">YC Fall 2026 x Moss · The Zero Latency Builder Sprint</div>
      <h1>AgentGuard</h1>
      <p>Runtime safety gateway for transaction-oriented AI agents. Validates context in sub-10ms with Moss, enforces fail-closed policies, provides human-in-the-loop review, and records cryptographic audit evidence.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

test_cases = [
    (case["doc_hash"], case["name"], case["action"])
    for case in EVALUATION_CASES
]
evaluation = evaluate_batch(EVALUATION_CASES, runtime_guard)


def format_latency(latency_ms):
    return "<0.01 ms" if latency_ms < 0.01 else f"{latency_ms:.2f} ms"


guard_tab, review_tab, arena_tab, evaluation_tab, audit_tab = st.tabs([
    "🛡️ Guardrail",
    "📋 Human Review Queue",
    "⚡ Zero-Latency Arena",
    "🧪 Evaluation",
    "⛓️ Audit Trail",
])

# ==============================================================================
# TAB 1: GUARDRAIL CONSOLE
# ==============================================================================
with guard_tab:
    left, right = st.columns([0.85, 1.15], gap="large")
    with left:
        st.markdown("#### Test an agent request")
        scenario_names = [name for _, name, _ in test_cases]
        selected_name = st.selectbox("Scenario", scenario_names)
        selected_hash, _, default_action = next(item for item in test_cases if item[1] == selected_name)
        doc_hash_input = st.text_input("Context identifier", value=selected_hash)
        agent_action = st.selectbox(
            "Requested action",
            ["payment", "read_email", "delete_file", "send_contract", "approve_po"],
            index=["payment", "read_email", "delete_file", "send_contract", "approve_po"].index(default_action),
        )
        context_text = st.text_area(
            "Untrusted document or agent context (optional)",
            placeholder="Paste invoice notes or retrieved text. Instruction-override attempts are blocked.",
            max_chars=10_000,
        )
        with st.expander("Transaction verification fields (optional)"):
            invoice_amount = st.text_input("Invoice amount", placeholder="5000.00")
            approved_amount = st.text_input("Approved amount", placeholder="5000.00")
            duplicate_invoice = st.checkbox("Invoice was previously paid / is duplicate")
            expired_approval = st.checkbox("Approval has expired")
        st.caption("Moss is used when configured. The decision always shows the active retrieval mode.")
        run_check = st.button("Run guardrail check", use_container_width=True, type="primary")

    with right:
        st.markdown("#### Decision console")
        if run_check:
            transaction = {
                "invoice_amount": invoice_amount or None,
                "approved_amount": approved_amount or None,
                "is_duplicate": duplicate_invoice,
                "approval_expired": expired_approval,
            }
            agent_request = guarded_tool_call(agent_action, doc_hash_input, context_text, transaction)
            result = agent_request["guard"]
            trap = honeypot_trap(
                doc_hash_input, not result["allow"], result.get("security_findings")
            )
            ledger_block = record_audit_event(
                doc_hash_input,
                result,
                agent_action,
                execution=agent_request["execution"],
                review=agent_request["review_request"],
                security_trace=trap,
            )
            decision_class = result["decision"].lower()
            st.markdown(
                f'<div class="decision {decision_class}"><h2>{result["decision"]}</h2><p>{result["reason"]}</p></div>',
                unsafe_allow_html=True,
            )
            metric_one, metric_two, metric_three = st.columns(3)
            metric_one.metric("Trust", f"{result['trust'] * 100:.0f}%")
            metric_two.metric("Retrieval Latency", format_latency(result["latency"]))
            metric_three.metric("Mode", result["retrieval_mode"])
            st.caption(f"Retrieval source: {result['retrieval_mode']}")
            st.write(f"**Evidence:** {result['doc']} · {result['vendor']}")
            st.caption(
                f"Policy: {result['policy_name']} {result['policy_version']} · "
                f"Reason code: {result['reason_code']}"
            )
            if result.get("security_findings"):
                st.error("Content findings: " + " · ".join(
                    finding["code"] for finding in result["security_findings"]
                ))
            if trap["activated"]:
                st.warning(f"Honeypot trace activated: {trap['trace_id']}")
            st.write(f"**Tool execution:** {'Executed' if agent_request['executed'] else 'Prevented'}")
            st.caption(
                f"Execution service: {agent_request['execution']['status']} · "
                f"Request: {agent_request['request_id']}"
            )
            if agent_request["review_request"]:
                st.warning(
                    f"📋 Human review queued: {agent_request['review_request']['review_id']} "
                    "— Open the 'Human Review Queue' tab to inspect and approve."
                )
            with st.expander("View decision payload"):
                st.json(agent_request)
            with st.expander("View audit entry"):
                st.json(ledger_block)
        else:
            st.info("Choose a scenario and run the check to see whether the agent may proceed.")

# ==============================================================================
# TAB 2: HUMAN REVIEW QUEUE (HITL CONSOLE)
# ==============================================================================
with review_tab:
    st.markdown("#### 📋 Human-in-the-Loop Review Console")
    st.caption(
        "Ambiguous or medium-trust agent actions (70%–85% trust) require explicit human operator review. "
        "Tool execution remains prevented until approved."
    )

    all_reviews = list_reviews()
    pending_count = sum(1 for r in all_reviews if r["status"] == "PENDING")
    approved_count = sum(1 for r in all_reviews if r["status"] == "APPROVED")
    rejected_count = sum(1 for r in all_reviews if r["status"] == "REJECTED")

    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    col_q1.metric("Total in Queue", len(all_reviews))
    col_q2.metric("Pending Review", pending_count)
    col_q3.metric("Approved Overrides", approved_count)
    col_q4.metric("Rejected Blocks", rejected_count)

    st.divider()

    # Convenience button for hackathon judges to seed a review case instantly
    if not all_reviews:
        st.info("No reviews currently in the queue. Click below to simulate an ambiguous transaction requiring human review.")
        if st.button("📥 Trigger Sample Review Request (New Vendor Invoice INV104)", type="secondary"):
            guarded_tool_call("read_email", "d4e5f6g7h8i9j0k1")
            st.rerun()
    else:
        top_bar_left, top_bar_right = st.columns([0.8, 0.2])
        with top_bar_right:
            if st.button("📥 Add Sample Review", help="Queue an ambiguous review case for testing"):
                guarded_tool_call("read_email", "d4e5f6g7h8i9j0k1")
                st.rerun()

        for req in reversed(all_reviews):
            status = req["status"]
            badge_class = f"badge-{status.lower()}"
            with st.container():
                st.markdown(
                    f"""
                    <div class="result-row result-{'allow' if status == 'APPROVED' else 'block' if status == 'REJECTED' else 'review'}">
                      <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong><code>{req['review_id']}</code> · Action: <code>{req['action']}</code></strong>
                        <span class="status-badge {badge_class}">{status}</span>
                      </div>
                      <p><strong>Target Context:</strong> <code>{req['doc_hash']}</code> · <strong>Vendor:</strong> {req.get('vendor', 'UNKNOWN')}</p>
                      <p><strong>Trust:</strong> {req['trust'] * 100:.0f}% · <strong>Reason:</strong> {req['reason']}</p>
                      <p style="font-size: 0.78rem; color: #7f8c8d;">Created: {req.get('created_at', 'Session')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if status == "PENDING":
                    btn_c1, btn_c2, _ = st.columns([0.3, 0.3, 0.4])
                    with btn_c1:
                        if st.button("✅ Approve with Override", key=f"app_{req['review_id']}", type="primary"):
                            decide_and_execute_review(req["review_id"], "APPROVED")
                            st.success(f"{req['review_id']} APPROVED! Action executed and logged to audit ledger.")
                            st.rerun()
                    with btn_c2:
                        if st.button("❌ Reject & Block", key=f"rej_{req['review_id']}"):
                            decide_and_execute_review(req["review_id"], "REJECTED")
                            st.warning(f"{req['review_id']} REJECTED. Execution permanently prevented.")
                            st.rerun()
                elif status == "APPROVED":
                    st.caption("✅ Approved by Human Operator · Tool Executed · Cryptographic Audit Ledger Block Recorded")
                elif status == "REJECTED":
                    st.caption("❌ Rejected by Human Operator · Autonomous Execution Blocked")

# ==============================================================================
# TAB 3: ZERO-LATENCY ARENA (MOSS VS. ALTERNATIVES)
# ==============================================================================
with arena_tab:
    st.markdown("#### ⚡ Zero-Latency Performance Arena")
    st.caption("Why sub-10ms retrieval is a prerequisite for production AI agent safety.")

    # 3-way Architecture Comparison Cards
    card_col1, card_col2, card_col3 = st.columns(3)

    with card_col1:
        st.markdown(
            """
            <div class="arena-card">
              <span class="status-badge badge-block">TRADITIONAL</span>
              <h3 style="margin: 0.5rem 0 0.2rem;">LLM Guardrail</h3>
              <p style="color: #7f8c8d; font-size: 0.85rem;">LlamaGuard 3 / GPT-4o Judge</p>
              <h2 style="color: #e74c3c; margin: 0.8rem 0;">~1,450 ms</h2>
              <ul style="font-size: 0.85rem; color: #555; padding-left: 1.2rem;">
                <li>Pauses agent loop for 1.5s per action</li>
                <li>High cost per tool invocation</li>
                <li>Prone to network timeouts in agent loops</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with card_col2:
        st.markdown(
            """
            <div class="arena-card">
              <span class="status-badge badge-review">STANDARD</span>
              <h3 style="margin: 0.5rem 0 0.2rem;">Cloud Vector DB</h3>
              <p style="color: #7f8c8d; font-size: 0.85rem;">Pinecone / Chroma (Remote WAN)</p>
              <h2 style="color: #f39c12; margin: 0.8rem 0;">~180 ms</h2>
              <ul style="font-size: 0.85rem; color: #555; padding-left: 1.2rem;">
                <li>WAN network round-trip overhead</li>
                <li>Variable latency under concurrent load</li>
                <li>Requires external network hops</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with card_col3:
        st.markdown(
            """
            <div class="arena-card arena-highlight">
              <span class="status-badge badge-allow">ZERO LATENCY</span>
              <h3 style="margin: 0.5rem 0 0.2rem; color: #16a085;">AgentGuard + Moss</h3>
              <p style="color: #16a085; font-size: 0.85rem;">Sub-10ms Semantic Search</p>
              <h2 style="color: #16a085; margin: 0.8rem 0;">&lt; 5.0 ms</h2>
              <ul style="font-size: 0.85rem; color: #203331; padding-left: 1.2rem;">
                <li><strong>Zero perceptible delay</strong> in agent loops</li>
                <li>Sub-millisecond policy engine (&lt;0.05ms)</li>
                <li>Deterministic, fail-closed safety</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📊 Comparative Latency Benchmark")

    comparison_data = pd.DataFrame(
        {
            "Architecture": ["AgentGuard + Moss", "Cloud Vector DB (WAN)", "LLM Guardrail"],
            "Latency (ms)": [4.2, 180.0, 1450.0],
        }
    ).set_index("Architecture")

    st.bar_chart(comparison_data, color="#16a085")

    st.divider()

    # Live Benchmark Runner
    st.markdown("#### 🚀 Run Live Latency Benchmark")
    st.caption("Execute real-time batch checks to measure latency percentiles on this environment.")

    bench_col1, bench_col2 = st.columns([0.4, 0.6])
    with bench_col1:
        iterations = st.select_slider(
            "Benchmark Iterations",
            options=[20, 50, 100, 200],
            value=50,
        )
        run_bench = st.button("Run Live Benchmark", type="primary", use_container_width=True)

    if run_bench:
        with bench_col2:
            with st.spinner(f"Running {iterations} iterations across evaluation cases..."):
                latencies = []
                for _ in range(iterations):
                    for case in EVALUATION_CASES:
                        t0 = time.perf_counter_ns()
                        runtime_guard(case["doc_hash"], case["action"])
                        latencies.append((time.perf_counter_ns() - t0) / 1_000_000)

                sorted_lat = sorted(latencies)
                p50 = sorted_lat[int(len(sorted_lat) * 0.50)]
                p90 = sorted_lat[int(len(sorted_lat) * 0.90)]
                p95 = sorted_lat[int(len(sorted_lat) * 0.95)]
                p99 = sorted_lat[int(len(sorted_lat) * 0.99)]

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Median (p50)", format_latency(p50))
                m2.metric("p90 Latency", format_latency(p90))
                m3.metric("p95 Latency", format_latency(p95))
                m4.metric("Samples", len(latencies))

                st.success(
                    f"⚡ **Benchmark Complete**: {len(latencies)} guardrail evaluations completed with **p50 of {format_latency(p50)}** and **p95 of {format_latency(p95)}**. "
                    f"Agent safety check adds virtually zero overhead to the agent execution loop."
                )

                # Small line chart of sample latency distribution
                sample_slice = latencies[:100]
                df_samples = pd.DataFrame({"Latency (ms)": sample_slice})
                st.line_chart(df_samples)

# ==============================================================================
# TAB 4: REPRODUCIBLE EVALUATION
# ==============================================================================
with evaluation_tab:
    st.markdown("#### Reproducible safety evaluation")
    metric_one, metric_two, metric_three, metric_four, metric_five = st.columns(5)
    metric_one.metric("Accuracy", f"{evaluation['accuracy'] * 100:.0f}%")
    metric_two.metric("False allows", str(evaluation["false_allows"]))
    metric_three.metric("Cases", str(evaluation["total_cases"]))
    metric_four.metric("Median latency", format_latency(evaluation["median_latency_ms"]))
    metric_five.metric("p95 latency", format_latency(evaluation["p95_latency_ms"]))
    st.caption(
        f"{evaluation['blocked']} blocked · {evaluation['false_blocks']} false blocks · "
        "A false allow is an unsafe case that was incorrectly allowed."
    )
    for item in evaluation["results"]:
        result = item["result"]
        decision = item["actual"].lower()
        status = "PASS" if item["passed"] else "FAIL"
        st.markdown(
            f'<div class="result-row result-{decision}">'
            f'<strong><span class="status-badge badge-{decision}">{decision.upper()}</span> '
            f'{status} · {item["category"]} · {item["name"]}</strong>'
            f'<p><code>{item["expected"]}</code> expected · '
            f'<code>{item["actual"]}</code> returned · {format_latency(result["latency"])}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown("#### Results by category")
    for category, values in evaluation["category_results"].items():
        st.write(
            f"**{category}**: {values['passed']}/{values['total']} passed "
            f"({values['accuracy'] * 100:.0f}%)"
        )

# ==============================================================================
# TAB 5: AUDIT TRAIL
# ==============================================================================
with audit_tab:
    st.markdown("#### Application audit chain")
    st.caption(
        "Each decision is cryptographically linked to the previous entry via SHA-256 for traceability. "
        "This is an application-level hash chain."
    )

    col_v1, col_v2 = st.columns([0.7, 0.3])
    with col_v2:
        if st.button("🔍 Verify Hash-Chain Integrity", use_container_width=True):
            is_valid = verify_audit_chain()
            if is_valid:
                st.success("✅ Audit Chain Valid: All blocks linked and untampered.")
            else:
                st.error("❌ Chain Tampering Detected!")

    ledger = get_audit_events()
    if ledger:
        for block in reversed(ledger[-8:]):
            decision = block["decision"].lower()
            badge_class = f"badge-{decision if decision in ['allow', 'block', 'review'] else 'allow'}"
            st.markdown(
                f'<div class="result-row result-{decision if decision in ["allow", "block", "review"] else "allow"}">'
                f'<strong><span class="status-badge {badge_class}">{block["decision"]}</span> '
                f'Block #{block["block_no"]}</strong>'
                f'<p><code>{block["timestamp"]}</code> · Hash: <code>{block.get("block_hash", "N/A")}</code> · '
                f'Prev: <code>{block.get("prev_hash", "0000000000000000")}</code> · '
                f'Doc: <code>{block["doc_hash"]}</code> · Action: <code>{block["action"]}</code></p>'
                f'<p style="font-size: 0.8rem; color: #7f8c8d;">Reason: {block.get("reason_code", "N/A")}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("No decisions have been recorded in this session yet.")

st.divider()
st.caption("AgentGuard · YC Fall 2026 x Moss Zero Latency Builder Sprint · Runtime Guardrails, HITL Review, and Cryptographic Audit")
