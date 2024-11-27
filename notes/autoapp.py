#!/usr/bin/env python3
"""Create an application instance."""
from flask.helpers import get_debug_flag

from notes.app import create_app
from notes.settings import DevConfig
from notes.settings import ProdConfig

CONFIG = DevConfig if get_debug_flag() else ProdConfig

app = create_app(CONFIG())

if __name__ == "__main__":
    app.run()