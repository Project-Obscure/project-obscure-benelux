#!/usr/bin/env python3
"""Install Project Obscure Benelux parsers into your forensic tools.

  python install.py aleapp  C:\\Tools\\ALEAPP        copy the ALEAPP parsers into an ALEAPP folder
  python install.py ileapp  C:\\Tools\\iLEAPP        copy the iLEAPP parsers into an iLEAPP folder
  python install.py aleapp  C:\\Tools\\ALEAPP --uninstall
  python install.py cellebrite                     show how to install in Physical Analyzer
  python install.py axiom                          show how to use the AXIOM queries
  python install.py list                           list the parsers available per tool

Only uses the Python standard library: no pip install needed.
"""
import argparse
import glob
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
FOLDERS = {
    'aleapp': 'ALEAPP',
    'ileapp': 'iLEAPP',
    'cellebrite': 'Cellebrite Physical Analyser',
    'axiom': 'Magnet AXIOM',
}
PREFIX = 'obscure_'


def parsers_dir(tool):
    return os.path.join(ROOT, FOLDERS[tool], 'Parsers')


def leapp_target(tool, path):
    """Return <path>/scripts/artifacts after checking it is a LEAPP source checkout."""
    name = FOLDERS[tool]
    path = os.path.abspath(os.path.expanduser(path))
    artifacts = os.path.join(path, 'scripts', 'artifacts')
    if os.path.isdir(artifacts):
        return artifacts
    if os.path.basename(path) == 'artifacts' and os.path.isdir(path):
        return path
    exes = glob.glob(os.path.join(path, '*.exe'))
    print('ERROR: %s is not an %s source folder (no scripts\\artifacts inside).' % (path, name))
    if exes:
        print('It looks like a compiled %s release (.exe). Those bundle their own modules,' % name)
        print('so add-on parsers need the source version:')
    else:
        print('Use the folder of the %s source version:' % name)
    repo = 'abrignoni/%s' % name
    print('  git clone https://github.com/%s' % repo)
    print('  cd %s' % name)
    print('  pip install -r requirements.txt')
    print('then run: python install.py %s <that folder>' % tool)
    sys.exit(1)


def install_leapp(tool, path, uninstall):
    target = leapp_target(tool, path)
    if uninstall:
        removed = sorted(glob.glob(os.path.join(target, PREFIX + '*.py')))
        for file in removed:
            os.remove(file)
            print('removed %s' % file)
        print('%d Project Obscure parser(s) removed from %s' % (len(removed), target))
        return
    sources = sorted(glob.glob(os.path.join(parsers_dir(tool), PREFIX + '*.py')))
    if not sources:
        print('There are no %s parsers yet.' % FOLDERS[tool])
        return
    for source in sources:
        shutil.copy2(source, target)
        print('installed %s' % os.path.basename(source))
    print('\n%d parser(s) copied to %s' % (len(sources), target))
    print('Restart %s. The artifacts are listed with the app name (module names start with %s).'
          % (FOLDERS[tool], PREFIX))


def show_cellebrite():
    files = sorted(glob.glob(os.path.join(parsers_dir('cellebrite'), '*.py')))
    print('Cellebrite (Inseyets) Physical Analyzer - needs a license with Python enabled.\n')
    print('Parsers in %s:' % parsers_dir('cellebrite'))
    for file in files:
        print('  %s' % os.path.basename(file))
    print("""
Try one parser on an open case:
  1. Tools > Settings > General: tick "Enable python development and debugging".
  2. Open the case, then Python > Run script > Decoding Scope, and pick the .py file above.
  3. Results appear under Analyzed Data (chats, accounts, searched items, notes, ...).

Run it automatically on every extraction:
  1. Run PluginPackager.exe from the Physical Analyzer install folder
     (default: C:\\Program Files\\Cellebrite Mobile Synchronization\\Ultra Physical Analyzer\\).
  2. Select the .py file, fill in the details, Publish -> you get a .tplug file.
  3. Plugins > Add/Remove Plugins > Install Decoding Plugin > pick the .tplug.
  4. Settings > Post-chain Plugins > Add Plugin.

More detail: "Cellebrite Physical Analyser/README.md" and the PDFs in its Resources folder.""")


def show_axiom():
    print('Magnet AXIOM - SQLite custom artifacts (interim format).\n')
    for readme in sorted(glob.glob(os.path.join(parsers_dir('axiom'), '*', 'README.md'))):
        print('  %s' % os.path.dirname(readme))
    print("""
Each folder has one .sql query per artifact and a README with the database path and
columns. Create an SQLite custom artifact in AXIOM with that path and query.
More detail: "Magnet AXIOM/README.md".""")


def show_list():
    for tool, folder in FOLDERS.items():
        base = parsers_dir(tool)
        items = sorted(n for n in os.listdir(base) if not n.startswith('.')) if os.path.isdir(base) else []
        print('%s (%s/Parsers): %s' % (folder, folder, ', '.join(items) if items else 'none yet'))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('tool', choices=['aleapp', 'ileapp', 'cellebrite', 'axiom', 'list'])
    parser.add_argument('path', nargs='?', help='ALEAPP/iLEAPP source folder')
    parser.add_argument('--uninstall', action='store_true', help='remove previously installed parsers')
    args = parser.parse_args(argv)
    if args.tool in ('aleapp', 'ileapp'):
        if not args.path:
            parser.error('give the %s folder, e.g. python install.py %s C:\\Tools\\%s'
                         % (FOLDERS[args.tool], args.tool, FOLDERS[args.tool]))
        install_leapp(args.tool, args.path, args.uninstall)
    elif args.tool == 'cellebrite':
        show_cellebrite()
    elif args.tool == 'axiom':
        show_axiom()
    else:
        show_list()
    return 0


if __name__ == '__main__':
    sys.exit(main())
