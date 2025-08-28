\set userId random(1, :n_users)
\set rnd random(1, 1000000000)
INSERT INTO post(user_id, image_path, description, created_at)
VALUES (:userId,
        '/img/'||:rnd||'.jpg',
        'new post '||:rnd,
        NOW());
