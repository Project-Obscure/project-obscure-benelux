# Project Obscure parsers for iLEAPP (iOS)

`Parsers/` holds ready-to-use iLEAPP modules, one file per app (`obscure_<COUNTRY>_<App>.py`). There are none yet: they appear here as soon as a parser in `specs/` has an iOS source.

> These files are generated from `specs/` by `python obscure.py build`. Don't edit them by hand.

## Install

You need the **source version** of iLEAPP:

```
git clone https://github.com/abrignoni/iLEAPP
cd iLEAPP
pip install -r requirements.txt
```

**With the installer** (from the root of this repository):

```
python install.py ileapp C:\path\to\iLEAPP
```

**By hand:** copy `Parsers\obscure_*.py` into `iLEAPP\scripts\artifacts\`.

Restart iLEAPP.

## Update or remove

- Update: pull this repository and run the installer again.
- Remove: `python install.py ileapp C:\path\to\iLEAPP --uninstall`
