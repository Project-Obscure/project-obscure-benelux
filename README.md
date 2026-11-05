# project-obscure-benelux

A community-driven collection of parsers for regional applications used in Belgium, Netherlands, and Luxembourg that are not commonly covered by commercial digital forensics tools like Cellebrite UFED, Magnet AXIOM, and others.

🎯Project Purpose

Commercial forensic tools excel at parsing internationally popular applications (WhatsApp, Facebook, Instagram), but regional and niche apps remain largely unsupported. Project Obscure Benelux focuses on filling this gap for the Benelux region.
This project is intended for:

- Digital forensics practitioners and researchers
- Incident response teams
- Law enforcement with proper authorization
- Academic research and education
- Security professionals conducting authorized investigations

📥 Download and install

Download the repository ([Code > Download ZIP](https://github.com/Project-Obscure/project-obscure-benelux/archive/refs/heads/main.zip)) or a zip per tool from [Releases](https://github.com/Project-Obscure/project-obscure-benelux/releases). Then open the folder for your tool:

| Tool | Folder | Install |
|---|---|---|
| ALEAPP (Android) | [ALEAPP/](ALEAPP) | `python install.py aleapp C:\path\to\ALEAPP` |
| iLEAPP (iOS) | [iLEAPP/](iLEAPP) | `python install.py ileapp C:\path\to\iLEAPP` |
| Cellebrite / Inseyets Physical Analyzer | [Cellebrite Physical Analyser/](Cellebrite%20Physical%20Analyser) | Run the script, or package it as a `.tplug` plugin. `python install.py cellebrite` prints the steps. |
| Magnet AXIOM | [Magnet AXIOM/](Magnet%20AXIOM) | SQLite custom artifacts (interim). `python install.py axiom` prints the steps. |

Each folder has a `README.md` with full instructions and a `Parsers/` folder with the ready-to-use files. `install.py` only needs Python: nothing to pip install.

📚 Parsers

| Parser | App | Platforms | Status |
|---|---|---|---|
| [BE-2dehands](specs/BE-2dehands) | 2dehands (marketplace) | Android | draft: schema still to be confirmed on a test phone |

🗂️ Repository layout

```
ALEAPP/Parsers/                    ready-to-use files per tool (generated, don't edit)
iLEAPP/Parsers/
Cellebrite Physical Analyser/Parsers/   (+ Resources/ with Cellebrite's Python docs)
Magnet AXIOM/Parsers/
specs/<ID>/parser.yaml             the source of every parser: edit these
framework/                         generators and test harness
docs/                              spec format, test data, tool status
install.py                         installer for users
obscure.py                         tool for parser developers
```

🧰 Writing parsers: one spec, every tool

Each parser is written once as a short `specs/<ID>/parser.yaml` (which database, which tables, what each column means). `obscure.py build` generates the files in every tool folder from it.

```
pip install -r requirements.txt
python obscure.py inspect app.db                       # explore an app database
python obscure.py new BE-AppName                       # start a parser in specs/
python obscure.py run BE-AppName --db app.db           # see what it extracts
python obscure.py test                                 # test generated parsers for every tool
python obscure.py build                                # regenerate the tool folders
```

Commit the spec **and** the regenerated tool folders together. CI fails if they're out of sync.

- [docs/SPEC.md](docs/SPEC.md): the `parser.yaml` format
- [docs/COLLECTING_TEST_DATA.md](docs/COLLECTING_TEST_DATA.md): getting data from your own test phones
- [docs/INSTALL.md](docs/INSTALL.md): installing parsers in each tool
- [docs/TOOLS.md](docs/TOOLS.md): what is verified per tool and how the generators work
- [docs/RELEASING.md](docs/RELEASING.md): branches and releases

🌍 Why Benelux?
We're starting with the Benelux region to:

- Build a focused, manageable collection
- Serve investigators working in Belgium, Netherlands, and Luxembourg
- Create templates and standards that can expand to other regions
- Develop a community around regional forensic needs

Interested in contributing parsers for your region? Contact Projectobscureglobal@proton.me

⚖️ **Legal and Ethical Use**
This project is designed for legal and authorized use only:

- Forensic examination with proper legal authority
- Incident response on systems you own or have authorization to examine
- Academic research and education
- Security testing on your own devices or with explicit permission

Users are responsible for ensuring their use complies with applicable laws and regulations in their jurisdiction.

📞 Contact & Community

- Email: projectobscureglobal@proton.me
- Issues: Use GitHub Issues for bug reports and feature requests
- Discussions: Use GitHub Discussions for general questions

📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
