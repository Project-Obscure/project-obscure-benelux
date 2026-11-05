# Project Obscure parsers for Cellebrite (Inseyets) Physical Analyzer

`Parsers/` holds one Python decoding script per app (`<COUNTRY>-<App>.py`). `Resources/` has Cellebrite's Python documentation.

> These files are generated from `specs/` by `python obscure.py build`. Don't edit them by hand.

What the scripts do:
- Find the app's databases in every file system of the extraction.
- Read them with Physical Analyzer's `SQLiteParser`, including the WAL file and **deleted records**.
- Add the results to Analyzed Data as chats, contacts, user accounts, locations, searched items, or notes (for app data that has no matching Cellebrite model).

Requirements: Inseyets PA with a license that includes Python (Inseyets Pro).

## Option 1: run a script on one case

1. Tools > Settings > General tab: tick **Enable python development and debugging**, then OK.
2. Open the case. In *Enrich Your Data*, tick **Python**, then Start Examination.
3. Python tab > Run script > **Decoding Scope**, and pick `Parsers\<ID>.py`.
4. The output shows `[Project Obscure] <ID> / <artifact>: N item(s)`. Results appear under Analyzed Data.

## Option 2: install as a plugin for every extraction

1. Run `PluginPackager.exe` from the Physical Analyzer folder (default `C:\Program Files\Cellebrite Mobile Synchronization\Ultra Physical Analyzer\`).
2. Select `Parsers\<ID>.py`, fill in the details, and click **Publish**. You get a `.tplug` file.
3. Plugins > Add/Remove Plugins > **Install Decoding Plugin**, then pick the `.tplug`.
4. Settings > **Post-chain Plugins** > Add Plugin, and select it.

From then on the parser runs at the end of every new case's processing. Details: `Resources/Python Integration.pdf`.

Run `python install.py cellebrite` to print these steps.
