from flexmock import flexmock

from smarty.domain.models import SlackIntegration
from smarty.extensions import db
from smarty.slack import controller
from tests.fixtures import unit_test_fixtures


class TestSlackController:
    def test__add_slack_integration(self):
        slack_response = unit_test_fixtures.slack_response
        slack_entry = unit_test_fixtures.slack_entry
        slack_entry_rep = unit_test_fixtures.slack_entry_rep
        current_user = unit_test_fixtures.user

        code = "8959570291.683062642213.f4a6323d5ad3fd288d35e9fe6ebee67c373d5e8827b545d92e7f4a6058244569"
        redirect_uri = "https://cerebro.ormuco.com/alerts"

        flexmock(controller).should_receive('publish_message').and_return(True)

        flexmock(controller).should_receive('oauth_access_slack')\
            .with_args(code, redirect_uri).and_return(slack_response)

        flexmock(SlackIntegration).should_receive('add').and_return(
            slack_entry)

        flexmock(db.session).should_receive('commit')

        flexmock(controller).should_receive('slack_to_dict').and_return(
            slack_entry_rep)

        response = controller.add_slack_integration(current_user, code,
                                                    redirect_uri)

        assert response['channel'] == slack_entry_rep['channel']
        assert response['channel_id'] == slack_entry_rep['channel_id']
        assert response['webhook_url'] == slack_entry_rep['webhook_url']

    def test__get_slack_entry(self):
        slack_entry = unit_test_fixtures.slack
        slack_id = slack_entry.slack_id

        flexmock(SlackIntegration).should_receive('query.get').with_args(
            slack_id).and_return(slack_entry)

        response = controller.get_slack_entry(slack_id)
        assert response == slack_entry

    def test__get_slack_entries(self):
        slack_entry = unit_test_fixtures.slack_entry_rep
        flexmock(SlackIntegration).should_receive('query.all').and_return(
            slack_entry)
        response = controller.get_slack_entries()
        assert response == slack_entry

    def test__delete_slack_entry(self):
        slack_id = 1
        slack = unit_test_fixtures.slack
        current_user = unit_test_fixtures.user

        flexmock(controller).should_receive('publish_message').and_return(True)

        flexmock(SlackIntegration).should_receive('query.get').with_args(
            slack_id).and_return(slack)
        flexmock(db.session).should_receive('commit')
        returned = controller.delete_slack_entry(current_user, slack_id)
        assert returned == unit_test_fixtures.none_response
