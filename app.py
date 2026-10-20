import asyncio, streamlit as st
from workflow import build, run_mcp
from generate import explainer_text

st.set_page_config(page_title="Review Pulse Workflow", page_icon="📈", layout="wide")
st.title("Groww Review Pulse → Fee Explainer → MCP")
st.caption("Facts-only support content. Nothing is saved or drafted until you approve.")

if "built" not in st.session_state:
    st.session_state.built = build()
a, pulse, e, entry, subject, body = st.session_state.built

if a["synthetic"]:
    st.warning("Running on SAMPLE (synthetic) reviews. Run fetch_reviews.py to use real Groww reviews.")
c1, c2 = st.columns(2)
with c1:
    st.subheader("Step 1 · Themes"); st.dataframe(a["themes"], hide_index=True)
    st.write(f"**Fee confusion:** {a['fee']['name']} — {a['fee']['confused']} reviews ({a['fee']['pct']}%)")
    st.subheader("Step 2 · Weekly pulse"); st.markdown(pulse)
with c2:
    st.subheader("Step 3 · Fee explainer"); st.markdown(explainer_text(e))
    st.subheader("Email draft preview"); st.text(f"Subject: {subject}\n\n{body[:600]}...")

st.divider()
st.subheader("Approval gate (MCP)")
st.info("On approval: (1) append entry to Notes via MCP `append_to_notes`, (2) create an email draft via MCP `create_email_draft`. No email is sent.")
col1, col2 = st.columns(2)
if col1.button("✅ Approve and run MCP actions", type="primary"):
    for line in asyncio.run(run_mcp(entry, subject, body)):
        st.success(line)
if col2.button("❌ Reject"):
    st.write("Rejected. No actions taken.")
