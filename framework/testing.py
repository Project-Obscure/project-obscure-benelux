"""Run generated parsers outside their tools, against a test database.

* ALEAPP/iLEAPP modules are executed with a stub `scripts.ilapfuncs`.
* Cellebrite scripts are executed against a mock of the Physical Analyzer
  API (ds, SQLiteParser, content models) backed by Python's sqlite3.

The mocks only implement what the generated code uses. They prove the
generated logic is right; they do not replace a run in the real tools.
"""
import datetime
import os
import sqlite3
import sys
import types

from . import engine


# ---------------------------------------------------------------- LEAPP ------
def run_leapp_module(source_code, db_paths, function_names):
    """Execute a generated ALEAPP/iLEAPP module; return {function: (headers, rows)}."""
    scripts = types.ModuleType('scripts')
    ilapfuncs = types.ModuleType('scripts.ilapfuncs')
    ilapfuncs.artifact_processor = lambda func: func
    ilapfuncs.logfunc = lambda message: print('  [leapp log] ' + message)
    scripts.ilapfuncs = ilapfuncs
    saved = {k: sys.modules.get(k) for k in ('scripts', 'scripts.ilapfuncs')}
    sys.modules['scripts'] = scripts
    sys.modules['scripts.ilapfuncs'] = ilapfuncs
    try:
        namespace = {'__name__': 'obscure_generated'}
        exec(compile(source_code, 'generated-leapp', 'exec'), namespace)
    finally:
        for key, value in saved.items():
            if value is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = value
    results = {}
    for name in function_names:
        headers, rows, _source = namespace[name](list(db_paths), None, None, False)
        results[name] = (headers, rows)
    return results


def leapp_rows_as_text(rows):
    out = []
    for row in rows:
        cells = []
        for value in row:
            if isinstance(value, datetime.datetime):
                cells.append(value.strftime('%Y-%m-%d %H:%M:%S') + ' UTC')
            else:
                cells.append(engine.obs_format(value) if value != '' else '')
        out.append(cells)
    return out


# ----------------------------------------------------------- Cellebrite ------
class _Field(object):
    def __init__(self):
        self.Value = None
        self.Source = None
        self.items = []

    def Add(self, item):
        self.items.append(item)


class _Model(object):
    def __init__(self, *args):
        object.__setattr__(self, '_fields', {})
        object.__setattr__(self, 'Deleted', None)
        object.__setattr__(self, '_args', args)

    def __getattr__(self, name):
        if name.startswith('__'):
            raise AttributeError(name)
        fields = object.__getattribute__(self, '_fields')
        if name not in fields:
            fields[name] = _Field()
        return fields[name]


def _model_class(name):
    return type(name, (_Model,), {})


class _DeletedState(object):
    Intact = 'Intact'
    Deleted = 'Deleted'
    Unknown = 'Unknown'


class _MockDateTime(object):
    def __init__(self, *args):
        self.dt = datetime.datetime(*args[:6])

    def AddSeconds(self, seconds):
        result = _MockDateTime(1970, 1, 1)
        result.dt = self.dt + datetime.timedelta(seconds=seconds)
        return result


class _TimeStamp(str):
    def __new__(cls, dt, has_tz=False):
        return str.__new__(cls, dt.dt.strftime('%Y-%m-%d %H:%M:%S') + ' UTC')

    @staticmethod
    def FromUnixTime(seconds):
        return _TimeStamp(_MockDateTime(1970, 1, 1).AddSeconds(seconds))


class _Party(object):
    @staticmethod
    def MakeFrom(value, source):
        return 'From: %s' % value

    @staticmethod
    def MakeTo(value, source):
        return 'To: %s' % value


class _RecField(object):
    def __init__(self, value):
        self.Value = value
        self.Source = None


class _Record(dict):
    Deleted = _DeletedState.Intact

    def __getitem__(self, key):
        return _RecField(dict.__getitem__(self, key))


class _Database(object):
    def __init__(self, path):
        self.path = path
        conn = engine.open_readonly(path)
        try:
            self.Tables = [r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")]
        finally:
            conn.close()

    @staticmethod
    def FromNode(node):
        return _Database(node.real_path)

    def __getitem__(self, table):
        conn = engine.open_readonly(self.path)
        try:
            cursor = conn.execute('SELECT * FROM "%s"' % table.replace('"', '""'))
            names = [d[0] for d in cursor.description]
            return [_Record(zip(names, row)) for row in cursor]
        finally:
            conn.close()

    def ReadTableRecords(self, signature, deleted):
        return self[signature.name]


class _TableSignature(object):
    def __init__(self, name):
        self.name = name


class _Node(object):
    def __init__(self, absolute_path, real_path):
        self.AbsolutePath = absolute_path
        self.real_path = real_path


class _FileSystem(object):
    def __init__(self, files):
        self.files = files

    def Search(self, regex):
        import re
        return [n for n in self.files if re.search(regex, n.AbsolutePath)]


class _Models(list):
    def Add(self, model):
        self.append(model)

    def AddRange(self, models):
        self.extend(models)


def run_cellebrite_script(source_code, mounts):
    """Run a generated Physical Analyzer script. mounts: [(device_path, local_db_path)]."""
    ds = types.SimpleNamespace(
        FileSystems=[_FileSystem([_Node(dev, real) for dev, real in mounts])], Models=_Models())
    physical = types.ModuleType('physical')
    model_names = ('InstantMessage', 'Chat', 'Contact', 'UserAccount', 'PhoneNumber',
                   'EmailAddress', 'UserID', 'Location', 'SearchedItem', 'Note')
    for name in model_names:
        setattr(physical, name, _model_class(name))
    physical.ds = ds
    physical.DeletedState = _DeletedState
    physical.TimeStamp = _TimeStamp
    physical.Party = _Party
    physical.MemoryRange = lambda source: source
    physical.Coordinate = lambda lat, lon: '(%s, %s)' % (lat, lon)
    physical.__all__ = list(model_names) + ['ds', 'DeletedState', 'TimeStamp', 'Party',
                                            'MemoryRange', 'Coordinate']
    sqlite_parser = types.ModuleType('SQLiteParser')
    sqlite_parser.Database = _Database
    sqlite_parser.TableSignature = _TableSignature
    system = types.ModuleType('System')
    system.DateTime = _MockDateTime
    system.DateTimeKind = types.SimpleNamespace(Utc='Utc')
    convert = types.ModuleType('System.Convert')
    convert.IsDBNull = lambda value: False
    system.Convert = convert
    fakes = {'physical': physical, 'SQLiteParser': sqlite_parser,
             'System': system, 'System.Convert': convert}
    saved = {k: sys.modules.get(k) for k in fakes}
    sys.modules.update(fakes)
    try:
        exec(compile(source_code, 'generated-cellebrite', 'exec'), {'__name__': '__main__'})
    finally:
        for key, value in saved.items():
            if value is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = value
    return [dump_model(m) for m in ds.Models]


def dump_model(model):
    """Plain dict view of a mock model, for comparing with expected output."""
    if not isinstance(model, _Model):
        return model
    out = {'model': type(model).__name__}
    for name, field in sorted(model._fields.items()):
        if field.items:
            out[name] = [dump_model(i) for i in field.items]
        elif field.Value is not None:
            out[name] = dump_model(field.Value)
    return out


def device_path_for(source):
    """A plausible Physical Analyzer path for a source glob, used to test path matching."""
    path = source['path'].replace('\\', '/')
    while path.startswith('*/') or path.startswith('**/'):
        path = path.split('/', 1)[1]
    path = path.replace('data/data/', 'data/', 1)
    path = path.replace('**/', '').replace('*', 'X')
    return '/Root/' + path


def py3_only_constructs(source_code):
    """Syntax that would break IronPython 2.7 (Physical Analyzer). Returns line descriptions."""
    import ast
    tree = ast.parse(source_code)
    banned = {
        ast.JoinedStr: 'f-string',
        ast.AnnAssign: 'variable annotation',
        ast.Nonlocal: 'nonlocal',
        ast.YieldFrom: 'yield from',
        ast.AsyncFunctionDef: 'async def',
        ast.Await: 'await',
        ast.NamedExpr: 'walrus operator',
        ast.Starred: 'starred expression',
    }
    found = []
    for node in ast.walk(tree):
        for cls, label in banned.items():
            if isinstance(node, cls):
                found.append('line %d: %s' % (node.lineno, label))
        if isinstance(node, (ast.FunctionDef, ast.Lambda)):
            args = node.args
            if args.kwonlyargs or args.posonlyargs or getattr(node, 'returns', None) \
                    or any(a.annotation for a in args.args):
                found.append('line %d: py3-only function signature' % node.lineno)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == 'print' and node.keywords:
            found.append('line %d: print() with keyword arguments' % node.lineno)
        if isinstance(node, ast.Raise) and node.cause is not None:
            found.append('line %d: raise ... from' % node.lineno)
    return found


def build_test_db(sql_path, out_dir):
    db_path = os.path.join(out_dir, os.path.basename(sql_path).rsplit('.', 1)[0] + '.db')
    if os.path.exists(db_path):
        os.remove(db_path)
    with open(sql_path, encoding='utf-8') as handle:
        script = handle.read()
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(script)
        conn.commit()
    finally:
        conn.close()
    return db_path
