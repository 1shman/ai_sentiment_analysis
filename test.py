import praw
import os
from dotenv import load_dotenv

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

# Choose subreddit and time filter
subreddit = reddit.subreddit("ArtificialInteligence")


# Loop through the top 10 posts
for i, submission in enumerate(subreddit.top(limit=10, time_filter="week"), start=1):
    print(f"{i}. {submission.title}")
    print(f"   Author: {submission.author}")
    print(f"   Score: {submission.score}")
    print(f"   URL: {submission.url}")
    print(f"   Comments: {submission.num_comments}")
    print(f"   Text: {submission.selftext[:200]}...\n")

    # Load the top comments
    submission.comment_sort = "top"
    submission.comments.replace_more(limit=0)  # remove "load more" placeholders
    top_comments = submission.comments[:5]

    for j, comment in enumerate(top_comments, start=1):
        text = comment.body.replace("\n", " ")
        print(f"      Comment {j}: {text[:180]}...\n")

    print("-" * 80)
