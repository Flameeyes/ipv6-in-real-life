# SPDX-FileCopyrightText: 2021 Diego Elio Pettenò
#
# SPDX-License-Identifier: 0BSD

import asyncio

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

    def index():
        asyncio.run(source.resolve_all())
        return render.index(source)

    @app.route("/force-index")
    def force_index():
        return index()

    @app.route("/regenerate-index")
    def regenerate_index():
        index_html = index()

        index_blob.upload_from_string(index_html, content_type="text/html")

        return ""

    return app


app = create_app()
