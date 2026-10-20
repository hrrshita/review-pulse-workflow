# Review Pulse Workflow — Groww (Milestone 1 product)

Turns raw app reviews into (1) a ≤250-word weekly product pulse and (2) a ≤6-bullet customer-facing fee explainer, then logs both through **MCP tools after an approval step**.

## How to run
```bash
pip install -r requirements.txt
python make_sample_reviews.py      # demo data (SYNTHETIC) -> data/reviews_sample.csv
# OPTIONAL, recommended for submission: real public reviews
python fetch_reviews.py            # -> data/reviews.csv (last 12 weeks, Google Play). analysis.py uses it automatically
python workflow.py                 # CLI: shows outputs, asks y/n, then calls MCP tools
streamlit run app.py               # UI with Approve / Reject buttons
```

## Pipeline
1. **Review intelligence** (`analysis.py`): last 12 weeks, PII scrubbed; TF-IDF + KMeans seeded with 5 candidate themes (max 5); top 3 by volume; 3 quotes = review closest to each top theme's centroid; fee confusion = fee term mentioned together with confusion language, highest count wins.
2. **Weekly pulse** (`generate.py`): themes, 3 quotes, key observation, 3 actions; trimmed automatically to ≤250 words.
3. **Fee explainer** (`generate.py`, `sources.py`): 6 neutral bullets, 2 source links, "Last checked: <date>".
4. **MCP** (`mcp_server.py`): tools `append_to_notes` and `create_email_draft` (writes a `.eml` draft, never sends).

## Where MCP approval happens
- `workflow.py`: the `input("Approve these actions? (y/n)")` line. `app.py`: the **Approve** button. Nothing runs before that.
- Second gate: both MCP tools return `REFUSED` unless called with `approved=True`.
- `--approve` flag in `workflow.py` skips the prompt for testing only.

## Fee issue identified from reviews
**Exit load** — in the sample run, 36 of 114 reviews (32%) mention an exit load deducted at redemption that users say was not shown beforehand.
⚠️ The bundled run uses **synthetic sample reviews**, so these numbers and quotes are illustrative. Run `fetch_reviews.py`, re-run the workflow, and use the real outputs for submission. If real reviews point to a different fee (e.g., brokerage/DP charges), `generate.py` will say no explainer is configured; add official sources in `sources.py` and a bullet set for that fee.

## Known limits
- Notes and email draft are written to local files via MCP (`output/notes_log.md`, `output/drafts/*.eml`). To log to Google Docs/Notion/Gmail, swap the tool bodies in `mcp_server.py` for a connector or Zapier/Make webhook.
- Streamlit Cloud has an ephemeral filesystem; notes/drafts there disappear on restart. Use the CLI locally for the "Notes snippet" and "Email draft" evidence.
- Theme labels come from a keyword lexicon (`THEME_LEX`); the pipeline does not call an LLM.
- Explainer sources: one AMC page (Edelweiss MF) and an AMC-hosted copy of the SEBI 30 Jun 2009 circular. Replace the latter with a sebi.gov.in link if you find one.
- Re-check the sources and update the "Last checked" date before each use.

## Deliverables (`deliverables/`)
`weekly_pulse.md` · `fee_explainer.md` · `notes_snippet.md` · `email_draft.txt` · `reviews_sample.csv` · `sources.md`
