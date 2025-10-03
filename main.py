import os
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

NYT_API_KEY = os.getenv("NYT_API_KEY")
YOUR_EMAIL = os.getenv("GMAIL_ADDRESS")
APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

KEYWORDS = [
    "Israel", "Middle East", "Gaza", "Hamas", "Iran",
    "White House", "Congress", "Trump",
    "economy", "Federal Reserve", "inflation", "market", "science", "culture", "tech", "artificial intelligence"
]
SECTIONS = ["world", "us", "business", "science", "tech", "artificial intelligence"]

def fetch_articles():
    articles = []
    for section in SECTIONS:
        url = f"https://api.nytimes.com/svc/topstories/v2/{section}.json?api-key={NYT_API_KEY}"
        r = requests.get(url).json()
        for item in r.get("results", []):
            title = item.get("title", "")
            abstract = item.get("abstract", "")
            link = item.get("url", "")
            if any(k.lower() in (title + abstract).lower() for k in KEYWORDS):
                articles.append((title, abstract, link))
    seen = set()
    unique = []
    for a in articles:
        if a[0] not in seen:
            unique.append(a)
            seen.add(a[0])
    return unique[:6]

def send_email(articles):
    today = datetime.now().strftime("%A, %B %d")
    subject = f"NYT Daily Brief — {today}"
    body = "Here are your top NYT stories:\n\n"
    for i, (title, abstract, url) in enumerate(articles, 1):
        body += f"{i}. {title}\n{abstract}\n{url}\n\n"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = YOUR_EMAIL
    msg["To"] = YOUR_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(YOUR_EMAIL, APP_PASSWORD)
        server.send_message(msg)

if __name__ == "__main__":
    articles = fetch_articles()
    print(f"Found {len(articles)} articles")
    if articles:
        send_email(articles)
    else:
        print("No matching articles found.")
