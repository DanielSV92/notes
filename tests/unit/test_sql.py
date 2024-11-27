from unittest import TestCase

from notes.domain.sql import CurrentTimestampMicros
from notes.domain.sql import DateTimeMicros


class TestDateTimeMicros(TestCase):
    def setup_class(self):
        self.dtmicros = DateTimeMicros


class TestCurrentTimestampMicros(TestCase):
    def setup_class(self):
        self.ctmicros = CurrentTimestampMicros
