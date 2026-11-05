# parser.yaml reference

Each parser is a folder in `parsers/` named `<COUNTRY>-<AppName>` (for example `BE-2dehands`, `NL-Tikkie`, `LU-Digicash`):

```
parsers/BE-2dehands/
  parser.yaml          what to read and how to show it
  README.md            app notes, versions tested, known gaps
  tests/
    android_main.sql   schema + fake rows, one file per source
    expected.json      expected output, written by `obscure.py test --update`
```

The same `parser.yaml` is turned into:

| Tool | Output | How it reads the data |
|---|---|---|
| ALEAPP | `build/aleapp/scripts/artifacts/obscure_<ID>.py` | SQL over `sqlite3` |
| iLEAPP | `build/ileapp/scripts/artifacts/obscure_<ID>.py` | SQL over `sqlite3` |
| Cellebrite Physical Analyzer | `build/cellebrite/<ID>.py` | `SQLiteParser` tables, **including deleted records** |
| Magnet AXIOM | `build/axiom/<ID>/*.sql` + README | SQL (interim, see [TOOLS.md](TOOLS.md)) |

Physical Analyzer's `SQLiteParser` reads tables directly and can't run SQL. That's why a spec describes **one main table plus optional joins**, not free-form SQL. Every tool can then do exactly the same thing.

## `app`

| Key | Required | Notes |
|---|---|---|
| `id` | yes | `BE-`, `NL-` or `LU-` + app name. Must match the folder name. |
| `name` | yes | Shown in every tool (Cellebrite uses it as the source application). |
| `country` | yes | `BE`, `NL` or `LU`. |
| `author` | yes | |
| `category` | no | LEAPP report category. Defaults to `name`. |
| `description` | no | |
| `status` | no | `draft` (not checked on real data) or `verified`. |
| `versions_tested` | no | List of `{platform, app_version, os}` you verified on a real device. |

## `sources`

A source is one database file, given by a name you choose:

```yaml
sources:
  android_main:
    platform: android            # android -> ALEAPP, ios -> iLEAPP
    path: "*/data/data/com.example.app/databases/main.db"
    cellebrite_regex: ...        # optional override, see below
```

- `path` is an ALEAPP/iLEAPP style glob. The generated LEAPP module also collects `<path>-*`, so the `-wal`/`-shm` files come along.
- For Cellebrite, the glob becomes a regex for `fs.Search()`. `data/data/` also matches Physical Analyzer's `/Root/data/<package>/` layout. Set `cellebrite_regex` only if the automatic one doesn't find the file.
- The file name may contain `*` (for example `account_*.db`). Every matching database is parsed.

## `artifacts`

```yaml
artifacts:
  - id: messages                 # letters/digits/_ only, unique in this parser
    name: Chat messages
    description: ...
    type: chat                   # chat | contact | account | location | search | generic
    source: android_main
    table: messages
    order_by: sent_at            # optional, column of the main table (or alias.column)
    joins:                       # optional lookups, LEFT JOIN semantics
      - table: conversations
        as: conversations        # optional alias, defaults to the table name
        local: conversation_id   # column in the main table
        foreign: id              # column in the joined table
    fields:
      - {column: sent_at, label: Sent, format: unix_ms, role: timestamp}
      - {column: conversations.ad_title, label: Ad title, role: subject}
      - {column: account_type, label: Type, values: {0: Private, 1: Business}}
```

### Field keys

| Key | Notes |
|---|---|
| `column` | Column of the main table, or `<join alias>.<column>`. |
| `label` | Column header in LEAPP/AXIOM and label in Cellebrite notes. |
| `format` | How to read the raw value (table below). Default `text`. |
| `values` | Optional mapping of raw values to text, such as status codes. |
| `role` | What the value means for the artifact `type`. Used to fill the right Cellebrite model property. |

Every field appears as a column in ALEAPP/iLEAPP/AXIOM. In Cellebrite, fields with a role go into the matching model property. Fields without a role go into notes or the body where the model allows it.

### Formats

| Format | Raw value |
|---|---|
| `text` | Text; empty string is treated as empty. Default. |
| `int`, `float` | Numbers. |
| `bool` | 0/1 (also `true`/`yes`) shown as Yes/No. |
| `hex` | Blob shown as hex. |
| `unix_s`, `unix_ms`, `unix_us`, `unix_ns` | Seconds / milliseconds / microseconds / nanoseconds since 1970-01-01 UTC. |
| `apple_s`, `apple_ns` | Seconds / nanoseconds since 2001-01-01 UTC (iOS Core Data / Cocoa). |
| `webkit_us` | Microseconds since 1601-01-01 UTC (Chromium/WebKit). |
| `iso` | ISO 8601 text such as `2024-11-05T09:46:40Z`. |

A timestamp of `0` is treated as empty. All times are UTC.

### Types and roles (what Cellebrite creates)

| Type | Cellebrite model | Roles |
|---|---|---|
| `chat` | `Chat` with `InstantMessage`s, grouped by `chat_id` | `chat_id`, `timestamp`, `body` (required), `from`, `to`, `peer`, `outgoing`, `subject` |
| `contact` | `Contact` | `name`, `phone`, `email`, `user_id`, `created`, `notes` |
| `account` | `UserAccount` | `name`, `username`, `email`, `user_id`, `created` |
| `location` | `Location` | `latitude`, `longitude` (both required), `timestamp`, `name`, `description` |
| `search` | `SearchedItem` | `value`, `timestamp` |
| `generic` | `Note` (Folder = artifact name, Body = every field) | `title`, `timestamp` |

How chats are filled: `peer` is the other person in the conversation and `outgoing` (a `bool` field) says whether the device owner sent the message. With these two, the generated Cellebrite parser sets From/To correctly even when the app only stores a direction flag. Explicit `from`/`to` values always win.

## Rules for test data

- `tests/<source>.sql` holds the **real schema** (`python obscure.py inspect app.db --schema`) plus a few **fake** rows. Never put real personal data in the repository, not even your own.
- Add rows for edge cases you have seen: NULLs, zero timestamps, deleted conversations, emoji.
- `python obscure.py test --update` writes `expected.json`. Check it by hand before you commit it.
