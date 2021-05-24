# SPDX-FileCopyrightText: 2021 Diego Elio Pettenò
#
# SPDX-License-Identifier: 0BSD

import cmarkgfm
import jinja2

from . import data_structures


def _render(source: data_structures.Source, template: str) -> str:
    jinja_env = jinja2.Environment(loader=jinja2.PackageLoader("ipv6_in_real_life"))
    template = jinja_env.get_template(template)

    rendered_markdown = template.render(source=source)
    return cmarkgfm.github_flavored_markdown_to_html(rendered_markdown)


def index(source: data_structures.Source) -> str:
    return _render(source, "index.md")


def details(source: data_structures.Source) -> str:
    return _render(source, "details.md")
