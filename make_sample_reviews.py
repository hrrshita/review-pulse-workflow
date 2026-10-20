"""Generates data/reviews_sample.csv: 120 SYNTHETIC Groww-style reviews (10 weeks) for offline demo/testing.
They imitate common themes but are NOT real user reviews. Use fetch_reviews.py for real ones."""
import random, datetime as dt, pandas as pd
random.seed(7)
END = dt.date(2026, 10, 18)
T = {
 "fee": ([
  "Redeemed my mutual fund after 5 months and got less money. Exit load was deducted and nobody told me before I clicked redeem.",
  "Why is there an exit load of 1% when I sold my units? It was not clearly shown on the redeem screen, felt like a hidden charge.",
  "I did not know about exit load. Withdrew my SIP units early and the amount credited was lower than what the app showed. Please show the charge upfront.",
  "Unexpected exit load deducted on redemption. The app should warn me before I sell, this is confusing for new investors.",
  "Confused about charges. Brokerage, DP charges and exit load all appear differently and I could not tell which one was applied to my sell order.",
  "Exit load explanation is missing in the app. I thought direct plans have no charges at all, then 1% got cut when I redeemed.",
  "Hidden charges everywhere. I only saw the exit load after the redemption went through. Very misleading for first time mutual fund users.",
  "Got charged exit load on my last SIP installment redemption, support says check scheme document. Why not show it in the app itself?",
 ], [1, 2, 2, 1, 2, 2, 1, 2], 36),
 "perf": ([
  "App keeps crashing at market open 9:15. Cannot place orders when it matters most, very frustrating.",
  "Very slow and laggy during market hours. Charts take forever to load and the app freezes often.",
  "After the latest update the app hangs on the portfolio screen. Please fix the bugs, it crashes every time I open it.",
  "Order page not loading, app stuck on loading screen again today. Server seems down every time the market is volatile.",
  "Login takes too long and the app force closes on my phone. Performance has become really bad this month.",
 ], [1, 2, 1, 1, 2], 26),
 "kyc": ([
  "My KYC verification is pending for over a week. Documents were uploaded correctly but status never changes.",
  "Withdrawal to my bank account is delayed by 3 days. Money stuck and no clear update on when it will arrive.",
  "Bank account verification failed again and again. Onboarding is painful, I could not even start investing.",
  "Payout of my redeemed amount did not reach the bank yet, the settlement timeline is not clear anywhere.",
  "Aadhaar eKYC keeps failing with an error. Account opening process is too long and confusing.",
 ], [2, 1, 2, 2, 1], 22),
 "support": ([
  "Customer support is not responding. Raised a ticket ten days ago and only got an automated reply.",
  "Support team gives copy paste answers and does not solve the issue. Chat support takes forever to connect.",
  "No one called back after my complaint. Terrible support experience, ticket closed without resolution.",
  "Support agent could not explain my deduction and just kept closing the ticket. Need real human help.",
 ], [1, 1, 2, 1], 16),
 "good": ([
  "Very easy to start a SIP, clean interface and quick investing. Love the simple design.",
  "Simple and smooth app for mutual funds. Setting up SIP took two minutes, great experience overall.",
  "Best app for beginners, the UI is neat and goals tracking is useful. Highly recommend.",
  "Good app, easy to track my portfolio and invest in stocks and mutual funds in one place.",
 ], [5, 5, 5, 4], 14),
}
rows = []
for key, (texts, ratings, n) in T.items():
    for i in range(n):
        j = random.randrange(len(texts))
        d = END - dt.timedelta(days=random.randint(0, 70))
        rows.append({"date": d.isoformat(), "rating": ratings[j], "review": texts[j], "synthetic": True})
random.shuffle(rows)
pd.DataFrame(rows).sort_values("date").to_csv("data/reviews_sample.csv", index=False)
print(len(rows), "synthetic reviews written")
