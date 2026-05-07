import feedparser
import json
import os
import socket

socket.setdefaulttimeout(10)


KEYWORDS = [
    "ai", "artificial intelligence", "machine learning", "deep learning",
    "openai", "chatgpt", "llm", "nvidia", "intel", "tesla",
    "google", "microsoft", "meta", "amazon", "apple",
    "startup", "cybersecurity", "robotics", "data science",
    "programming", "developer", "software", "coding",
    "python", "java", "javascript", "blockchain", "cloud"
]

MAX_ARTICLES = 20
SEEN_FILE = "seen_titles.json"

GOOGLE_NEWS_FEEDS = [
    "https://news.google.com/rss/search?q=ai&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=machine+learning&hl=en-IN&gl=IN&ceid=IN:en"
]

TECHCRUNCH_FEED = "https://techcrunch.com/feed/"


def load_seen_titles():
    """
    Load already processed article titles
    to avoid duplicates.
    """

    if os.path.exists(SEEN_FILE):

        try:
            with open(SEEN_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))

        except Exception as e:
            print(f"Error reading {SEEN_FILE}: {e}")

    return set()



def save_seen_titles(titles):
    """
    Save processed article titles.
    """

    try:
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(
                sorted(list(titles)),
                f,
                ensure_ascii=False,
                indent=2
            )

    except Exception as e:
        print(f"Error saving seen titles: {e}")


def filter_articles(entries):

    articles = []

    seen_titles = load_seen_titles()

    updated_titles = set(seen_titles)

    for entry in entries:

        title = entry.get("title", "").strip()

        summary = entry.get("summary", "").strip()

        link = entry.get("link", "#")

        
        if not title:
            continue

        
        if title in seen_titles:
            continue

       
        content_combined = (title + " " + summary).lower()

        
        if True:

            article = {
                "title": title,
                "summary": summary,
                "link": link,
                "content": summary
            }

            articles.append(article)

            updated_titles.add(title)

        if len(articles) >= MAX_ARTICLES:
            break

    save_seen_titles(updated_titles)

    return articles



def get_tech_articles():

    all_entries = []

    feeds = GOOGLE_NEWS_FEEDS + [TECHCRUNCH_FEED]

    for feed_url in feeds:

        try:

            print(f"\nFetching feed:")
            print(feed_url)

            parsed = feedparser.parse(feed_url)

            
            if parsed.bozo:
                print(f"Warning: malformed feed -> {feed_url}")


            if hasattr(parsed, "entries"):

                print(f"Found {len(parsed.entries)} articles")

                all_entries.extend(parsed.entries[:15])

            else:
                print("No entries found")

        except Exception as e:

            print(f"Error fetching feed:")
            print(feed_url)
            print(f"Reason: {e}")

    print(f"\nTotal entries collected: {len(all_entries)}")

    filtered_articles = filter_articles(all_entries)

    print(f"Filtered tech articles: {len(filtered_articles)}")

    return filtered_articles



if __name__ == "__main__":

    articles = get_tech_articles()

    print("\n=========================")
    print("TECH ARTICLES")
    print("=========================\n")

    for i, article in enumerate(articles, start=1):

        print(f"{i}. {article['title']}")
        print(article['link'])
        print()