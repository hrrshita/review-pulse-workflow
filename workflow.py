"""End-to-end: analyze -> pulse -> explainer -> APPROVAL GATE -> MCP tool calls.
Usage: python workflow.py            (asks y/n before any action)
       python workflow.py --approve  (non-interactive demo; skips the prompt - for testing only)"""
import sys, asyncio
from analysis import analyze
from generate import weekly_pulse, fee_explainer, explainer_text, notes_entry, email

async def run_mcp(entry, subject, body):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    params = StdioServerParameters(command=sys.executable, args=["mcp_server.py"])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            res1 = await s.call_tool("append_to_notes", {"entry": entry, "approved": True})
            res2 = await s.call_tool("create_email_draft", {"subject": subject, "body": body, "approved": True})
            return [res1.content[0].text, res2.content[0].text]

def build():
    a = analyze(); pulse = weekly_pulse(a); e = fee_explainer(a)
    subject, body = email(a, pulse, e)
    return a, pulse, e, notes_entry(a, pulse, e), subject, body

if __name__ == "__main__":
    a, pulse, e, entry, subject, body = build()
    print(pulse, "\n\n", explainer_text(e), "\n")
    print("PROPOSED ACTIONS (nothing has run yet):\n 1. append_to_notes -> output/notes_log.md\n 2. create_email_draft ->", subject)
    ok = "--approve" in sys.argv or input("\nApprove these actions? (y/n): ").strip().lower() == "y"   # <-- APPROVAL GATE
    if not ok:
        print("Not approved. No actions taken."); sys.exit(0)
    for line in asyncio.run(run_mcp(entry, subject, body)):
        print(line)
