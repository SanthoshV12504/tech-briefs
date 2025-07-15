# scraper.py

import requests
from datetime import datetime, timedelta

API_KEY = 'e2fcd5d82b674090a26fac7f6b580fd9'  # 🔁 Replace this with your real key

def get_tech_articles():
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')

    url = (
        f"https://newsapi.org/v2/everything?"
        f"q=technology&"
        f"from={date_str}&to={date_str}&"
        f"language=en&"
        f"sortBy=popularity&"
        f"pageSize=10&"
        f"apiKey={API_KEY}"
    )

    response = requests.get(url)
    data = response.json()

    articles = []
    for item in data.get("articles", []):
        articles.append({
            'title': item['title'],
            'summary': item.get('description', 'No description available.'),
            'link': item['url']
        })

    return articles
if __name__ == "__main__":
    articles = get_tech_articles()
    print("Fetched Articles:", len(articles))
    for article in articles:
        print(article['title'])



