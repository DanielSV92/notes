from unittest import TestCase

from smarty.health.views import health


class TestHealth(TestCase):
    @classmethod
    def setup_class(cls):
        cls.health = health

    def test_health(self):
        should_return = 'Server is Running!'
        returned_value = health()
        assert returned_value == should_return
