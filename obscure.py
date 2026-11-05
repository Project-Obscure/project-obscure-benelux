#!/usr/bin/env python3
"""Project Obscure Benelux command line tool.

  python obscure.py new BE-MyApp              scaffold a new parser
  python obscure.py inspect app.db            show tables, columns and sample rows
  python obscure.py run parsers/BE-MyApp --db app.db
                                              run a parser on a real database
  python obscure.py validate                  check every parser.yaml
  python obscure.py test [--update]           test generated parsers for every tool
  python obscure.py build                     write ALEAPP/iLEAPP/Cellebrite/AXIOM files to build/
"""
import argparse
import fnmatch
import json
import os
import shutil
import sqlite3
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from framework import engine, gen_axiom, gen_cellebrite, gen_leapp, testing  # noqa: E402
from framework import spec as specmod  # noqa: E402


def _parser_dirs(names):
    if not names:
        return specmod.discover(ROOT)
    out = []
    for name in names:
        path = name if os.path.isdir(name) else os.path.join(ROOT, 'parsers', name)
        out.append(path)
    return out


def generate_all(spec):
    files = {}
    for platform in specmod.PLATFORMS:
        files.update(gen_leapp.generate(spec, platform))
    files.update(gen_cellebrite.generate(spec))
    files.update(gen_axiom.generate(spec))
    return files


# ------------------------------------------------------------------ commands --
def cmd_validate(args):
    failed = 0
    for parser_dir in _parser_dirs(args.parsers):
        try:
            spec = specmod.load(parser_dir)
            print('OK    %s (%d artifacts)' % (spec['app']['id'], len(spec['artifacts'])))
        except specmod.SpecError as ex:
            failed += 1
            print('FAIL  %s' % ex)
    return 1 if failed else 0


def cmd_build(args):
    out_dir = os.path.abspath(args.out)
    count = 0
    for parser_dir in _parser_dirs(args.parsers):
        spec = specmod.load(parser_dir)
        for rel, content in generate_all(spec).items():
            path = os.path.join(out_dir, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8', newline='\n') as handle:
                handle.write(content)
            print('wrote %s' % os.path.relpath(path, ROOT))
            count += 1
    print('%d file(s) written to %s' % (count, os.path.relpath(out_dir, ROOT)))
    return 0


def _print_table(headers, rows, limit):
    widths = [min(40, max([len(h)] + [len(r[i]) for r in rows[:limit]])) for i, h in enumerate(headers)]
    clip = lambda text, w: text if len(text) <= w else text[:w - 1] + '~'
    print('  ' + ' | '.join(clip(h, w).ljust(w) for h, w in zip(headers, widths)))
    print('  ' + '-+-'.join('-' * w for w in widths))
    for row in rows[:limit]:
        print('  ' + ' | '.join(clip(c.replace('\n', ' '), w).ljust(w) for c, w in zip(row, widths)))
    if len(rows) > limit:
        print('  ... %d more row(s)' % (len(rows) - limit))


def cmd_run(args):
    spec = specmod.load(_parser_dirs([args.parser])[0])
    status = 0
    for art in spec['artifacts']:
        if args.artifact and art['id'] != args.artifact:
            continue
        source = spec['sources'][art['source']]
        pattern = specmod.db_filename(source)
        matches = [d for d in args.db if fnmatch.fnmatch(os.path.basename(d), pattern)]
        if not matches and len(spec['sources']) == 1:
            matches = list(args.db)
        if not matches:
            print('\n[%s] skipped: no --db file named like %s' % (art['id'], pattern))
            continue
        for db in matches:
            print('\n[%s] %s  <-  %s' % (art['id'], art['name'], db))
            try:
                shaped = engine.run_artifact(art, db)
            except sqlite3.Error as ex:
                print('  ERROR: %s' % ex)
                print('  Check the table/column names in parser.yaml with: python obscure.py inspect %s' % db)
                status = 1
                continue
            headers = [f['label'] for f in art['fields']]
            _print_table(headers, engine.as_table(shaped), args.limit)
            print('  %d row(s)' % len(shaped))
    return status


def cmd_inspect(args):
    conn = engine.open_readonly(args.db)
    if args.schema:
        try:
            print('-- Schema of %s (paste into tests/<source>.sql, then add fake rows)'
                  % os.path.basename(args.db))
            for (sql,) in conn.execute("SELECT sql FROM sqlite_master WHERE type='table' "
                                       "AND sql IS NOT NULL AND name NOT LIKE 'sqlite_%' ORDER BY name"):
                print(sql + ';')
        finally:
            conn.close()
        return 0
    try:
        tables = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        for table in tables:
            quoted = specmod.quote_ident(table)
            count = conn.execute('SELECT COUNT(*) FROM %s' % quoted).fetchone()[0]
            columns = conn.execute('PRAGMA table_info(%s)' % quoted).fetchall()
            print('\n%s (%d rows)' % (table, count))
            for col in columns:
                print('  %-30s %s' % (col[1], col[2] or ''))
            if args.rows and count:
                cursor = conn.execute('SELECT * FROM %s LIMIT %d' % (quoted, args.rows))
                for row in cursor:
                    print('    ' + repr(tuple(row))[:200])
    finally:
        conn.close()
    return 0


def cmd_new(args):
    if not specmod.ID_RE.match(args.id):
        print('ID must look like BE-AppName, NL-AppName or LU-AppName')
        return 1
    target = os.path.join(ROOT, 'parsers', args.id)
    if os.path.exists(target):
        print('%s already exists' % os.path.relpath(target, ROOT))
        return 1
    template = os.path.join(ROOT, 'framework', 'templates', 'new_parser')
    shutil.copytree(template, target)
    yaml_path = os.path.join(target, 'parser.yaml')
    with open(yaml_path, encoding='utf-8') as handle:
        text = handle.read()
    text = text.replace('XX-AppName', args.id).replace('XX', args.id.split('-')[0])
    with open(yaml_path, 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(text)
    print('Created %s - edit parser.yaml, then run: python obscure.py test %s'
          % (os.path.relpath(target, ROOT), args.id))
    return 0


def _strip_utc(cell):
    return cell[:-4] if cell.endswith(' UTC') else cell


def test_parser(parser_dir, update):
    spec = specmod.load(parser_dir)
    app_id = spec['app']['id']
    tests_dir = os.path.join(parser_dir, 'tests')
    expected_path = os.path.join(tests_dir, 'expected.json')
    problems = []
    tmp = tempfile.mkdtemp(prefix='obscure-')
    try:
        dbs = {}
        for name, source in spec['sources'].items():
            sql = os.path.join(tests_dir, name + '.sql')
            if not os.path.isfile(sql):
                problems.append('missing test data tests/%s.sql' % name)
                continue
            # Name the test db like the real file so path/filename matching is exercised.
            built = testing.build_test_db(sql, tmp)
            real_name = specmod.db_filename(source).replace('*', 'x')
            final = os.path.join(tmp, name, real_name)
            os.makedirs(os.path.dirname(final), exist_ok=True)
            os.replace(built, final)
            dbs[name] = final
        if problems:
            return problems

        # 1. reference engine
        reference = {}
        for art in spec['artifacts']:
            reference[art['id']] = engine.as_table(engine.run_artifact(art, dbs[art['source']]))

        # 2. ALEAPP / iLEAPP
        for platform in specmod.PLATFORMS:
            for rel, code in gen_leapp.generate(spec, platform).items():
                arts = [a for a in spec['artifacts']
                        if spec['sources'][a['source']]['platform'] == platform]
                names = [gen_leapp.function_name(spec, a) for a in arts]
                results = testing.run_leapp_module(code, dbs.values(), names)
                for art, name in zip(arts, names):
                    headers, rows = results[name]
                    if [h[0] if isinstance(h, tuple) else h for h in headers] != \
                            [f['label'] for f in art['fields']]:
                        problems.append('%s: %s headers differ from spec' % (rel, art['id']))
                    if testing.leapp_rows_as_text(rows) != reference[art['id']]:
                        problems.append('%s: %s rows differ from reference engine' % (rel, art['id']))

        # 3. AXIOM queries
        for art in spec['artifacts']:
            conn = engine.open_readonly(dbs[art['source']])
            try:
                rows = conn.execute(gen_axiom.axiom_sql(art)).fetchall()
            finally:
                conn.close()
            got = [[engine.obs_format(v) for v in row] for row in rows]
            want = [[_strip_utc(c) for c in row] for row in reference[art['id']]]
            if got != want:
                problems.append('axiom: %s query output differs from reference engine' % art['id'])

        # 4. Cellebrite (mocked Physical Analyzer)
        code = list(gen_cellebrite.generate(spec).values())[0]
        for issue in testing.py3_only_constructs(code):
            problems.append('cellebrite: not IronPython 2.7 compatible: %s' % issue)
        mounts = [(testing.device_path_for(spec['sources'][n]), db) for n, db in dbs.items()]
        cellebrite = testing.run_cellebrite_script(code, mounts)
        if not cellebrite:
            problems.append('cellebrite: no models produced (path regex or table names wrong?)')

        actual = {'reference': reference, 'cellebrite': cellebrite}
        if update or not os.path.isfile(expected_path):
            with open(expected_path, 'w', encoding='utf-8', newline='\n') as handle:
                json.dump(actual, handle, indent=2, ensure_ascii=False)
                handle.write('\n')
            print('  wrote %s' % os.path.relpath(expected_path, ROOT))
        else:
            with open(expected_path, encoding='utf-8') as handle:
                expected = json.load(handle)
            for key in ('reference', 'cellebrite'):
                if expected.get(key) != actual[key]:
                    problems.append('%s output differs from tests/expected.json '
                                    '(run with --update if the change is intended)' % key)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return problems


def cmd_test(args):
    failed = 0
    for parser_dir in _parser_dirs(args.parsers):
        name = os.path.basename(parser_dir)
        try:
            problems = test_parser(parser_dir, args.update)
        except specmod.SpecError as ex:
            problems = [str(ex)]
        if problems:
            failed += 1
            print('FAIL  %s' % name)
            for problem in problems:
                print('      - %s' % problem)
        else:
            print('PASS  %s (reference, ALEAPP/iLEAPP, AXIOM SQL, Cellebrite mock)' % name)
    return 1 if failed else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)

    p = sub.add_parser('validate', help='check parser.yaml files')
    p.add_argument('parsers', nargs='*')
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser('build', help='generate files for every tool')
    p.add_argument('parsers', nargs='*')
    p.add_argument('--out', default=os.path.join(ROOT, 'build'))
    p.set_defaults(func=cmd_build)

    p = sub.add_parser('test', help='test generated parsers against tests/*.sql')
    p.add_argument('parsers', nargs='*')
    p.add_argument('--update', action='store_true', help='rewrite tests/expected.json')
    p.set_defaults(func=cmd_test)

    p = sub.add_parser('run', help='run a parser against real database file(s)')
    p.add_argument('parser')
    p.add_argument('--db', action='append', required=True, help='database file (repeatable)')
    p.add_argument('--artifact')
    p.add_argument('--limit', type=int, default=25)
    p.set_defaults(func=cmd_run)

    p = sub.add_parser('inspect', help='list tables/columns of a SQLite database')
    p.add_argument('db')
    p.add_argument('--rows', type=int, default=3, help='sample rows per table (0 = none)')
    p.add_argument('--schema', action='store_true', help='print CREATE TABLE statements only')
    p.set_defaults(func=cmd_inspect)

    p = sub.add_parser('new', help='create a parser from the template')
    p.add_argument('id', help='e.g. BE-2dehands, NL-Tikkie, LU-Digicash')
    p.set_defaults(func=cmd_new)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
