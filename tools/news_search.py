from newsapi import NewsApiClient
from datetime import datetime, timedelta

# Initialize NewsAPI
newsapi = NewsApiClient(api_key='7b09b291f62145209456b5d0e313374f')

def fetch_recent_news(query: str, page_size: int = 5):
    """
    Fetch recent news articles for a query from the last 7 days.
    Returns a list of dicts: [{'title': ..., 'description': ..., 'url': ..., 'source': ...}, ...]
    """
    to_date = datetime.utcnow()
    from_date = to_date - timedelta(days=7)

    # Format dates as YYYY-MM-DD
    from_str = from_date.strftime("%Y-%m-%d")
    to_str = to_date.strftime("%Y-%m-%d")

    try:
        response = newsapi.get_everything(
            q=query,
            language='en',
            from_param=from_str,
            to=to_str,
            sort_by='relevancy',
            page_size=page_size
        )
    except Exception as e:
        print("Error fetching news:", e)
        return []

    articles = []
    for item in response.get('articles', []):
        articles.append({
            "title": item.get('title'),
            "description": item.get('description'),
            "url": item.get('url'),
            "source": item.get('source', {}).get('name')
        })

    return articles

# Example usage
if __name__ == "__main__":
    query = "AI OR 'Artificial Intelligence'"
    news = fetch_recent_news(query)
    for i, article in enumerate(news, start=1):
        print(f"{i}. {article['title']} - {article['source']}")
        print("Description:", article['description'])
        print("URL:", article['url'])
        print()
