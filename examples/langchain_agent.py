# examples/langchain_agent.py
# Task 6: Developer Experience Example - LangChain + AgentGuard
import os
import sys
# FIX: Add project root to path so 'src' is found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.honeypot import honeypot_trap

def agentguard_security_tool(doc_hash: str) -> str:
    is_malicious = any(x in doc_hash.lower() for x in ["malicious", "inject", "hack", "prompt"])
    result = honeypot_trap(doc_hash, is_malicious)
    if is_malicious:
        return f"[BLOCKED] Document {doc_hash} flagged by AgentGuard."
    else:
        return f"[SAFE] Document {doc_hash} passed. Trace: {result}"

def get_langchain_tools():
    try:
        from langchain.tools import tool
        @tool
        def AgentGuardCheck(doc_hash: str) -> str:
            return agentguard_security_tool(doc_hash)
        return [AgentGuardCheck]
    except ImportError:
        return []

if __name__ == "__main__":
    print("=== AgentGuard + LangChain Example - Task 6 ===\n")
    for doc in ["safe_doc_123", "malicious_injection_attempt", "normal_report.pdf"]:
        print(f"Checking: {doc}")
        print(f" -> {agentguard_security_tool(doc)}\n")
