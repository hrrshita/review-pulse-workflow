"""MCP server exposing two approval-gated tools. Run via stdio by workflow.py / app.py.
Tools REFUSE to act unless approved=True (second gate behind the UI/CLI approval)."""
import json, datetime as dt
from pathlib import Path
from email.message import EmailMessage
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("product-pulse-tools")
OUT = Path("output"); (OUT / "drafts").mkdir(parents=True, exist_ok=True)

@mcp.tool()
def append_to_notes(entry: dict, approved: bool = False) -> str:
    """Append a weekly-pulse entry to the notes doc (output/notes_log.md). Requires approved=True."""
    if not approved:
        return "REFUSED: not approved"
    md = (f"\n---\n## {entry['date']}\n**Top themes:** {', '.join(entry['top_themes'])}\n\n"
          f"**Identified fee issue:** {entry['identified_fee_issue']}\n\n{entry['weekly_pulse']}\n\n"
          "**Explanation bullets**\n" + "\n".join(f"- {b}" for b in entry["explanation_bullets"]) +
          "\n\n**Sources**\n" + "\n".join(f"- {u}" for u in entry["source_links"]) + "\n")
    with open(OUT / "notes_log.md", "a", encoding="utf-8") as f:
        f.write(md)
    with open(OUT / "notes_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return "OK: appended to output/notes_log.md"

@mcp.tool()
def create_email_draft(subject: str, body: str, approved: bool = False) -> str:
    """Create an email DRAFT (.eml, never sent) in output/drafts. Requires approved=True."""
    if not approved:
        return "REFUSED: not approved"
    m = EmailMessage()
    m["Subject"], m["To"], m["From"], m["X-Unsent"] = subject, "product-team@example.com", "pulse-bot@example.com", "1"
    m.set_content(body)
    p = OUT / "drafts" / f"draft_{dt.datetime.now():%Y%m%d_%H%M%S}.eml"
    p.write_bytes(bytes(m))
    return f"OK: draft saved to {p} (not sent)"

if __name__ == "__main__":
    mcp.run()
