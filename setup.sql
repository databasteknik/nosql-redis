-- Create the 'posts' table
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,   -- Unique post ID
    user_id INTEGER NOT NULL,               -- User who created the post
    caption TEXT NOT NULL                   -- Post caption
);

-- Create the 'likes' table
CREATE TABLE likes (
    user_id INTEGER NOT NULL,               -- User who liked the post
    post_id INTEGER NOT NULL,               -- Post that was liked
    PRIMARY KEY (user_id, post_id),         -- Composite primary key
    FOREIGN KEY (post_id) REFERENCES posts (id) -- Foreign key constraint
);

-- Insert example data into 'posts'
INSERT INTO posts (user_id, caption) 
VALUES (1, 'First post by user 1');

INSERT INTO posts (user_id, caption) 
VALUES (2, 'A cool post by user 2');

INSERT INTO posts (user_id, caption) 
VALUES (1, 'Another post by user 1');

INSERT INTO posts (user_id, caption) 
VALUES (3, 'Hello world from user 3');

-- Insert example data into 'likes'
INSERT INTO likes (user_id, post_id) 
VALUES (2, 1);  -- User 2 likes Post 1

INSERT INTO likes (user_id, post_id) 
VALUES (3, 1);  -- User 3 likes Post 1

INSERT INTO likes (user_id, post_id) 
VALUES (1, 2);  -- User 1 likes Post 2

INSERT INTO likes (user_id, post_id) 
VALUES (3, 3);  -- User 3 likes Post 3
