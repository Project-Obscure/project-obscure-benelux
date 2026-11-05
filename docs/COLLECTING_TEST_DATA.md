# Collecting test data from your own test phones

Use **dedicated test phones with test accounts only**. Never use a seized device, a real case, or someone else's data to develop a parser, and never commit real data to this repository.

## 1. Generate activity

Install the app on a test phone, log in with a test account, and use the features you want to parse: send and receive messages (a second test phone/account helps), save searches, add favourites, share a location, and so on. **Write down what you did and when.** That's your ground truth for checking the parser later.

Also delete a few things (a message, a conversation). Physical Analyzer can recover deleted records, and you want to know what the app leaves behind.

## 2. Get the app's files

### Android

App databases live in `/data/data/<package>/databases/` (Cellebrite shows this as `/Root/data/<package>/...`). This folder isn't readable without root or a full file system extraction.

Find the package name:

```
adb shell pm list packages | findstr /i 2dehands
```

Then use one of these options:

- **Cellebrite (UFED/Inseyets) full file system extraction.** Open the extraction in Physical Analyzer, browse to `/Root/data/<package>/`, and export the whole folder.
- **Rooted test phone.** Force-stop the app first, then:

  ```
  adb shell su -c "tar -cf /sdcard/app.tar /data/data/<package>"
  adb pull /sdcard/app.tar
  ```

- **Android emulator** with a "Google APIs" image (not "Google Play"), which allows `adb root`. Only works if the app installs without the Play Store.

### iOS

App data lives in `/private/var/mobile/Containers/Data/Application/<UUID>/`. The UUID is random per install. The folder's `.com.apple.mobile_container_manager.metadata.plist` file holds the bundle ID, which is how you find the right folder.

- **Full file system extraction** (Cellebrite, or checkm8-based tools on supported devices). Export the app's container folder.
- **Encrypted iTunes/Finder backup.** Contains most apps' `Documents` and `Library` folders. A backup reader can export them.

Shared app-group containers (`/private/var/mobile/Containers/Shared/AppGroup/<UUID>/`) often hold the interesting databases too.

### Always

Copy each database **together with its `-wal` and `-shm` files**. Recent messages are often only in the `-wal` file.

## 3. Find the data

```
python obscure.py inspect path/to/databases/app.db
```

This lists every table with its columns and a few sample rows. Look for your test messages, search terms, and so on, and note the table, the columns, and how timestamps are stored. A 13-digit number is usually `unix_ms`. A 9-digit number around `7xxxxxxxx` is usually `apple_s`.

## 4. Write and check the parser

```
python obscure.py new BE-AppName             # or edit an existing parser.yaml
python obscure.py run BE-AppName --db path/to/app.db
```

`run` shows exactly what ALEAPP/iLEAPP will show. Compare it with your notes from step 1. Times are UTC, and Belgium/NL/LU are UTC+1 (UTC+2 in summer).

## 5. Make test data for the repository

```
python obscure.py inspect path/to/app.db --schema > specs/BE-AppName/tests/android_main.sql
```

Then edit that file. Keep only the tables the parser uses, and add a handful of **fake** `INSERT` rows that look like what you saw (same value formats, NULLs, edge cases). Then run:

```
python obscure.py test BE-AppName --update   # writes tests/expected.json, check it
python obscure.py test                       # all parsers
```

## 6. Check in the real tools

Build with `python obscure.py build` and load the output into ALEAPP/iLEAPP, Physical Analyzer and AXIOM using the same extraction (see [INSTALL.md](INSTALL.md)). If everything matches your notes, set `status: verified` and fill in `versions_tested`.
