# SPDX-FileCopyrightText: 2021 Diego Elio Pettenò
#
# SPDX-License-Identifier: 0BSD

import asyncio

import flask

from ipv6_in_real_life import data_input, render


def create_app():
    app = flask.Flask(__name__)

    source = data_input.load_packaged_data()

    @app.route("/force-index")
    def force_index():
        asyncio.run(source.resolve_all())
        return render.index(source)

    return app


app = create_app()
