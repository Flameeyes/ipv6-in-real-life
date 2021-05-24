# SPDX-FileCopyrightText: 2021 Diego Elio Pettenò
#
# SPDX-License-Identifier: 0BSD

import asyncio
import datetime

import flask
import google.auth.exceptions
from google.cloud import storage

from ipv6_in_real_life import data_input, render


def create_app():
    app = flask.Flask(__name__)

    source = data_input.load_packaged_data()
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket("ipv6-in-real-life-homepage")
        index_blob = bucket.blob("index.html")
    except google.auth.exceptions.DefaultCredentialsError:
        pass

    def _maybe_resolve():
        if source.last_resolved is None or (
            datetime.datetime.now() - source.last_resolved
        ) > datetime.timedelta(hours=12):
            asyncio.run(source.resolve_all())

    @app.route("/")
    def index():
        _maybe_resolve()
        return render.index(source)

    @app.route("/details")
    def details():
        _maybe_resolve()
        return render.details(source)

    return app


app = create_app()
