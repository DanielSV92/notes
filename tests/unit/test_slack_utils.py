from unittest import TestCase

from flexmock import flexmock

from smarty.slack import utils
from tests.fixtures import unit_test_fixtures


class TestSlackUtils(TestCase):
    def setup_class(self):
        self.utils = utils

    def test_slack_to_dict(self):
        should_return = unit_test_fixtures.slack_dict
        slack_entry = unit_test_fixtures.slack

        returned = self.utils.slack_to_dict(slack_entry)

        assert returned == should_return

    def test_generate_slack_severity_color(self):
        # critical severity
        severity = 'critical'
        text_critical = '#fff'
        background_critical = '#f44242'

        color_background, color_text = self.utils.generate_slack_severity_color(
            severity)

        assert color_background == background_critical
        assert color_text == text_critical

        #  high severity
        severity = 'high'
        text_high = '#fff'
        background_high = '#ff5a00'

        color_background, color_text = self.utils.generate_slack_severity_color(
            severity)

        assert color_background == background_high
        assert color_text == text_high

        # medium seveity
        severity = 'medium'
        text_medium = '#fff'
        background_medium = '#ffa600'

        color_background, color_text = self.utils.generate_slack_severity_color(
            severity)

        assert color_background == background_medium
        assert color_text == text_medium

        #  low severity
        severity = 'low'
        text_low = '#3c3c3c'
        background_low = '#fdc900'

        color_background, color_text = self.utils.generate_slack_severity_color(
            severity)

        assert color_background == background_low
        assert color_text == text_low

        #  healthy severity
        severity = 'healthy'
        text_healthy = '#fff'
        background_healthy = '#00b100'

        color_background, color_text = self.utils.generate_slack_severity_color(
            severity)

        assert color_background == background_healthy
        assert color_text == text_healthy

        # unknown severity
        severity = 'unknown'
        text_unknown = '#fff'
        background_unknown = '#909090'

        color_background, color_text = self.utils.generate_slack_severity_color(
            severity)

        assert color_background == background_unknown
        assert color_text == text_unknown
