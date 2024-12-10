from flask import Flask, jsonify, request
import psycopg2
import redis

app = Flask(__name__)

# Redis client setup
cache = redis.Redis(
    host="localhost", port=6379, db=0, decode_responses=True
)

# PostgreSQL connection setup
conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="123"
)
cur = conn.cursor()

# Like a Post
@app.route('/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    user_id = request.json.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    # Check if the post exists
    cur.execute("SELECT id FROM posts WHERE id = %s", (post_id,))
    post = cur.fetchone()
    if not post:
        return jsonify({"error": "Post not found"}), 404

    # Add like in PostgreSQL (if not already liked)
    try:
        cur.execute(
            "INSERT INTO likes (post_id, user_id) VALUES (%s, %s)",
            (post_id, user_id)
        )
        conn.commit()
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return jsonify({"error": "Post already liked"}), 400

    # Update Redis like count
    cache.incr(f"post:{post_id}:likes")

    return jsonify({"message": "Post liked"}), 201

# Get Like Count
@app.route('/posts/<int:post_id>/likes', methods=['GET'])
def get_like_count(post_id):
    like_count = cache.get(f"post:{post_id}:likes") or 0
    return jsonify({"post_id": post_id, "likes": int(like_count)}), 200



if __name__ == "__main__":
    app.run(debug=True)
