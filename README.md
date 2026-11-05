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

🧰 One parser, every tool

Each parser is written once as a short `parser.yaml` (which database, which tables, what each column means). From that file, the framework generates:

| Tool | Generated output |
|---|---|
| ALEAPP (Android) | module for `scripts/artifacts/` |
| iLEAPP (iOS) | module for `scripts/artifacts/` |
| Cellebrite / Inseyets Physical Analyzer | Decoding-scope Python script (can be packaged as `.tplug`), including deleted records |
| Magnet AXIOM | SQL queries for SQLite custom artifacts (interim) |

```
pip install -r requirements.txt
python obscure.py inspect app.db                       # explore an app database
python obscure.py new BE-AppName                       # start a parser
python obscure.py run BE-AppName --db app.db           # see what it extracts
python obscure.py test                                 # test generated parsers for every tool
python obscure.py build                                # write everything to build/
```

- [docs/SPEC.md](docs/SPEC.md): the `parser.yaml` format
- [docs/COLLECTING_TEST_DATA.md](docs/COLLECTING_TEST_DATA.md): getting data from your own test phones
- [docs/INSTALL.md](docs/INSTALL.md): installing parsers in each tool
- [docs/TOOLS.md](docs/TOOLS.md): what is verified per tool and how the generators work

📚 Parsers

| Parser | App | Platforms | Status |
|---|---|---|---|
| [BE-2dehands](parsers/BE-2dehands) | 2dehands (marketplace) | Android | draft: schema still to be confirmed on a test phone |

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
