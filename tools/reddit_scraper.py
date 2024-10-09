import json
import os

from config.scraper_config import *
import praw # pip install praw

reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent
)

subreddit = reddit.subreddit(subreddit_name)

posts = subreddit.search(search_query, limit=search_limit)

posts_data = []
for post in posts:
    post_info = {
        "title": post.title,
        "score": post.score,
        "url": post.url,
        "num_comments": post.num_comments,
        "comments": []
    }

    # Extract the comments of the post
    post.comments.replace_more(limit=0)  # Replace "MoreComments" instances
    for comment in post.comments.list():
        comment_info = {
            "body": comment.body,
            "score": comment.score
        }
        post_info["comments"].append(comment_info)

    posts_data.append(post_info)

# Save the data to JSON file
os.makedirs("../data/raw", exist_ok=True)
file_path = "../data/raw/reddit_posts.json"
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(posts_data, f, ensure_ascii=False, indent=4)

print(f"Data saved to {file_path}")