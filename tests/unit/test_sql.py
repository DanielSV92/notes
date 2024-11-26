from unittest import TestCase

from smarty.domain.sql import CurrentTimestampMicros
from smarty.domain.sql import DateTimeMicros


class TestDateTimeMicros(TestCase):
    def setup_class(self):
        self.dtmicros = DateTimeMicros


class TestCurrentTimestampMicros(TestCase):
    def setup_class(self):
        self.ctmicros = CurrentTimestampMicros
