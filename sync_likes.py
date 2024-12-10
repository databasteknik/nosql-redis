import psycopg2
import redis

# Redis client setup
cache = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# PostgreSQL connection setup
conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="123"
)
cur = conn.cursor()

def sync_likes():
    # Fetch all like counts from PostgreSQL
    cur.execute("""
        SELECT post_id, COUNT(user_id) AS like_count
        FROM likes
        GROUP BY post_id
    """)
    postgres_likes = cur.fetchall()

    updated_posts = []
    for post_id, like_count in postgres_likes:
        # Get current Redis count
        redis_key = f"post:{post_id}:likes"
        redis_like_count = int(cache.get(redis_key) or 0)

        # Update Redis if values differ
        if redis_like_count != like_count:
            cache.set(redis_key, like_count)
            updated_posts.append((post_id, like_count))

    if updated_posts:
        print(f"Updated posts in Redis: {updated_posts}")
    else:
        print("Redis cache is already synchronized.")

if __name__ == "__main__":
    sync_likes()
