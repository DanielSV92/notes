#!/usr/bin/env python3
"""Create an application instance."""
from flask.helpers import get_debug_flag

from smarty.app import create_app
from smarty.settings import DevConfig
from smarty.settings import ProdConfig

CONFIG = DevConfig if get_debug_flag() else ProdConfig

app = create_app(CONFIG())
