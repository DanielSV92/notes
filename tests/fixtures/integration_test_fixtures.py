# SK login responses
class SKResponseBase:
    def __init__(self, valid=True, **kwargs):
        self.valid = valid
        self.kwargs = kwargs

    def raise_for_status(self) -> None:
        return

    def status_code(self):
        return 200


class ProctorResponse:
    def __init__(self, valid=True, **kwargs):
        self.valid = valid
        self.kwargs = kwargs

    def raise_for_status(self) -> None:
        return

    def status_code(self):
        return 500


class SKLoginResponse(SKResponseBase):
    def json(self) -> dict:
        return {
            'user': {
                'id': 1,
                'is_org_admin': True,
                **self.kwargs
            },
            'token': 'dummy token',
            **self.kwargs
        } if self.valid else {
            'message': 'some message',
            'statusCode': 401
        }


class SKUserGroups(SKResponseBase):
    def json(self) -> list:
        return [
            {
                'name': 'Admin',
                **self.kwargs
            }
        ] if self.valid else {
            'message': 'some message',
            'statusCode': 401
        }


class SKTokenResponse(SKResponseBase):
    def json(self) -> dict:
        return {
            'userId': 1,
            **self.kwargs
        } if self.valid else {
            'message': 'some message',
            'statusCode': 401
        }

    incoming_webhook = {
        'ok': True,
        'incoming_webhook': {
            'channel': '#test_slack_path',
            'channel_id': 'IWASHERE',
            'url': 'daniel.is.awesome.com'
        }
    }


class SlackWebhookResponse(SKResponseBase):
    def json(self) -> dict:
        return {
            'ok': True,
            'incoming_webhook': {
                'channel': '#test_slack_path',
                'channel_id': 'IWASHERE',
                'url': 'daniel.is.awesome.com'
            },
            **self.kwargs
        } if self.valid else {
            'message': 'some message',
            'statusCode': 401
        }
