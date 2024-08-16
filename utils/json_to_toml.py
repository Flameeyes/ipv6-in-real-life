# SPDX-FileCopyrightText: 2024 Diego Elio Pettenò
#
# SPDX-License-Identifier: 0BSD

import json
import pathlib
from collections.abc import Sequence

import click
import click_log

click_log.basic_config()


@click.command()
@click_log.simple_verbosity_option()
@click.argument(
    "input-files",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        path_type=pathlib.Path,
    ),
    required=True,
    nargs=-1,
)
def main(input_files: Sequence[pathlib.Path]):
    for file in input_files:
        json_in = json.loads(file.read_text())
        toml_out_path = file.with_suffix(".toml")
        license = file.with_suffix(".json.license").read_text().splitlines()

        with toml_out_path.open("w") as toml_out:
            toml_out.writelines(f"# {line}\n" for line in license)

            for entry in json_in:
                toml_out.write("\n")

                toml_out.write(f"[[{file.stem}]]\n")
                if "name" in entry:
                    toml_out.write(f"name = \"{entry['name']}\"\n")
                toml_out.write(f"main_host = \"{entry['main_host']}\"\n")

                if "additional_hosts" in entry:
                    toml_out.write("additional_hosts = [\n")
                    for additional_host in entry["additional_hosts"]:
                        toml_out.write(f'    "{additional_host}",\n')
                    toml_out.write("]\n")

        toml_out = {file.stem: json_in}


if __name__ == "__main__":
    main()
