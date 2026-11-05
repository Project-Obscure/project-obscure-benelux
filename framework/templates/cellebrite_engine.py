# --- Project Obscure Cellebrite engine ----------------------------------------
# Runs inside Cellebrite (Inseyets) Physical Analyzer, IronPython 2.7, Decoding scope.
# Reads tables with SQLiteParser (intact AND deleted records, WAL included)
# and adds the results to ds.Models.


def _obs_field(record, column):
    """(value, source) of a column in a SQLiteParser record; (None, None) if absent/NULL."""
    try:
        field = record[column]
    except Exception:
        return None, None
    value = field.Value
    if value is None or IsDBNull(value):
        return None, None
    return value, getattr(field, 'Source', None)


def _obs_ts(value):
    """Naive-UTC datetime -> Physical Analyzer TimeStamp (UTC)."""
    seconds = obs_unix_seconds(value)
    try:
        return TimeStamp(DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc).AddSeconds(seconds), True)
    except Exception:
        return TimeStamp.FromUnixTime(int(seconds))


def _obs_set(model_field, value, source=None):
    """Assign a converted value (and its source location when known) to a model Field."""
    if value is None:
        return
    if isinstance(value, _obs_dt.datetime):
        value = _obs_ts(value)
    elif isinstance(value, bool):
        value = 'Yes' if value else 'No'
    model_field.Value = value
    if source is not None:
        try:
            model_field.Source = MemoryRange(source)
        except Exception:
            pass


def _obs_text(value):
    return None if value is None else obs_format(value)


def _obs_records(db, table, deleted):
    if table not in list(db.Tables):
        return []
    if deleted:
        # Empty signature, as recommended by Cellebrite: keeps the most deleted records.
        return db.ReadTableRecords(SQLiteParser.TableSignature(table), True)
    return db[table]


def _obs_rows(db, art):
    """Yield (raw dict, sources dict, DeletedState) for every record of the artifact."""
    lookups = []
    for join in art['joins']:
        index = {}
        for rec in _obs_records(db, join['table'], False):
            key, _src = _obs_field(rec, join['foreign'])
            if key is not None and key not in index:
                index[key] = rec
        lookups.append((join, index))
    for rec in _obs_records(db, art['table'], True):
        raw = {}
        sources = {}
        joined = {}
        for join, index in lookups:
            key, _src = _obs_field(rec, join['local'])
            joined[join['as']] = index.get(key) if key is not None else None
        for field in art['fields']:
            column = field['column']
            if '.' in column:
                alias, col = column.split('.', 1)
                other = joined.get(alias)
                value, src = _obs_field(other, col) if other is not None else (None, None)
            else:
                value, src = _obs_field(rec, column)
            raw[column] = value
            sources[column] = src
        yield raw, sources, rec.Deleted


def _obs_role_source(art, sources, role):
    for field in art['fields']:
        if field.get('role') == role:
            return sources.get(field['column'])
    return None


def _obs_build(art, raw, sources, deleted):
    """Return the Physical Analyzer model for one record (chat messages are grouped later)."""
    shaped = obs_shape(art, raw)
    roles = shaped['roles']
    src = lambda role: _obs_role_source(art, sources, role)
    kind = art['type']

    if kind == 'chat':
        im = InstantMessage()
        im.Deleted = deleted
        # 'peer' is the other person in the conversation; 'outgoing' says
        # whether the device owner sent this message.
        sender = roles.get('from')
        recipient = roles.get('to')
        outgoing = roles.get('outgoing')
        peer = roles.get('peer')
        if outgoing is True:
            sender = sender if sender is not None else 'Device owner'
            recipient = recipient if recipient is not None else peer
        elif outgoing is False:
            sender = sender if sender is not None else peer
            recipient = recipient if recipient is not None else 'Device owner'
        if sender is not None:
            im.From.Value = Party.MakeFrom(_obs_text(sender), None)
        if recipient is not None:
            im.To.Add(Party.MakeTo(_obs_text(recipient), None))
        _obs_set(im.Body, _obs_text(roles.get('body')), src('body'))
        _obs_set(im.Subject, _obs_text(roles.get('subject')), src('subject'))
        _obs_set(im.TimeStamp, roles.get('timestamp'), src('timestamp'))
        _obs_set(im.SourceApplication, OBS_APP['name'])
        return im

    if kind in ('contact', 'account'):
        model = Contact() if kind == 'contact' else UserAccount()
        model.Deleted = deleted
        _obs_set(model.Name, _obs_text(roles.get('name')), src('name'))
        if kind == 'contact':
            _obs_set(model.Source, OBS_APP['name'])
        else:
            _obs_set(model.Username, _obs_text(roles.get('username')), src('username'))
            _obs_set(model.ServiceType, OBS_APP['name'])
        for role, cls in (('phone', PhoneNumber), ('email', EmailAddress), ('user_id', UserID)):
            if roles.get(role) is not None:
                entry = cls()
                entry.Deleted = deleted
                _obs_set(entry.Value, _obs_text(roles[role]), src(role))
                model.Entries.Add(entry)
        _obs_set(model.TimeCreated, roles.get('created'), src('created'))
        notes = obs_note_body(shaped['extras'])
        if roles.get('notes') is not None:
            notes = _obs_text(roles['notes']) + ('\n' + notes if notes else '')
        if notes:
            model.Notes.Add(notes)
        return model

    if kind == 'location':
        loc = Location()
        loc.Deleted = deleted
        try:
            loc.Position.Value = Coordinate(float(roles['latitude']), float(roles['longitude']))
        except (TypeError, ValueError, KeyError):
            pass
        _obs_set(loc.TimeStamp, roles.get('timestamp'), src('timestamp'))
        _obs_set(loc.Name, _obs_text(roles.get('name')), src('name'))
        description = _obs_text(roles.get('description')) or obs_note_body(shaped['extras'])
        _obs_set(loc.Description, description or None)
        _obs_set(loc.Category, OBS_APP['name'])
        return loc

    if kind == 'search':
        item = SearchedItem()
        item.Deleted = deleted
        _obs_set(item.Value, _obs_text(roles.get('value')), src('value'))
        _obs_set(item.TimeStamp, roles.get('timestamp'), src('timestamp'))
        _obs_set(item.Source, OBS_APP['name'])
        return item

    # generic: Physical Analyzer has no free-form model, so use a Note that
    # lists every field. Folder = artifact name so it is easy to filter.
    note = Note()
    note.Deleted = deleted
    _obs_set(note.Title, _obs_text(roles.get('title')) or art['name'], src('title'))
    _obs_set(note.Body, obs_note_body(shaped['columns']))
    _obs_set(note.Creation, roles.get('timestamp'), src('timestamp'))
    _obs_set(note.Source, OBS_APP['name'])
    _obs_set(note.Folder, art['name'])
    return note


def _obs_find_dbs(regex):
    seen = set()
    for fs in ds.FileSystems:
        for node in fs.Search(regex):
            path = node.AbsolutePath
            if path in seen:
                continue
            seen.add(path)
            yield node


def obs_main():
    total = 0
    for art in OBS_ARTIFACTS:
        regex = OBS_PATH_REGEX[art['id']]
        models = []
        for node in _obs_find_dbs(regex):
            try:
                db = SQLiteParser.Database.FromNode(node)
            except Exception as ex:
                print('[Project Obscure] %s: cannot open %s (%s)' % (art['id'], node.AbsolutePath, ex))
                continue
            if db is None:
                continue
            chats = {}
            for raw, sources, deleted in _obs_rows(db, art):
                model = _obs_build(art, raw, sources, deleted)
                if art['type'] != 'chat':
                    models.append(model)
                    continue
                chat_id = _obs_text(obs_shape(art, raw)['roles'].get('chat_id')) or 'unknown'
                chat = chats.get(chat_id)
                if chat is None:
                    chat = Chat()
                    chat.Id.Value = chat_id
                    chat.Source.Value = OBS_APP['name']
                    chat.Deleted = DeletedState.Deleted
                    chats[chat_id] = chat
                    models.append(chat)
                if deleted == DeletedState.Intact:
                    chat.Deleted = DeletedState.Intact
                chat.Messages.Add(model)
        if models:
            ds.Models.AddRange(models)
        total += len(models)
        print('[Project Obscure] %s / %s: %d item(s)' % (OBS_APP['id'], art['id'], len(models)))
    return total
# --- end Cellebrite engine ----------------------------------------------------
