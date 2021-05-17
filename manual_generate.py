# SPDX-FileCopyrightText: 2021 Diego Elio Pettenò
#
# SPDX-License-Identifier: 0BSD

import asyncio
import pathlib
from typing import IO, Sequence

import click
import click_log
import jinja2
import pycmarkgfm

from ipv6_in_real_life import data_input

click_log.basic_config()


async def amain(input_files: Sequence[IO[str]], output_directory: pathlib.Path) -> None:

    if input_files:
        source = data_input.load_input_data(input_files)
    else:
        source = data_input.load_packaged_data()

    await source.resolve_all()

    jinja_env = jinja2.Environment(loader=jinja2.PackageLoader("ipv6_in_real_life"))
    template = jinja_env.get_template("index.md")

    rendered_markdown = template.render(source=source)

    (output_directory / "index.html").write_text(
        pycmarkgfm.gfm_to_html(rendered_markdown)
    )


@click.command()
@click_log.simple_verbosity_option()
@click.option(
    "--output-directory",
    type=click.Path(dir_okay=True, file_okay=False, exists=True, writable=True),
    default=".",
)
@click.argument(
    "input-files", type=click.File("rb", encoding="utf-8"), required=False, nargs=-1
)
def main(input_files: Sequence[IO[str]], output_directory: str) -> None:
    loop = asyncio.SelectorEventLoop()
    asyncio.set_event_loop(loop)

    asyncio.run(amain(input_files, pathlib.Path(output_directory)))


if __name__ == "__main__":
    main()
