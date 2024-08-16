# SPDX-FileCopyrightText: 2021 Diego Elio Pettenò
#
# SPDX-License-Identifier: 0BSD

import importlib.resources
import tomllib
from collections.abc import Iterable, Iterator
from typing import Any

from . import data_structures, observability


def _source_from_input(
    input_data: Iterable[dict[str, Any]]
) -> data_structures.Source:
    try:
        source = data_structures.Source()
        source.extend_from_input(input_data)
    except Exception as e:
        observability.Metrics.get().set_source_loaded(
            observability.LoadStatus.FAILED
        )
        raise e
    else:
        observability.Metrics.get().set_source_loaded(
            observability.LoadStatus.COMPLETED
        )
        return source


def _all_toml_entities_from_package() -> Iterator[dict[str, Any]]:
    for directory in importlib.resources.files("ipv6_in_real_life.data").glob(
        "??"
    ):
        for packed_file in directory.glob("*.toml"):
            for category, entities in tomllib.loads(
                packed_file.read_text()
            ).items():
                for toml_entity in entities:
                    toml_entity.setdefault("country", directory.name)
                    toml_entity.setdefault("category", category)
                    yield toml_entity


def load_packaged_data() -> data_structures.Source:
    return _source_from_input(_all_toml_entities_from_package())
