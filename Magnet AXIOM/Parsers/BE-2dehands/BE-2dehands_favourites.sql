SELECT CASE WHEN "main"."added_at" IS NULL OR "main"."added_at" = 0 THEN NULL ELSE datetime("main"."added_at" / 1000.0, 'unixepoch') END AS "Added",
       "main"."title" AS "Ad title",
       "main"."ad_id" AS "Ad ID",
       "main"."price_cents" AS "Price (cents)",
       "main"."seller_name" AS "Seller",
       "main"."url" AS "URL"
FROM "favourites" AS "main"
ORDER BY "main"."added_at";
