# Project Obscure parsers for Magnet AXIOM

`Parsers/<ID>/` holds, per app:
- one `.sql` query per artifact, with timestamps already converted to UTC text
- a `README.md` with the database path (Android/iOS) and the columns

> These files are generated from `specs/` by `python obscure.py build`. Don't edit them by hand.

## Use

AXIOM supports custom artifacts for SQLite databases. For each artifact:

1. Look up the database path in `Parsers/<ID>/README.md`.
2. Create a SQLite custom artifact for that database in AXIOM and use the `.sql` file as its query.
3. Add the custom artifact to your processing settings and process (or re-process) the evidence.

## Status

This is an interim format. The plan is to generate AXIOM's own custom-artifact files directly, so they can be imported with a single click. That needs one exported AXIOM custom artifact as a reference for the exact format. If you have AXIOM, please share one by opening an issue.
