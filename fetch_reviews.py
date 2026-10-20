"""OPTIONAL: pull REAL public Groww reviews from Google Play (run on your own machine).
Writes data/reviews.csv with the last 12 weeks of reviews. analysis.py prefers this file over the sample."""
import datetime as dt, pandas as pd
from google_play_scraper import reviews, Sort

APP_ID = "com.nextbillion.groww"
cutoff = dt.datetime.now() - dt.timedelta(weeks=12)
rows, token = [], None
while True:
    batch, token = reviews(APP_ID, lang="en", country="in", sort=Sort.NEWEST, count=200, continuation_token=token)
    for r in batch:
        if r["at"] < cutoff:
            token = None; break
        rows.append({"date": r["at"].date().isoformat(), "rating": r["score"], "review": r["content"], "synthetic": False})
    if not token or not batch:
        break
df = pd.DataFrame(rows)
df.to_csv("data/reviews.csv", index=False)
print(f"Saved {len(df)} real reviews -> data/reviews.csv")
