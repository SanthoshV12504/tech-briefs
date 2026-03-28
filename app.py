from flask import Flask, send_file
from datetime import datetime
import os
from rss_fetcher import get_tech_articles
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

def get_pdf_filename():
    return f"tech_news_{datetime.now().strftime('%Y-%m-%d')}.pdf"


def generate_pdf(articles, filename):
    doc = SimpleDocTemplate(filename, pagesize=LETTER)
    styles = getSampleStyleSheet()
    story = []

    date_str = datetime.now().strftime("%Y-%m-%d")
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

    # Skip generation if today's PDF already exists
    if os.path.exists(filename):
        print("✅ Today's PDF already exists.")
        return

    print(f"📄 Generating PDF: {filename}")
    articles = get_tech_articles()
    generate_pdf(articles, filename)


@app.route("/")
def index():
    check_and_refresh_news()

    today = datetime.now().strftime("%Y-%m-%d")

    all_files = sorted(
        [f for f in os.listdir(".") if f.startswith("tech_news_") and f.endswith(".pdf")],
        reverse=True
    )

    past_files = [f for f in all_files if not f.endswith(f"{today}.pdf")][:7]

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

    return f"""
    <html>
    <head>
        <title>TechBriefs – Daily Tech News</title>
    </head>

    <body style="font-family:Poppins;background:#0f0f0f;color:white;text-align:center">

        <h1>📰 TechBriefs</h1>

        <h2>📅 Tech News for {datetime.strptime(today, "%Y-%m-%d").strftime("%B %d, %Y")}</h2>

        <p>Your daily digest of trending technology news.</p>

        <a href="/download">Download Today's PDF</a>

        <h2>📚 Past 7 Days</h2>

        {past_entries}

        <footer style="margin-top:50px">
        <p>Made with Flask by <b>Santhosh</b></p>
        </footer>

    </body>
    </html>
    """


@app.route("/download")
def download():
    return send_file(get_pdf_filename(), as_attachment=True)


@app.route("/download/<filename>")
def download_file(filename):
    return send_file(filename, as_attachment=True)


# Render requires this
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)