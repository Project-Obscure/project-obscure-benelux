# --- Project Obscure shared runtime -------------------------------------------
# This block is copied verbatim into every generated parser (ALEAPP/iLEAPP,
# Cellebrite Physical Analyzer, ...) and is also used by the reference engine.
# It MUST stay compatible with Python 2.7 / IronPython 2.7 AND Python 3:
#   no f-strings, no type hints, no keyword-only args, no walrus, etc.
import datetime as _obs_dt

_OBS_EPOCHS = {
    'unix_s': (_obs_dt.datetime(1970, 1, 1), 1.0),
    'unix_ms': (_obs_dt.datetime(1970, 1, 1), 1000.0),
    'unix_us': (_obs_dt.datetime(1970, 1, 1), 1000000.0),
    'unix_ns': (_obs_dt.datetime(1970, 1, 1), 1000000000.0),
    'apple_s': (_obs_dt.datetime(2001, 1, 1), 1.0),
    'apple_ns': (_obs_dt.datetime(2001, 1, 1), 1000000000.0),
    'webkit_us': (_obs_dt.datetime(1601, 1, 1), 1000000.0),
}


def obs_is_timestamp(fmt):
    return fmt in _OBS_EPOCHS or fmt == 'iso'


def obs_to_text(value):
    if value is None:
        return None
    if isinstance(value, bytearray):
        value = bytes(value)
    if isinstance(value, bytes) and not isinstance(value, str):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin-1')
    return value


def obs_convert(value, fmt, values=None):
    """Convert a raw database value according to a spec field definition.

    Timestamps are returned as naive datetime objects in UTC.
    Returns None for NULL / empty / zero timestamps.
    """
    if value is None:
        return None
    if values:
        key = obs_to_text(value)
        if not isinstance(key, str):
            key = str(key)
        if key in values:
            return values[key]
    if fmt in _OBS_EPOCHS:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return obs_to_text(value)
        if number == 0:
            return None
        base, divisor = _OBS_EPOCHS[fmt]
        try:
            return base + _obs_dt.timedelta(seconds=number / divisor)
        except (OverflowError, ValueError):
            return obs_to_text(value)
    if fmt == 'iso':
        text = obs_to_text(value)
        for pattern in ('%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ',
                        '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S',
                        '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S'):
            try:
                return _obs_dt.datetime.strptime(text, pattern)
            except (TypeError, ValueError):
                pass
        return text
    if fmt == 'bool':
        try:
            return bool(int(value))
        except (TypeError, ValueError):
            return obs_to_text(value) in ('true', 'True', 'TRUE', 'yes')
    if fmt == 'int':
        try:
            return int(value)
        except (TypeError, ValueError):
            return obs_to_text(value)
    if fmt == 'float':
        try:
            return float(value)
        except (TypeError, ValueError):
            return obs_to_text(value)
    if fmt == 'hex':
        if isinstance(value, (bytes, bytearray)):
            return ''.join('%02x' % b for b in bytearray(value))
        return obs_to_text(value)
    text = obs_to_text(value)
    if text == '':
        return None
    return text


def obs_unix_seconds(dt):
    """Seconds since 1970-01-01 UTC for a naive-UTC datetime."""
    delta = dt - _obs_dt.datetime(1970, 1, 1)
    return delta.days * 86400 + delta.seconds + delta.microseconds / 1000000.0


def obs_format(value):
    """Render a converted value as text (used for notes/bodies and tests)."""
    if value is None:
        return ''
    if isinstance(value, _obs_dt.datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S') + ' UTC'
    if isinstance(value, bool):
        return 'Yes' if value else 'No'
    return obs_to_text(value) if not isinstance(value, (int, float)) else str(value)
# --- end runtime ----------------------------------------------------------------
