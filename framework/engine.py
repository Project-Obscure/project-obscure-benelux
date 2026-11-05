"""Reference engine: run a spec directly against a SQLite file with plain Python 3.

Uses the exact same runtime/shaper code that is embedded in the generated
parsers, so its output is the yardstick the generated parsers are tested against.
"""
import sqlite3

from . import spec as specmod

_NS = {}
exec(compile(specmod.read_template('runtime.py') + '\n' + specmod.read_template('shaper.py'),
             'obscure-runtime', 'exec'), _NS)
obs_shape = _NS['obs_shape']
obs_format = _NS['obs_format']


def open_readonly(db_path):
    uri = 'file:%s?mode=ro' % db_path.replace('\\', '/')
    return sqlite3.connect(uri, uri=True)


def run_artifact(art, db_path):
    """Return a list of shaped rows for one artifact."""
    conn = open_readonly(db_path)
    try:
        cursor = conn.execute(specmod.build_sql(art))
        names = [d[0] for d in cursor.description]
        return [obs_shape(art, dict(zip(names, row))) for row in cursor]
    finally:
        conn.close()


def as_table(shaped_rows):
    """Rows as lists of display strings: what ALEAPP/iLEAPP should show."""
    return [[obs_format(value) for _label, value in row['columns']] for row in shaped_rows]
