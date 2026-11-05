# --- Project Obscure shaper -----------------------------------------------------
# Turns one raw database row into converted values, the same way in every tool.
# Embedded verbatim into generated parsers: keep it Python 2.7/IronPython/3 compatible.


def obs_shape(artifact, raw):
    """raw: dict of 'column' / 'alias.column' -> raw value.

    Returns a dict with:
      roles:   {role: converted value}          (only fields that have a role)
      columns: [(label, converted value), ...]  (every field, in spec order)
      extras:  [(label, converted value), ...]  (fields without a role)
    """
    roles = {}
    columns = []
    extras = []
    for field in artifact['fields']:
        value = obs_convert(raw.get(field['column']), field['format'], field.get('values'))
        columns.append((field['label'], value))
        role = field.get('role')
        if role:
            if roles.get(role) is None:
                roles[role] = value
        else:
            extras.append((field['label'], value))
    return {'roles': roles, 'columns': columns, 'extras': extras}


def obs_note_body(pairs):
    """'Label: value' lines for a list of (label, value) pairs, skipping empty values."""
    lines = []
    for field_label, value in pairs:
        if value is None:
            continue
        lines.append(field_label + ': ' + obs_format(value))
    return '\n'.join(lines)
# --- end shaper -----------------------------------------------------------------
