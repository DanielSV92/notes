import datetime

from sqlalchemy import dialects
from sqlalchemy import event
from sqlalchemy import types
from sqlalchemy.engine import Engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.functions import FunctionElement


class CurrentTimestampMicros(FunctionElement):
    """Return the current timestamp with microsecond resolution."""
    name = 'current_timestamp_micros'


@compiles(CurrentTimestampMicros, 'sqlite')
def visit_current_timestamp_micros_sqlite(element, compiler, **kwargs):
    # Note: SQLite3 only does miliseconds, so we just pad the
    # fractional zeroes with three trailing zeroes. This is good
    # enough for our testing needs.
    return "(strftime('%Y-%m-%d %H:%M:%f000', 'now'))"


@compiles(CurrentTimestampMicros, 'mysql')
def visit_current_timestamp_micros_mysql(element, compiler, **kwargs):
    return 'CURRENT_TIMESTAMP(6)'


class DateTimeMicros(types.TypeDecorator):
    impl = types.DateTime
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'mysql':
            return dialect.type_descriptor(dialects.mysql.DATETIME(fsp=6))

        return dialect.type_descriptor(types.DateTime)

    def process_bind_param(self, value, dialect):
        if type(value) is str and dialect.name == 'sqlite':
            return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return value
