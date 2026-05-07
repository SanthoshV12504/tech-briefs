from flask import Flask, send_file, request
from datetime import datetime, timedelta
import os
from rss_fetcher import get_tech_articles
from email_service import send_email_with_pdf
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
import os
import requests
import re
import html

app = Flask(__name__)

DATE_FILE = "last_updated.txt"


def get_pdf_filename():
    return f"tech_news_{datetime.now().strftime('%Y-%m-%d')}.pdf"


def generate_pdf(articles, filename):
    doc = SimpleDocTemplate(filename, pagesize=LETTER)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'PremiumTitle', 
        parent=styles['Title'], 
        fontSize=26, 
        textColor=colors.HexColor("#1abc9c"), 
        alignment=TA_CENTER, 
        spaceAfter=30
    )
    
    heading_style = ParagraphStyle(
        'PremiumHeading', 
        parent=styles['Heading3'], 
        fontSize=14, 
        textColor=colors.HexColor("#2c3e50"), 
        alignment=TA_LEFT, 
        spaceBefore=15, 
        spaceAfter=5
    )
    
    link_style = ParagraphStyle(
        'PremiumLink', 
        parent=styles['BodyText'], 
        fontSize=10, 
        textColor=colors.HexColor("#16a085"), 
        alignment=TA_LEFT
    )

    story = []
    date_str = datetime.now().strftime("%B %d, %Y")

    story.append(Paragraph(f"<b>TechBriefs Daily</b>", title_style))
    story.append(Paragraph(f"<i>Critical insights for {date_str}</i>", styles["Normal"]))
    story.append(Spacer(1, 40))

    for idx, article in enumerate(articles, start=1):
        title = article.get("title", "No Title")
        summary = article.get("content") or article.get("summary") or "No summary available."
        link = article.get("link", "#")

        story.append(Paragraph(f"<b>{idx}. {title}</b>", heading_style))
        story.append(Paragraph(f"{summary}", styles["BodyText"]))
        story.append(Paragraph(f'<a href="{link}" color="#16a085">Read Full Article &rarr;</a>', link_style))
        story.append(Spacer(1, 10))
        
        story.append(Paragraph("<hr color='#eeeeee'/>", styles["Normal"]))

    doc.build(story)


def check_and_refresh_news():
    today = datetime.now().strftime("%Y-%m-%d")
    filename = get_pdf_filename()

    if not os.path.exists(DATE_FILE) or open(DATE_FILE).read() != today or not os.path.exists(filename):

        print(f"📄 Generating PDF: {filename}")

        articles = get_tech_articles()

        if len(articles) > 0:
            generate_pdf(articles, filename)

            with open(DATE_FILE, "w") as f:
                f.write(today)
        else:
            print("⚠ No articles fetched")

            articles = [{
                "title": "No articles found today",
                "summary": "We couldn't find any relevant tech news articles today. Please check back tomorrow for the latest updates.",
                "link": "https://techcrunch.com",
                "content": "RSS feeds returned limited results for today."
            }]
            generate_pdf(articles, filename)
            with open(DATE_FILE, "w") as f:
                f.write(today)

    else:
        print("✅ PDF already up to date.")


check_and_refresh_news()


@app.route("/")
def index():
    today_dt = datetime.now()
    previews = []
    try:
        articles = get_tech_articles()
        previews = articles[:3]
    except Exception as e:
        print(f"Error fetching articles for preview: {e}")
    
    all_files = sorted([f for f in os.listdir(".") if f.startswith("tech_news_") and f.endswith(".pdf")], reverse=True)

    past_files = []
    for f in all_files:
        try:
            date_str = f.replace("tech_news_", "").replace(".pdf", "")
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            delta = (today_dt.date() - file_date.date()).days
            if 1 <= delta <= 7:
                past_files.append(f)
        except Exception:
            continue

    past_files = past_files[:7]

    preview_html = ""
    for art in previews:
        clean_summary = re.sub('<[^<]+?>', '', art['summary'])
        clean_summary = (clean_summary[:150] + '...') if len(clean_summary) > 150 else clean_summary
        
        safe_link = html.escape(art['link'])
        safe_title = html.escape(art['title'])

        preview_html += f"""
            <div class="preview-card">
                <h3>{safe_title}</h3>
                <p>{clean_summary}</p>
                <a href="{safe_link}" target="_blank">Full Story →</a>
            </div>
        """

    past_entries = ""
    for file in past_files:
        date_label = datetime.strptime(file.replace("tech_news_", "").replace(".pdf", ""), "%Y-%m-%d").strftime("%B %d, %Y")
        past_entries += f"""
            <div class="past-item">
                <span>📄 {date_label}</span>
                <a href="/download/{file}" class="past-btn">Download</a>
            </div>
        """

    current_year = datetime.now().year

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>TechBriefs – Premium Daily News</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --accent: #1abc9c;
                --accent-dark: #16a085;
                --bg: #050505;
                --glass: rgba(255, 255, 255, 0.05);
                --glass-border: rgba(255, 255, 255, 0.1);
            }}

            body {{
                margin: 0;
                font-family: 'Outfit', sans-serif;
                background: linear-gradient(135deg, #050505 0%, #0a1a1a 100%);
                color: #e0e0e0;
                min-height: 100vh;
                overflow-x: hidden;
            }}

            header {{
                padding: 20px 50px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: rgba(0,0,0,0.3);
                backdrop-filter: blur(10px);
                position: fixed;
                width: 100%;
                box-sizing: border-box;
                z-index: 1000;
                border-bottom: 1px solid var(--glass-border);
                transition: padding 0.3s ease;
            }}

            .logo {{
                font-size: 24px;
                font-weight: 700;
                color: var(--accent);
                display: flex;
                align-items: center;
                gap: 10px;
            }}

            .container {{
                max-width: 1000px;
                margin: 0 auto;
                padding: 120px 20px 60px;
            }}

            .hero {{
                text-align: center;
                margin-bottom: 60px;
                animation: fadeInUp 0.8s ease-out;
            }}

            .hero h1 {{
                font-size: 52px;
                margin: 0;
                background: linear-gradient(to right, #fff, var(--accent));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}

            .hero p {{
                font-size: 18px;
                color: #aaa;
                margin-top: 10px;
            }}

            .main-actions {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                margin-bottom: 60px;
            }}

            .glass-card {{
                background: var(--glass);
                backdrop-filter: blur(12px);
                border: 1px solid var(--glass-border);
                border-radius: 24px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.4);
                transition: transform 0.3s ease;
            }}

            .glass-card:hover {{
                transform: translateY(-5px);
            }}

            h2 {{
                font-size: 24px;
                margin-top: 0;
                color: var(--accent);
                display: flex;
                align-items: center;
                gap: 10px;
            }}

            .btn {{
                display: inline-block;
                background: var(--accent);
                color: white;
                padding: 15px 30px;
                border-radius: 50px;
                text-decoration: none;
                font-weight: 600;
                font-size: 16px;
                transition: all 0.3s ease;
                border: none;
                cursor: pointer;
                box-shadow: 0 10px 20px rgba(26, 188, 156, 0.3);
            }}

            .btn:hover {{
                background: var(--accent-dark);
                transform: scale(1.05);
                box-shadow: 0 15px 30px rgba(26, 188, 156, 0.4);
            }}

            .email-form {{
                margin-top: 20px;
                display: flex;
                gap: 10px;
            }}

            .email-form input {{
                flex: 1;
                background: rgba(255,255,255,0.1);
                border: 1px solid var(--glass-border);
                border-radius: 50px;
                padding: 0 20px;
                color: white;
                outline: none;
            }}

            .preview-section {{
                margin-top: 40px;
            }}

            .preview-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }}

            .preview-card {{
                background: rgba(255,255,255,0.03);
                border: 1px solid var(--glass-border);
                border-radius: 16px;
                padding: 20px;
                transition: 0.3s;
            }}

            .preview-card h3 {{
                font-size: 18px;
                margin: 0 0 10px;
                line-height: 1.4;
            }}

            .preview-card p {{
                font-size: 14px;
                color: #888;
                margin-bottom: 15px;
            }}

            .preview-card a {{
                color: var(--accent);
                text-decoration: none;
                font-weight: 600;
                font-size: 14px;
            }}

            .past-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 0;
                border-bottom: 1px solid var(--glass-border);
            }}

            .past-item:last-child {{ border: none; }}

            .past-btn {{
                color: var(--accent);
                text-decoration: none;
                font-weight: 600;
                font-size: 14px;
            }}

            @keyframes fadeInUp {{
                from {{ opacity: 0; transform: translateY(30px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}

            @media (max-width: 768px) {{
                header {{ padding: 15px 20px; }}
                .container {{ padding-top: 100px; }}
                .main-actions {{ grid-template-columns: 1fr; gap: 20px; }}
                .hero h1 {{ font-size: 32px; }}
                .hero p {{ font-size: 16px; }}
                .glass-card {{ padding: 24px; }}
                .email-form {{ flex-direction: column; }}
                .email-form input, .email-form .btn {{ width: 100%; box-sizing: border-box; }}
                .email-form input {{ padding: 12px 20px; margin-bottom: 10px; min-height: 45px; }}
                .preview-grid {{ grid-template-columns: 1fr; }}
            }}
        </style>
    </head>
    <body>
        <header>
            <div class="logo">⚡ TechBriefs</div>
            <div class="user-action">
                <a href="#past" style="color: #666; text-decoration: none; font-size: 14px;">Archive</a>
            </div>
        </header>

        <div class="container">
            <div class="hero">
                <h1>Ready for your briefing?</h1>
                <p>The core of today's tech evolution, curated just for you.</p>
            </div>

            <div class="main-actions">
                <div class="glass-card">
                    <h2>📰 {today_dt.strftime("%B %d, %Y")}</h2>
                    <p>Your comprehensive daily PDF is ready for download.</p>
                    <div style="margin-top: 30px;">
                        <a href="/download" class="btn">Download Today’s Briefing</a>
                    </div>
                </div>

                <div class="glass-card">
                    <h2>📧 Email Delivery</h2>
                    <p>Send today's briefing directly to your inbox.</p>
                    <form action="/email" method="POST" class="email-form">
                        <input type="email" name="email" placeholder="enter your email..." required>
                        <button type="submit" class="btn">Send</button>
                    </form>
                    <p id="email-msg" style="font-size: 12px; margin-top: 10px; color: var(--accent);"></p>
                </div>
            </div>

            <div class="preview-section">
                <h2>🗞️ Today's Highlights</h2>
                <div class="preview-grid">
                    {preview_html}
                </div>
            </div>

            <div id="past" class="preview-section" style="margin-top: 80px; margin-bottom: 60px;">
                <h2>📚 Archives</h2>
                <div class="glass-card" style="padding: 20px 40px;">
                    {past_entries if past_entries else '<p style="color:#666">No recent archives found.</p>'}
                </div>
            </div>
        </div>

        <footer style="text-align: center; padding: 40px; color: #444; font-size: 13px; border-top: 1px solid var(--glass-border);">
            &copy; {current_year} TechBriefs. Developed by Santhosh.
        </footer>
    </body>
    </html>
    """

@app.route("/email", methods=["POST"])
def email_briefing():
    recipient = request.form.get("email")
    if not recipient:
        return "Email required", 400
    
    filename = get_pdf_filename()
    if not os.path.exists(filename):
        check_and_refresh_news()
    
    success, message = send_email_with_pdf(recipient, filename)
    if success:
        return f"<script>alert('Briefing sent successfully!'); window.location.href='/';</script>"
    else:
        err_msg = message
        if "Authentication failed" in message or "Bad credentials" in message or "535" in message:
            err_msg = "Authentication failed. Please check your SMTP settings in email_service.py (you might need a Gmail App Password)."
            
        return f"<script>alert('Email Error: {err_msg}'); window.location.href='/';</script>"


@app.route("/download")
def download():
    filename = get_pdf_filename()
    if not os.path.exists(filename):
        check_and_refresh_news()
    if not os.path.exists(filename):
        return """
        <h1>No PDF Generated</h1>
        <p>No articles were available today.</p>
        """, 500 
    return send_file(get_pdf_filename(), as_attachment=True)


@app.route("/download/<filename>")
def download_file(filename):
    return send_file(filename, as_attachment=True)



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)