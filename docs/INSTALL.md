# Installing the parsers

The ready-to-use files are already in the repository, one folder per tool. You don't need to build anything.

1. Get the files: either **Code > Download ZIP** on GitHub, `git clone https://github.com/Project-Obscure/project-obscure-benelux`, or a per-tool zip from the Releases page.
2. Follow the README in your tool's folder:

| Tool | Instructions | Quick install |
|---|---|---|
| ALEAPP | [ALEAPP/README.md](../ALEAPP/README.md) | `python install.py aleapp C:\path\to\ALEAPP` |
| iLEAPP | [iLEAPP/README.md](../iLEAPP/README.md) | `python install.py ileapp C:\path\to\iLEAPP` |
| Cellebrite PA | [Cellebrite Physical Analyser/README.md](../Cellebrite%20Physical%20Analyser/README.md) | `python install.py cellebrite` (prints the steps) |
| Magnet AXIOM | [Magnet AXIOM/README.md](../Magnet%20AXIOM/README.md) | `python install.py axiom` (prints the steps) |

`python install.py list` shows which parsers are available per tool.

## Updating

Download or `git pull` the latest version and repeat the install. For ALEAPP/iLEAPP the installer overwrites the old files. For a Cellebrite plugin, package and install the new `.tplug`.

## Building from the specs (parser developers)

```
pip install -r requirements.txt
python obscure.py build          # regenerates <tool>/Parsers/ from specs/
python obscure.py build --out C:\somewhere\else    # or write a copy elsewhere
```
