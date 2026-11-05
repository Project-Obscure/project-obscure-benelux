SELECT CASE WHEN "main"."sent_at" IS NULL OR "main"."sent_at" = 0 THEN NULL ELSE datetime("main"."sent_at" / 1000.0, 'unixepoch') END AS "Sent",
       "main"."conversation_id" AS "Conversation ID",
       "conversations"."ad_title" AS "Ad title",
       "conversations"."other_party_name" AS "Other party",
       "main"."sender_name" AS "Sender",
       CASE WHEN "main"."is_outgoing" IS NULL THEN NULL WHEN "main"."is_outgoing" THEN 'Yes' ELSE 'No' END AS "Outgoing",
       "main"."body" AS "Message",
       CASE WHEN "main"."is_read" IS NULL THEN NULL WHEN "main"."is_read" THEN 'Yes' ELSE 'No' END AS "Read"
FROM "messages" AS "main"
LEFT JOIN "conversations" AS "conversations" ON "main"."conversation_id" = "conversations"."id"
ORDER BY "main"."sent_at";
