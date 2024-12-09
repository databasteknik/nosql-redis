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
    database="test_db",
    user="postgres",
    password="password"
)
cur = conn.cursor()


# Create a Post
@app.route('/posts', methods=['POST'])
def create_post():
    data = request.json
    title = data.get("title")
    if not title:
        return jsonify({"error": "Title is required"}), 400

    # Insert post into PostgreSQL
    cur.execute("INSERT INTO posts (title) VALUES (%s) RETURNING id", (title,))
    post_id = cur.fetchone()[0]
    conn.commit()

    return jsonify({"message": "Post created", "post_id": post_id}), 201


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


# Unlike a Post
@app.route('/posts/<int:post_id>/unlike', methods=['POST'])
def unlike_post(post_id):
    user_id = request.json.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    # Remove like from PostgreSQL
    cur.execute(
        "DELETE FROM likes WHERE post_id = %s AND user_id = %s RETURNING id",
        (post_id, user_id)
    )
    result = cur.fetchone()
    if not result:
        return jsonify({"error": "Like not found"}), 404

    conn.commit()

    # Decrement Redis like count
    cache.decr(f"post:{post_id}:likes", 1)

    return jsonify({"message": "Post unliked"}), 200


# Get Like Count
@app.route('/posts/<int:post_id>/likes', methods=['GET'])
def get_like_count(post_id):
    like_count = cache.get(f"post:{post_id}:likes") or 0
    return jsonify({"post_id": post_id, "likes": int(like_count)}), 200



if __name__ == "__main__":
    app.run(debug=True)
