import os
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
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
        print(f"Fetching: {url}")
        try:
            r = requests.get(url)
            data = r.json()
            for item in data.get("results", []):
                if item.get("item_type") == "Interactive":
                    continue
                title = item.get("title", "")
                abstract = item.get("abstract", "")
                link = item.get("url", "")
                if any(k.lower() in (title + abstract).lower() for k in KEYWORDS):
                    articles.append((title, abstract, link))
        except Exception as e:
            print(f"Error fetching {section}: {e}")
            continue
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
    
    # lead story is first one
    lead = articles[0]
    rest = articles[1:]
    
    html = f"""
    <html>
    <body style="font-family: Georgia, serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #333; border-bottom: 2px solid #000; padding-bottom: 10px;">NYT Daily Brief</h2>
        
        <div style="margin: 30px 0; padding: 20px; background: #f8f8f8; border-left: 4px solid #000;">
            <h1 style="font-size: 28px; margin: 0 0 15px 0; line-height: 1.3;">
                <a href="{lead[2]}" style="color: #000; text-decoration: none;">{lead[0]}</a>
            </h1>
            <p style="font-size: 16px; color: #666; line-height: 1.6; margin: 0;">{lead[1]}</p>
        </div>
        
        <div style="margin-top: 30px;">
    """
    
    for i, (title, abstract, url) in enumerate(rest, 2):
        html += f"""
        <div style="margin-bottom: 25px; padding-bottom: 20px; border-bottom: 1px solid #ddd;">
            <h3 style="font-size: 18px; margin: 0 0 8px 0;">
                <a href="{url}" style="color: #000; text-decoration: none;">{i}. {title}</a>
            </h3>
            <p style="font-size: 14px; color: #666; line-height: 1.5; margin: 0;">{abstract}</p>
        </div>
        """
    
    html += """
        </div>
    </body>
    </html>
    """
    
    msg = MIMEMultipart('alternative')
    msg["Subject"] = subject
    msg["From"] = YOUR_EMAIL
    msg["To"] = YOUR_EMAIL
    
    msg.attach(MIMEText(html, 'html'))
    
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