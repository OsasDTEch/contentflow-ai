import os
import asyncio
import asyncpraw
from dotenv import load_dotenv

load_dotenv()

# Initialize Reddit client
reddit = asyncpraw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)


async def fetch_reddit_posts(subreddit_name: str, keyword: str = "", limit: int = 5):
    """
    Fetch posts from a subreddit optionally filtered by a keyword (async).

    Args:
        subreddit_name (str): Name of the subreddit (e.g., 'fintech')
        keyword (str): Optional keyword to search in titles
        limit (int): Number of posts to fetch

    Returns:
        list[dict]: List of posts with details and top comments
    """
    results = []
    subreddit = await reddit.subreddit(subreddit_name)

    # Search posts containing the keyword (or all hot posts if keyword is empty)
    if keyword:
        posts = subreddit.search(keyword, limit=limit)
    else:
        posts = subreddit.hot(limit=limit)

    async for post in posts:
        await post.load()  # Ensure all attributes are loaded
        await post.comments.replace_more(limit=0)  # Flatten all top-level comments

        top_comments = []
        i = 0
        async for comment in post.comments.list():
            if i >= 5:
                break
            top_comments.append(
                {
                    "author": str(comment.author),
                    "body": comment.body,
                    "score": comment.score,
                }
            )
            i += 1

        results.append(
            {
                "id": post.id,
                "title": post.title,
                "subreddit": str(post.subreddit),
                "url": post.url,
                "score": post.score,
                "num_comments": post.num_comments,
                "selftext": post.selftext,
                "created_utc": post.created_utc,
                "top_comments": top_comments,
            }
        )

    return results


# Example usage
if __name__ == "__main__":

    async def main():
        posts = await fetch_reddit_posts("fintech", keyword="startup", limit=5)
        for p in posts:
            print(p)

    asyncio.run(main())
