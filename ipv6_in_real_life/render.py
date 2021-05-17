# SPDX-FileCopyrightText: 2021 Diego Elio Pettenò
#
# SPDX-License-Identifier: 0BSD

import datetime

import jinja2
import pycmarkgfm

from . import data_structures


def index(source: data_structures.Source) -> str:
    jinja_env = jinja2.Environment(loader=jinja2.PackageLoader("ipv6_in_real_life"))
    template = jinja_env.get_template("index.md")

    rendered_markdown = template.render(
        source=source, generation_timestamp=datetime.datetime.now()
    )
    return pycmarkgfm.gfm_to_html(rendered_markdown)
