# Project Obscure parsers for ALEAPP (Android)

`Parsers/` holds ready-to-use ALEAPP modules, one file per app (`obscure_<COUNTRY>_<App>.py`).

> These files are generated from `specs/` by `python obscure.py build`. Don't edit them by hand. Change the app's `parser.yaml` instead.

## Install

You need the **source version** of ALEAPP. The `.exe` releases bundle their own modules and can't load add-ons:

```
git clone https://github.com/abrignoni/ALEAPP
cd ALEAPP
pip install -r requirements.txt
```

**With the installer** (from the root of this repository):

```
python install.py aleapp C:\path\to\ALEAPP
```

**By hand:** copy `Parsers\obscure_*.py` into `ALEAPP\scripts\artifacts\`.

Restart ALEAPP (`aleapp.py` or `aleappGUI.py`). The artifacts appear with the app's category, for example *Marketplace > 2dehands - Chat messages*.

## Update or remove

- Update: pull the latest version of this repository and run the installer again. It overwrites the old files.
- Remove: `python install.py aleapp C:\path\to\ALEAPP --uninstall` deletes every `obscure_*.py` from ALEAPP.

## Notes

- Parsers read the databases with Python's `sqlite3`, so only intact records are shown. For deleted records, use the Cellebrite parser.
- All timestamps are UTC.
