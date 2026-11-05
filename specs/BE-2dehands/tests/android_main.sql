-- Synthetic test data for BE-2dehands (placeholder schema, see parser.yaml).
-- Replace with a minimal, anonymised copy of the real schema once known.
-- Never commit real personal data: use your own test accounts only.

CREATE TABLE conversations (id TEXT PRIMARY KEY, ad_title TEXT, other_party_name TEXT);
CREATE TABLE messages (
  id INTEGER PRIMARY KEY, conversation_id TEXT, sender_name TEXT,
  is_outgoing INTEGER, body TEXT, sent_at INTEGER, is_read INTEGER);
CREATE TABLE saved_searches (id INTEGER PRIMARY KEY, query TEXT, category TEXT, postcode TEXT, created_at INTEGER);
CREATE TABLE favourites (ad_id TEXT PRIMARY KEY, title TEXT, price_cents INTEGER, seller_name TEXT, url TEXT, added_at INTEGER);
CREATE TABLE user (user_id TEXT, display_name TEXT, email TEXT, registered_at INTEGER, account_type INTEGER);

INSERT INTO conversations VALUES ('c-100', 'Gazelle stadsfiets 28 inch', 'Test Verkoper');
INSERT INTO conversations VALUES ('c-200', 'PlayStation 5 + 2 controllers', 'Test Koper');

INSERT INTO messages VALUES (1, 'c-100', 'Test Gebruiker', 1, 'Is de fiets nog beschikbaar?', 1730800000000, 1);
INSERT INTO messages VALUES (2, 'c-100', 'Test Verkoper', 0, 'Ja, je kan zaterdag komen kijken in Gent.', 1730800360500, 1);
INSERT INTO messages VALUES (3, 'c-200', 'Test Koper', 0, 'Wat is je laagste prijs?', 1730900000000, 0);
INSERT INTO messages VALUES (4, 'c-999', NULL, 1, 'Bericht in gesprek zonder metadata', 1730950000000, NULL);

INSERT INTO saved_searches VALUES (1, 'bakfiets', 'Fietsen', '9000', 1730700000000);
INSERT INTO saved_searches VALUES (2, 'iphone 15', NULL, NULL, 1730710000000);

INSERT INTO favourites VALUES ('a-1', 'Gazelle stadsfiets 28 inch', 15000, 'Test Verkoper', 'https://www.2dehands.be/v/a-1', 1730750000000);
INSERT INTO favourites VALUES ('a-2', 'Eettafel eik', NULL, NULL, NULL, 0);

INSERT INTO user VALUES ('u-42', 'Test Gebruiker', 'testgebruiker@example.com', 1700000000, 0);
