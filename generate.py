"""Step 2 (weekly pulse, <=250 words) and Step 3 (fee explainer, <=6 bullets, 2 official links)."""
import datetime as dt
from sources import EXPLAINER_LINKS

TODAY = dt.date(2026, 10, 20)
WORD_LIMIT = 250

def words(t): return len(t.split())

def weekly_pulse(a):
    th, q, fee = a["top3"], a["quotes"], a["fee"]
    tag = " [SAMPLE DATA]" if a["synthetic"] else ""
    themes = "\n".join(f"{i+1}. {r.theme} - {r.share_pct}% of reviews, avg {r.avg_rating}/5" for i, r in enumerate(th.itertuples()))
    def build(quotes):
        qs = "\n".join(f'- "{x["quote"]}" ({x["rating"]}/5)' for x in quotes)
        return f"""# Weekly Product Pulse - {TODAY.isoformat()}{tag}
Based on {a['n']} reviews, {a['date_range'][0]} to {a['date_range'][1]}.

**Top themes**
{themes}

**What users say**
{qs}

**Key observation**
{fee['name']} confusion shows up in {fee['pct']}% of all reviews ({fee['confused']} of {a['n']}). Users say the charge appears only after they redeem, and several assume direct plans carry no charges. Fee confusion is now the single largest complaint cluster.

**Action ideas**
1. Show the exact exit-load amount and the date it falls away on the redeem confirmation screen.
2. Add a short in-app "exit load" explainer next to each fund's redeem and SIP-stop actions.
3. Give support a standard exit-load reply and track fee-related tickets weekly."""
    pulse = build(q)
    while words(pulse) > WORD_LIMIT and len(q) > 1:
        q = q[:-1]; pulse = build(q)
    return pulse

def fee_explainer(a):
    fee = a["fee"]["name"]
    if fee != "Exit load":
        return {"fee": fee, "bullets": [f"No verified explainer is configured for '{fee}'. Add official sources in sources.py."], "links": [], "last_checked": TODAY.isoformat()}
    bullets = [
        "Exit load is a fee some mutual fund schemes charge when units are redeemed or switched out within a stated holding period.",
        "It is a percentage of the redemption value and is deducted at redemption, so the amount credited is lower than the gross value shown.",
        "Many equity schemes charge about 1% if units are redeemed within one year; after the period it is usually nil. Rates and periods differ by scheme.",
        "Each scheme's exit load is set by the fund house (AMC) and disclosed in its offer documents (SID/KIM) and scheme page. Check it before you redeem.",
        "Since 1 August 2009 SEBI has barred entry loads on mutual fund schemes, so exit load is the only load that can apply.",
        "Exit load is different from the expense ratio, which is the ongoing fee for managing the fund.",
    ]
    return {"fee": fee, "bullets": bullets, "links": [{"title": t, "url": u} for t, u in EXPLAINER_LINKS], "last_checked": TODAY.isoformat()}

def explainer_text(e):
    b = "\n".join(f"- {x}" for x in e["bullets"])
    l = "\n".join(f"- {x['title']}: {x['url']}" for x in e["links"])
    return f"**{e['fee']} - what it is**\n{b}\n\nSources:\n{l}\n\nLast checked: {e['last_checked']}"

def notes_entry(a, pulse, e):
    return {"date": TODAY.isoformat(), "top_themes": a["top3"]["theme"].tolist(), "weekly_pulse": pulse,
            "identified_fee_issue": f"{e['fee']} confusion - {a['fee']['pct']}% of reviews",
            "explanation_bullets": e["bullets"], "source_links": [x["url"] for x in e["links"]]}

def email(a, pulse, e):
    subject = f"Weekly Product Pulse + Customer Clarification - {TODAY.isoformat()}"
    body = f"Hi team,\n\n{pulse}\n\n---\nSupport snippet (reusable):\n\n{explainer_text(e)}\n\nRegards,\nProduct Insights Workflow\n"
    return subject, body
