
-- Activer l'extension Citus
CREATE EXTENSION IF NOT EXISTS citus;

DROP TABLE IF EXISTS follower_followee CASCADE;
DROP TABLE IF EXISTS post CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
   id BIGSERIAL PRIMARY KEY,
   username VARCHAR(255) UNIQUE NOT NULL,
   password VARCHAR(255) NOT NULL
);

CREATE TABLE post (
   id BIGSERIAL,
   user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
   image_path VARCHAR(255) NOT NULL,
   description VARCHAR(255),
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY (user_id, id)
);

CREATE TABLE follower_followee (
   id BIGSERIAL,
   follower_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
   followee_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
   PRIMARY KEY (follower_id, id)
);

-- Indexes that matter for the query
CREATE INDEX ON post (user_id, created_at DESC);
CREATE INDEX ON follower_followee (follower_id, followee_id);
CREATE UNIQUE INDEX IF NOT EXISTS uniq_follow ON follower_followee(follower_id, followee_id);


-- Distribuer les tables avec Citus
SELECT create_reference_table('users');
SELECT create_distributed_table('post', 'user_id');
SELECT create_distributed_table('follower_followee', 'follower_id');
