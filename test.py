from scraper import get_tech_articles
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(articles):
    doc = SimpleDocTemplate("daily_tech_news.pdf", pagesize=LETTER)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Recent Tech News", styles["Title"]))
    story.append(Spacer(1, 12))

    for article in articles:
        story.append(Paragraph(f"<b>{article['title']}</b>", styles["Heading3"]))
        story.append(Paragraph(f"• {article['summary']}", styles["BodyText"]))
        story.append(Paragraph(f'<a href="{article["link"]}">Read full article</a>', styles["BodyText"]))
        story.append(Spacer(1, 12))

    doc.build(story)

articles = get_tech_articles()
generate_pdf(articles)
print("✅ PDF created!")
