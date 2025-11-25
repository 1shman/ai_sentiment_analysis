import praw
import os
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone


def load_reddit_client():
    load_dotenv()
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
    )

def get_comments(submission, limit=10):
    """Retrieve top comments for a submission."""
    submission.comment_sort = "top"
    submission.comments.replace_more(limit=0)

    comments = []
    count = 0

    # error checking
    for comment in submission.comments:
        if count >= limit:
            break
        if not hasattr(comment, "body"):
            continue

        comments.append({
            "author": str(comment.author),
            "body": comment.body,
            "score": comment.score,
            "created_utc": comment.created_utc,
            "created_date": datetime.fromtimestamp(
                comment.created_utc, tz=timezone.utc
            ).strftime("%Y-%m-%d"),
        })
        count += 1

    return comments

def get_posts(reddit, subreddit_name, fetch_limit=2000, top_n=50):
    # identify subreddit
    subreddit = reddit.subreddit(subreddit_name)

    # identify start/end time
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=365 * 2)

    candidates = []

    # Grab a bunch of all-time top posts, then filter by timestamp
    for submission in subreddit.top(time_filter="all", limit=fetch_limit):
        created_dt = datetime.fromtimestamp(
            submission.created_utc, tz=timezone.utc
        )
        if created_dt >= cutoff:
            candidates.append(
                {
                    "id": submission.id,
                    "title": submission.title,
                    "score": submission.score,
                    "author": str(submission.author),
                    "created_utc": submission.created_utc,
                    "created_date": created_dt.strftime("%Y-%m-%d"),
                    "url": submission.url,
                    "selftext": submission.selftext,
                    "comments": [],  # fill later
                }
            )

    # Sort filtered candidates by score
    candidates.sort(key=lambda x: x["score"], reverse=True)

    # Only keep the top N
    top_posts = candidates[:top_n]

    # Fetch comments for each post (top 10)
    for post in top_posts:
        try:
            submission = reddit.submission(id=post["id"])
            post["comments"] = get_comments(submission, limit=10)
        except Exception as e:
            print(f"Error fetching comments for post {post['id']}: {e}")
            post["comments"] = []

    return top_posts, len(candidates)



def main():
    reddit = load_reddit_client()
    subreddit = "ArtificialInteligence"

    # keep this for error checking
    # for s in reddit.subreddit("ArtificialInteligence").top(limit=5):
    #     print(s.title)

    # identify search filters
    top_n = 50
    fetch_limit = 2000

    # select start/end time
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=365 * 2)

    print(
        f"Collecting ~{fetch_limit} all-time top posts from r/{subreddit}, "
        f"then filtering to last 2 years ({cutoff.date()} to {now.date()})..."
    )

    # retreive posts
    top_posts, total_candidates = get_posts(
        reddit, subreddit, fetch_limit=fetch_limit, top_n=top_n
    )

    # format output for json
    out = {
        "subreddit": subreddit,
        "start_date": cutoff.strftime("%Y-%m-%d"),
        "end_date": now.strftime("%Y-%m-%d"),
        "total_candidates_in_window": total_candidates,
        "top_posts": top_posts,
    }

    # print to json
    filename = f"{subreddit}_top{top_n}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=4, ensure_ascii=False)

    # notify completion
    print(f"\nSaved {filename}")
    print(
        f"Found {total_candidates} posts in the last 2 years from the all-time pool, "
        f"returning top {len(top_posts)} by score."
    )


if __name__ == "__main__":
    main()
