import feedparser
import json
import os

# ✅ Extended keyword list for wider tech news coverage
KEYWORDS = [
    "ai", "artificial intelligence", "machine learning", "deep learning",
    "openai", "chatgpt", "llm", "nvidia", "intel", "tesla",
    "google", "microsoft", "meta", "amazon", "apple",
    "startup", "cybersecurity", "robotics", "data science",
    "programming", "developer", "software", "coding",
    "python", "java", "javascript", "blockchain", "cloud"
]

MAX_ARTICLES = 25
SEEN_FILE = "seen_titles.json"

# ✅ RSS feeds
GOOGLE_NEWS_FEEDS = [
    "https://news.google.com/rss/search?q=ai&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=google+ai&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=microsoft+technology&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=programming&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=machine+learning&hl=en-IN&gl=IN&ceid=IN:en"
]

TECHCRUNCH_FEED = "https://techcrunch.com/feed/"

# ✅ Load previously used titles
def load_seen_titles():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

# ✅ Save updated seen titles
def save_seen_titles(titles):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(titles)), f, ensure_ascii=False, indent=2)

# ✅ Filter articles based on keywords and skip seen titles
def filter_articles(entries):
    articles = []
    seen_titles = load_seen_titles()
    updated_titles = set(seen_titles)

    for entry in entries:
        title = entry.title.strip()
        summary = entry.get("summary", "").strip()
        content_combined = (title + " " + summary).lower()

        if title in seen_titles:
            continue  # already used in a past PDF

        if any(keyword in content_combined for keyword in KEYWORDS):
            articles.append({
                "title": title,
                "summary": summary,
                "link": entry.link,
                "content": summary
            })
            updated_titles.add(title)

        if len(articles) >= MAX_ARTICLES:
            break

    save_seen_titles(updated_titles)
    return articles

# ✅ Fetch and filter tech articles
def get_tech_articles():
    all_entries = []

    for feed_url in GOOGLE_NEWS_FEEDS + [TECHCRUNCH_FEED]:
        parsed = feedparser.parse(feed_url)
        all_entries.extend(parsed.entries)

    return filter_articles(all_entries)
