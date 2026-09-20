import streamlit as st

from src.agent import guarded_tool_call
from src.blockchain import add_to_ledger, get_ledger
from src.evaluator import evaluate_batch
from src.evaluation_cases import EVALUATION_CASES
from src.honeypot import honeypot_trap
from src.moss_validator import runtime_guard

st.set_page_config(page_title="AgentGuard - YC Winner", layout="wide", page_icon="🛡️")

# --- UI ---
st.markdown(
    """
    <style>
    .block-container { max-width: 1180px; padding-top: 2.5rem; }
    .eyebrow { color: #16a085; font-size: 0.76rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; }
    .hero { border-bottom: 1px solid #d9e2df; padding-bottom: 1.5rem; margin-bottom: 1.5rem; }
    .hero h1 { color: #102a2a; font-size: 2.8rem; letter-spacing: -0.04em; margin: 0.25rem 0 0.5rem; }
    .hero p { color: #526563; font-size: 1.05rem; max-width: 720px; }
    .decision { border-radius: 10px; padding: 1.4rem 1.5rem; margin: 1rem 0; border: 1px solid; }
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
    </style>
    <div class="hero">
      <div class="eyebrow">Runtime safety gateway · local retrieval demo</div>
      <h1>AgentGuard</h1>
      <p>Validate context before an AI agent executes a sensitive action. Retrieve evidence, enforce policy, and leave an explainable audit trail.</p>
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

guard_tab, evaluation_tab, audit_tab = st.tabs(["Guardrail", "Evaluation", "Audit trail"])

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
        st.caption("Retrieval mode is shown after each guardrail check.")
        run_check = st.button("Run guardrail check", use_container_width=True, type="primary")

    with right:
        st.markdown("#### Decision console")
        if run_check:
            agent_request = guarded_tool_call(agent_action, doc_hash_input)
            result = agent_request["guard"]
            trap = honeypot_trap(doc_hash_input, not result["allow"])
            ledger_block = add_to_ledger(doc_hash_input, result, agent_action)
            decision_class = result["decision"].lower()
            st.markdown(
                f'<div class="decision {decision_class}"><h2>{result["decision"]}</h2><p>{result["reason"]}</p></div>',
                unsafe_allow_html=True,
            )
            metric_one, metric_two, metric_three = st.columns(3)
            metric_one.metric("Trust", f"{result['trust'] * 100:.0f}%")
            metric_two.metric("Retrieval", format_latency(result["latency"]))
            metric_three.metric("Mode", result["retrieval_mode"])
            st.caption(f"Retrieval source: {result['retrieval_mode']}")
            st.write(f"**Evidence:** {result['doc']} · {result['vendor']}")
            if trap["activated"]:
                st.warning(f"Honeypot trace activated: {trap['trace_id']}")
            st.write(f"**Tool execution:** {'Executed' if agent_request['executed'] else 'Prevented'}")
            if agent_request["review_request"]:
                st.info(
                    "Human review queued: "
                    f"{agent_request['review_request']['review_id']}"
                )
            with st.expander("View decision payload"):
                st.json(agent_request)
            with st.expander("View audit entry"):
                st.json(ledger_block)
        else:
            st.info("Choose a scenario and run the check to see whether the agent may proceed.")

with evaluation_tab:
    st.markdown("#### Reproducible safety evaluation")
    metric_one, metric_two, metric_three, metric_four, metric_five = st.columns(5)
    metric_one.metric("Accuracy", f"{evaluation['accuracy'] * 100:.0f}%")
    metric_two.metric("Blocked", str(evaluation["blocked"]))
    metric_three.metric("Cases", str(evaluation["total_cases"]))
    metric_four.metric("Median latency", format_latency(evaluation["median_latency_ms"]))
    metric_five.metric("p95 latency", format_latency(evaluation["p95_latency_ms"]))
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

with audit_tab:
    st.markdown("#### Application audit chain")
    st.caption("Each decision is linked to the previous entry for traceability. This is an application hash chain, not an external blockchain.")
    ledger = get_ledger()
    if ledger:
        for block in reversed(ledger[-5:]):
            decision = block["decision"].lower()
            st.markdown(
                f'<div class="result-row result-{decision}">'
                f'<strong><span class="status-badge badge-{decision}">{block["decision"]}</span> '
                f'Block #{block["block_no"]}</strong>'
                f'<p><code>{block["timestamp"]}</code> · '
                f'<code>{block["doc_hash"]}</code> · {format_latency(block["latency_ms"])}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("No decisions have been recorded in this session yet.")

st.divider()
st.caption("AgentGuard · Runtime guardrails, context validation, and explainable audit evidence")