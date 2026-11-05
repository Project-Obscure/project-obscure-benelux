"""Load, validate and normalise parser.yaml specs."""
import os
import re

import yaml

TEMPLATES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

PLATFORMS = ('android', 'ios')
FORMATS = ('text', 'int', 'float', 'bool', 'hex', 'iso',
           'unix_s', 'unix_ms', 'unix_us', 'unix_ns', 'apple_s', 'apple_ns', 'webkit_us')
# Which roles each artifact type understands. Fields without a role are still
# shown in ALEAPP/iLEAPP/AXIOM and added as notes in Cellebrite where possible.
TYPES = {
    'chat': ('chat_id', 'timestamp', 'body', 'from', 'to', 'peer', 'outgoing', 'subject'),
    'contact': ('name', 'phone', 'email', 'user_id', 'created', 'notes'),
    'account': ('name', 'username', 'email', 'user_id', 'created'),
    'location': ('latitude', 'longitude', 'timestamp', 'name', 'description'),
    'search': ('value', 'timestamp'),
    'generic': ('title', 'timestamp'),
}
ID_RE = re.compile(r'^(BE|NL|LU)-[A-Za-z0-9][A-Za-z0-9_.-]*$')
IDENT_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


class SpecError(Exception):
    pass


def read_template(name):
    with open(os.path.join(TEMPLATES, name), encoding='utf-8') as handle:
        return handle.read()


def load(parser_dir):
    path = os.path.join(parser_dir, 'parser.yaml')
    if not os.path.isfile(path):
        raise SpecError('%s: parser.yaml not found' % parser_dir)
    with open(path, encoding='utf-8') as handle:
        spec = yaml.safe_load(handle)
    spec['_dir'] = os.path.abspath(parser_dir)
    errors = validate(spec)
    if errors:
        raise SpecError('%s:\n  - %s' % (path, '\n  - '.join(errors)))
    return spec


def validate(spec):
    """Check the spec and fill in defaults. Returns a list of error strings."""
    errors = []
    app = spec.get('app') or {}
    for key in ('id', 'name', 'country', 'author'):
        if not app.get(key):
            errors.append('app.%s is required' % key)
    if app.get('id') and not ID_RE.match(app['id']):
        errors.append('app.id must look like BE-AppName, NL-AppName or LU-AppName')
    app.setdefault('status', 'draft')
    app.setdefault('category', app.get('name'))
    app.setdefault('description', '')
    spec['app'] = app

    sources = spec.get('sources') or {}
    if not sources:
        errors.append('at least one source is required')
    for name, source in sources.items():
        if source.get('platform') not in PLATFORMS:
            errors.append('sources.%s.platform must be one of %s' % (name, ', '.join(PLATFORMS)))
        if not source.get('path'):
            errors.append('sources.%s.path is required' % name)
        source['name'] = name
    spec['sources'] = sources

    artifacts = spec.get('artifacts') or []
    if not artifacts:
        errors.append('at least one artifact is required')
    seen = set()
    for index, art in enumerate(artifacts):
        where = 'artifacts[%d]' % index
        art_id = art.get('id')
        if not art_id or not IDENT_RE.match(art_id):
            errors.append('%s.id must be a simple identifier (letters, digits, _)' % where)
        elif art_id in seen:
            errors.append('%s.id %r is used twice' % (where, art_id))
        seen.add(art_id)
        where = 'artifact %s' % art_id
        if art.get('source') not in sources:
            errors.append('%s: source %r is not defined in sources' % (where, art.get('source')))
        if not art.get('table'):
            errors.append('%s: table is required' % where)
        art.setdefault('name', art_id)
        art.setdefault('type', 'generic')
        art.setdefault('description', '')
        if art['type'] not in TYPES:
            errors.append('%s: type must be one of %s' % (where, ', '.join(TYPES)))
            continue
        aliases = {}
        for join in art.setdefault('joins', []):
            alias = join.setdefault('as', join.get('table'))
            if not join.get('table') or not join.get('local') or not join.get('foreign'):
                errors.append('%s: each join needs table, local and foreign' % where)
            elif not IDENT_RE.match(alias):
                errors.append('%s: join alias %r must be a simple identifier' % (where, alias))
            elif alias in aliases or alias == 'main':
                errors.append('%s: join alias %r is used twice' % (where, alias))
            aliases[alias] = join
        if not art.get('fields'):
            errors.append('%s: at least one field is required' % where)
        roles_used = set()
        for field in art.get('fields') or []:
            column = field.get('column')
            if not column:
                errors.append('%s: every field needs a column' % where)
                continue
            if '.' in column and column.split('.', 1)[0] not in aliases:
                errors.append('%s: field %r refers to unknown join %r'
                              % (where, column, column.split('.', 1)[0]))
            field.setdefault('label', column)
            field.setdefault('format', 'text')
            if field['format'] not in FORMATS:
                errors.append('%s: field %r has unknown format %r (use one of %s)'
                              % (where, column, field['format'], ', '.join(FORMATS)))
            if field.get('values'):
                field['values'] = dict((str(k), str(v)) for k, v in field['values'].items())
            role = field.get('role')
            if role:
                if role not in TYPES[art['type']]:
                    errors.append('%s: role %r is not valid for type %s (valid: %s)'
                                  % (where, role, art['type'], ', '.join(TYPES[art['type']])))
                roles_used.add(role)
        if art['type'] == 'chat' and 'body' not in roles_used:
            errors.append('%s: chat artifacts need a field with role: body' % where)
        if art['type'] == 'location' and not {'latitude', 'longitude'} <= roles_used:
            errors.append('%s: location artifacts need latitude and longitude roles' % where)
        order = art.get('order_by')
        if order and order not in [f.get('column') for f in art.get('fields') or []] \
                and not IDENT_RE.match(order):
            errors.append('%s: order_by must be a column name' % where)
    spec['artifacts'] = artifacts
    return errors


def runtime_artifact(art):
    """The subset of an artifact that generated code needs at runtime."""
    return {
        'id': art['id'],
        'name': art['name'],
        'type': art['type'],
        'table': art['table'],
        'order_by': art.get('order_by'),
        'joins': [{'table': j['table'], 'as': j['as'], 'local': j['local'],
                   'foreign': j['foreign']} for j in art['joins']],
        'fields': [dict((k, f[k]) for k in ('column', 'label', 'format', 'role', 'values')
                        if f.get(k) is not None) for f in art['fields']],
    }


def quote_ident(name):
    return '"%s"' % name.replace('"', '""')


def build_sql(art):
    """SELECT statement used by ALEAPP/iLEAPP, AXIOM and the reference engine."""
    selects = []
    for field in art['fields']:
        column = field['column']
        if '.' in column:
            alias, col = column.split('.', 1)
        else:
            alias, col = 'main', column
        selects.append('%s.%s AS %s' % (quote_ident(alias), quote_ident(col), quote_ident(column)))
    sql = 'SELECT %s\nFROM %s AS "main"' % (',\n       '.join(selects), quote_ident(art['table']))
    for join in art['joins']:
        sql += '\nLEFT JOIN %s AS %s ON "main".%s = %s.%s' % (
            quote_ident(join['table']), quote_ident(join['as']), quote_ident(join['local']),
            quote_ident(join['as']), quote_ident(join['foreign']))
    order = art.get('order_by')
    if order:
        if '.' in order:
            alias, col = order.split('.', 1)
        else:
            alias, col = 'main', order
        sql += '\nORDER BY %s.%s' % (quote_ident(alias), quote_ident(col))
    return sql


def db_filename(source):
    return source['path'].replace('\\', '/').rsplit('/', 1)[-1]


def glob_to_regex(glob):
    """Convert an ALEAPP-style path glob into a regex for Cellebrite's fs.Search().

    Cellebrite shows Android app data as /Root/data/<package>/... while
    ALEAPP paths usually contain /data/data/<package>/..., so 'data/data/'
    is made to match both.
    """
    path = glob.replace('\\', '/')
    while path.startswith('*/') or path.startswith('**/'):
        path = path.split('/', 1)[1]
    out = []
    i = 0
    while i < len(path):
        if path.startswith('data/data/', i):
            out.append('data/(?:data/)?')
            i += len('data/data/')
            continue
        char = path[i]
        if char == '*':
            if path.startswith('**', i):
                out.append('.*')
                i += 2
                continue
            out.append('[^/]*')
        elif char == '?':
            out.append('[^/]')
        else:
            out.append(re.escape(char))
        i += 1
    return '/' + ''.join(out) + '$'


def discover(root):
    """All parser spec directories under root/specs."""
    base = os.path.join(root, 'specs')
    if not os.path.isdir(base):
        return []
    return sorted(os.path.join(base, name) for name in os.listdir(base)
                  if os.path.isfile(os.path.join(base, name, 'parser.yaml')))
