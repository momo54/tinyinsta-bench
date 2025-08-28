\set userId random(1, :n_users)
SELECT p.*
FROM post p
WHERE p.user_id = :userId
   OR p.user_id IN (
        SELECT followee_id
        FROM follower_followee
        WHERE follower_id = :userId
     )
ORDER BY p.created_at DESC;
