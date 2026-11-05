SELECT CASE WHEN "main"."created_at" IS NULL OR "main"."created_at" = 0 THEN NULL ELSE datetime("main"."created_at" / 1000.0, 'unixepoch') END AS "Created",
       "main"."query" AS "Search term",
       "main"."category" AS "Category",
       "main"."postcode" AS "Postcode"
FROM "saved_searches" AS "main"
ORDER BY "main"."created_at";
