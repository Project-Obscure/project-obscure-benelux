# Tool support: what is verified and what is not

`python obscure.py test` runs every generated parser against its test data:

- **ALEAPP/iLEAPP:** the generated module runs for real with Python 3. Only `scripts.ilapfuncs` is stubbed.
- **AXIOM:** the generated SQL runs for real against the test database.
- **Cellebrite:** the generated script runs against a **mock** of the Physical Analyzer API, and is checked for syntax that IronPython 2.7 can't handle.

All outputs must agree with the reference engine. These checks prove the generated logic is right. They don't prove the tools accept the files. Status per tool:

| Tool | Status | To do |
|---|---|---|
| ALEAPP / iLEAPP | LEAPP "artifacts v2" format (`__artifacts_v2__` + `@artifact_processor`). Checked by reading the current ALEAPP source (Nov 2026): the plugin loader finds the functions, the 4-argument signature is still supported, and source paths are newline-separated. | Run a real ALEAPP/iLEAPP on a test extraction and check the report. |
| Cellebrite PA | Uses the API from the Python Scripting Guide (`SQLiteParser`, `ReadTableRecords`, `Chat`, `InstantMessage`, `Party`, `Contact`, `UserAccount`, `Location`, `SearchedItem`, `Note`, `TimeStamp`). | Run once in Physical Analyzer and confirm: models appear, timestamps are UTC, deleted records are marked deleted, and the source highlighting (`MemoryRange`) works. |
| Magnet AXIOM | Interim: SQL queries + README. | Export an existing SQLite custom artifact from AXIOM (or one from Artifact Exchange) as a reference, then make `framework/gen_axiom.py` write that format directly. |

## How the generators share code

```
parser.yaml
   |
   +-- framework/spec.py              validate, build SQL, build Cellebrite path regex
   |
   +-- framework/templates/runtime.py   value conversion (timestamps, bool, hex, value maps)
   +-- framework/templates/shaper.py    row -> labelled values + roles
   |        (both embedded verbatim into every generated file; Python 2.7 + 3 compatible)
   |
   +-- gen_leapp.py       -> ALEAPP / iLEAPP module
   +-- gen_cellebrite.py  -> Physical Analyzer script (+ templates/cellebrite_engine.py)
   +-- gen_axiom.py       -> AXIOM SQL + README
```

A fix in `runtime.py` or `shaper.py` reaches every tool on the next `build`.
