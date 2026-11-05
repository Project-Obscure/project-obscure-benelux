# Installing the parsers

First build everything:

```
pip install -r requirements.txt
python obscure.py build
```

This creates `build/aleapp`, `build/ileapp`, `build/cellebrite` and `build/axiom`.

## ALEAPP / iLEAPP

Copy the generated modules into your ALEAPP or iLEAPP checkout:

```
copy build\aleapp\scripts\artifacts\obscure_*.py  <ALEAPP>\scripts\artifacts\
copy build\ileapp\scripts\artifacts\obscure_*.py  <iLEAPP>\scripts\artifacts\
```

Restart ALEAPP/iLEAPP. The artifacts show up under the app's category, and every module's name starts with `obscure_`.

## Cellebrite (Inseyets) Physical Analyzer

You need an Inseyets Pro license for Python. See the PDFs in [`Cellebrite Physical Analyser/Resources`](../Cellebrite%20Physical%20Analyser/Resources).

**To try a parser on a case:**
1. Tools > Settings > General: enable *Python development and debugging*.
2. Open the case with the extraction, then choose Python > Run script > **Decoding Scope** and pick `build/cellebrite/<ID>.py`.
3. The Python output shows `[Project Obscure] <ID> / <artifact>: N item(s)`. Results appear under Analyzed Data: chats, contacts, user accounts, searched items, locations, or notes for generic artifacts.

**To run it on every extraction:**
1. Run `PluginPackager.exe` from the Physical Analyzer install folder, select the generated `.py` file, and publish a `.tplug`.
2. Plugins > Add/Remove Plugins > Install Decoding Plugin.
3. Settings > Post-chain Plugins > Add the plugin.

## Magnet AXIOM

For now, `build/axiom/<ID>/` contains one SQL query per artifact with timestamps already converted to UTC text, plus a README with the file path and columns. Use these to create an SQLite custom artifact in AXIOM. Generating native AXIOM custom-artifact files is planned, see [TOOLS.md](TOOLS.md).
