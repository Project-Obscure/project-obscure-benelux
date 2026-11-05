SELECT "main"."display_name" AS "Name",
       "main"."email" AS "Email",
       "main"."user_id" AS "User ID",
       CASE WHEN "main"."registered_at" IS NULL OR "main"."registered_at" = 0 THEN NULL ELSE datetime("main"."registered_at", 'unixepoch') END AS "Registered",
       CASE CAST("main"."account_type" AS TEXT) WHEN '0' THEN 'Private' WHEN '1' THEN 'Business' ELSE "main"."account_type" END AS "Account type"
FROM "user" AS "main";
