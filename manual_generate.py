# SPDX-FileCopyrightText: 2021 Diego Elio Pettenò
#
# SPDX-License-Identifier: 0BSD

import asyncio
import pathlib
from typing import IO, Sequence

import click
import click_log

from ipv6_in_real_life import data_input, observability, render

click_log.basic_config()


async def amain(
    input_files: Sequence[IO[str]], output_directory: pathlib.Path, json_only: bool
) -> None:
    # Initialize the start timestamp.
    observability.Metrics.get()

    if input_files:
        source = data_input.load_input_data(input_files)
    else:
        source = data_input.load_packaged_data()

    await source.resolve_all()

    try:
        (output_directory / "ipv6-in-real-life.json").write_text(source.as_json())
        if not json_only:
            (output_directory / "index.html").write_text(render.index(source))
            (output_directory / "details.html").write_text(render.details(source))
    finally:
        observability.Metrics.get().write_out(output_directory / "metrics.json")


@click.command()
@click_log.simple_verbosity_option()
@click.option(
    "--output-directory",
    type=click.Path(dir_okay=True, file_okay=False, exists=True, writable=True),
    default="./out",
)
@click.option("--json-only", type=bool, is_flag=True, default=False)
@click.argument(
    "input-files", type=click.File("rb", encoding="utf-8"), required=False, nargs=-1
)
def main(
    input_files: Sequence[IO[str]], output_directory: str, json_only: bool
) -> None:
    loop = asyncio.SelectorEventLoop()
    asyncio.set_event_loop(loop)

    asyncio.run(amain(input_files, pathlib.Path(output_directory), json_only))


if __name__ == "__main__":
    main()
