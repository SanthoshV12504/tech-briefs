from flask import Flask, send_file
from datetime import datetime, timedelta
import os
from rss_fetcher import get_tech_articles
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
DATE_FILE = "last_updated.txt"

# ✅ Generate PDF filename using yesterday’s date
def get_pdf_filename():
    yesterday = datetime.now() - timedelta(days=1)
    return f"tech_news_{yesterday.strftime('%Y-%m-%d')}.pdf"

def generate_pdf(articles, filename):
    doc = SimpleDocTemplate(filename, pagesize=LETTER)
    styles = getSampleStyleSheet()
    story = []

    date_str = filename.replace("tech_news_", "").replace(".pdf", "")
    story.append(Paragraph(f"<b>Daily Tech News - {date_str}</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    for idx, article in enumerate(articles, start=1):
        title = article.get("title", "No Title")
        summary = article.get("content") or article.get("summary") or "No summary available."
        link = article.get("link", "#")

        story.append(Paragraph(f"<b>{idx}. {title}</b>", styles["Heading3"]))
        story.append(Paragraph(f"• {summary}", styles["BodyText"]))
        story.append(Paragraph(f'<a href="{link}">Read full article</a>', styles["BodyText"]))
        story.append(Spacer(1, 12))

    doc.build(story)

def check_and_refresh_news():
    filename = get_pdf_filename()
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')

    if not os.path.exists(DATE_FILE) or open(DATE_FILE).read() != date_str or not os.path.exists(filename):
        print(f"📄 Generating PDF for {date_str}")
        articles = get_tech_articles()
        generate_pdf(articles, filename)
        with open(DATE_FILE, "w") as f:
            f.write(date_str)
    else:
        print("✅ PDF already up to date.")

@app.route("/")
def index():
    check_and_refresh_news()
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y-%m-%d')

    all_files = sorted([f for f in os.listdir(".") if f.startswith("tech_news_") and f.endswith(".pdf")], reverse=True)
    past_files = [f for f in all_files if not f.endswith(f"{yesterday_str}.pdf")][:7]

    def format_date(file):
        date_str = file.replace("tech_news_", "").replace(".pdf", "")
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %d, %Y")

    past_entries = ""
    for file in past_files:
        label = format_date(file)
        past_entries += f"""
            <div class="past-item">
                📄 {label}
                <a href="/download/{file}" class="past-btn">Download</a>
            </div>
        """

    current_year = datetime.now().year
    display_date = yesterday.strftime("%B %d, %Y")

    return f"""
    <html>
        <head>
            <title>TechBriefs – Daily Tech News</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: 'Poppins', sans-serif;
                    background: #0f0f0f;
                    color: white;
                    scroll-behavior: smooth;
                }}
                header {{
                    position: sticky;
                    top: 0;
                    background: rgba(0, 0, 0, 0.7);
                    padding: 15px 25px;
                    font-size: 22px;
                    font-weight: 600;
                    z-index: 100;
                    text-align: left;
                    color: #1abc9c;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.4);
                }}
                .section {{
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    padding: 60px 20px;
                    background: url('https://images.unsplash.com/photo-1548092372-0d1bd40894a3?q=80&w=870&auto=format&fit=crop') no-repeat center center fixed;
                    background-size: cover;
                }}
                .glass {{
                    background: rgba(0, 0, 0, 0.6);
                    backdrop-filter: blur(8px);
                    border-radius: 20px;
                    padding: 40px;
                    max-width: 600px;
                    width: 90%;
                    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);
                    text-align: center;
                    margin-bottom: 60px;
                    animation: fadeIn 1s ease-out;
                }}
                .past-item {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin: 15px 0;
                    background-color: rgba(255,255,255,0.05);
                    padding: 10px 15px;
                    border-radius: 10px;
                }}
                h1, h2 {{
                    margin: 0 0 15px;
                }}
                .btn, .past-btn {{
                    background: #1abc9c;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 30px;
                    text-decoration: none;
                    font-weight: 600;
                    transition: 0.3s;
                }}
                .btn:hover, .past-btn:hover {{
                    background: #16a085;
                }}
                .section-divider {{
                    border: none;
                    height: 1px;
                    width: 80%;
                    margin: 0 auto 40px;
                    background: linear-gradient(to right, transparent, #666, transparent);
                    opacity: 0.4;
                }}
                .footer {{
                    background: rgba(0, 0, 0, 0.6);
                    backdrop-filter: blur(6px);
                    border-top: 1px solid #333;
                    padding: 30px 20px;
                    color: #aaa;
                    text-align: center;
                }}
                .footer-inner {{
                    max-width: 900px;
                    margin: auto;
                }}
                .footer-tagline {{
                    margin-bottom: 10px;
                    font-size: 14px;
                    color: #ccc;
                }}
                .footer-links {{
                    display: flex;
                    justify-content: center;
                    flex-wrap: wrap;
                    gap: 20px;
                    margin-bottom: 10px;
                }}
                .footer-links a {{
                    color: #1abc9c;
                    text-decoration: none;
                    font-weight: 500;
                    transition: color 0.3s;
                    font-size: 14px;
                }}
                .footer-links a:hover {{
                    color: #ffffff;
                    text-decoration: underline;
                }}
                .footer-copy {{
                    font-size: 12px;
                    color: #777;
                }}
                @keyframes fadeIn {{
                    from {{ opacity: 0; transform: translateY(20px); }}
                    to {{ opacity: 1; transform: translateY(0); }}
                }}
            </style>
        </head>
        <body>
            <header>📰 TechBriefs</header>

            <section class="section">
                <div class="glass">
                    <h2>📅 Tech News for {display_date}</h2>
                    <p>Your daily digest of trending technology news.</p>
                    <a href="/download" class="btn">Download PDF</a>
                </div>

                <div class="glass">
                    <h2>📚 Past 7 Days</h2>
                    {past_entries}
                </div>
            </section>

            <div class="footer">
                <div class="footer-inner">
                    <p class="footer-tagline">Made with ❤️ by <strong>Santhosh</strong> — Tech Enthusiast & Python Developer</p>
                    <div class="footer-links">
                        <a href="mailto:santhoshv12504@gmail.com">📧 Email</a>
                        <a href="https://www.linkedin.com/in/santhoshv12504/" target="_blank">🔗 LinkedIn</a>
                        <a href="tel:+916382866340">📞 Call</a>
                    </div>
                    <p class="footer-copy">© {current_year} Santhosh. All rights reserved.</p>
                </div>
            </div>
        </body>
    </html>
    """

@app.route("/download")
def download():
    return send_file(get_pdf_filename(), as_attachment=True)

@app.route("/download/<filename>")
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
