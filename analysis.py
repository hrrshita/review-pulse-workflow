"""Step 1 - Review Intelligence: cluster (<=5 themes), top 3, 3 quotes, 1 fee confusion."""
import re, os, datetime as dt
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_distances

THEME_LEX = {
    "Pricing & fee confusion": "exit load charge charges fee brokerage deducted deduction hidden dp charges cut less money",
    "App performance & crashes": "crash crashes slow lag laggy freeze hang loading server bug update market open force closes",
    "KYC, onboarding & withdrawals": "kyc verification pending withdrawal bank payout delayed aadhaar ekyc onboarding settlement",
    "Customer support": "support ticket response complaint agent call chat helpdesk resolution",
    "Ease of use & SIP experience": "easy simple smooth interface design beginners sip clean great love recommend",
}
FEES = {  # fee name -> trigger phrases
    "Exit load": [r"exit\s*load"],
    "Brokerage / DP charges": [r"brokerage", r"\bdp\s*charges?"],
    "Hidden / unexplained charges": [r"hidden charge", r"extra charge", r"unexpected charge"],
}
CONFUSION = r"why|not clear|unclear|confus|did not know|didn't know|nobody told|no one told|hidden|unexpected|misleading|missing|surprise|warn"

def scrub(t):
    t = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "[email]", t)
    t = re.sub(r"(?<!\d)(?:\+?91[\s-]?)?[6-9]\d{9}(?!\d)", "[phone]", t)
    t = re.sub(r"\b[A-Z]{5}\d{4}[A-Z]\b", "[pan]", t)
    return t.strip()

def load(weeks=12):
    path = "data/reviews.csv" if os.path.exists("data/reviews.csv") else "data/reviews_sample.csv"
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["date"] >= df["date"].max() - pd.Timedelta(weeks=weeks)].copy()
    df["review"] = df["review"].astype(str).map(scrub)
    return df.reset_index(drop=True), path

def label(top_terms):
    scores = {k: len(set(v.split()) & set(top_terms)) for k, v in THEME_LEX.items()}
    return max(scores, key=scores.get)

def analyze(k=5):
    df, path = load()
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=2)
    X = vec.fit_transform(df["review"])
    # guided clustering: KMeans seeded with one centroid per candidate theme (max 5 themes)
    names = list(THEME_LEX)
    seeds = vec.transform([THEME_LEX[n] for n in names]).toarray()
    km = KMeans(n_clusters=len(names), init=seeds, n_init=1, random_state=42).fit(X)
    df["cluster"] = km.labels_
    cl_label = dict(enumerate(names))
    df["theme"] = df["cluster"].map(cl_label)
    themes = (df.groupby("theme").agg(count=("review", "size"), avg_rating=("rating", "mean"))
                .sort_values("count", ascending=False).reset_index())
    themes["share_pct"] = (100 * themes["count"] / len(df)).round(0).astype(int)
    themes["avg_rating"] = themes["avg_rating"].round(1)
    # top 3 problem-focused themes (exclude pure-positive theme when picking "issues")
    top3 = themes.head(3)
    # quotes: closest-to-centroid review per top theme, prefer low rating, 60-220 chars
    quotes = []
    for th in top3["theme"]:
        sub = df[df["theme"] == th]
        idxs = sub.index.to_list()
        dist = cosine_distances(X[idxs], km.cluster_centers_[sub["cluster"].iloc[0]].reshape(1, -1)).ravel()
        sub = sub.assign(dist=dist)
        sub = sub[sub["review"].str.len().between(60, 220)]
        sub = sub.sort_values(["dist"])
        quotes.append({"theme": th, "quote": sub.iloc[0]["review"], "rating": int(sub.iloc[0]["rating"])})
    # fee confusion: count reviews that mention a fee AND show confusion language
    fee_rows = []
    for fee, pats in FEES.items():
        m = df["review"].str.contains("|".join(pats), case=False, regex=True)
        conf = m & df["review"].str.contains(CONFUSION, case=False, regex=True)
        fee_rows.append({"fee": fee, "mentions": int(m.sum()), "confused": int(conf.sum())})
    fees = pd.DataFrame(fee_rows).sort_values(["confused", "mentions"], ascending=False).reset_index(drop=True)
    top_fee = fees.iloc[0]
    fq = df[df["review"].str.contains("|".join(FEES[top_fee["fee"]]), case=False, regex=True)
            & df["review"].str.contains(CONFUSION, case=False, regex=True)]
    fee_quote = fq.sort_values("review", key=lambda s: s.str.len()).iloc[len(fq) // 2]["review"] if len(fq) else ""
    return {"source": path, "n": len(df), "synthetic": bool(df["synthetic"].any()) if "synthetic" in df else False,
            "date_range": (df["date"].min().date().isoformat(), df["date"].max().date().isoformat()),
            "themes": themes, "top3": top3, "quotes": quotes, "fees": fees,
            "fee": {"name": top_fee["fee"], "mentions": int(top_fee["mentions"]), "confused": int(top_fee["confused"]),
                    "pct": round(100 * top_fee["confused"] / len(df)), "quote": fee_quote}}

if __name__ == "__main__":
    r = analyze()
    print(r["themes"], "\n", r["quotes"], "\n", r["fee"])
