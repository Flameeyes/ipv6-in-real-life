# SPDX-FileCopyrightText: 2021 Diego Elio Pettenò
#
# SPDX-License-Identifier: 0BSD

import importlib.resources
import itertools
import json
import tomllib
from typing import Any, Dict, Iterable, Iterator

from . import data_structures, observability


def _source_from_input(
    input_data: Iterable[Dict[str, Any]]
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


def _all_json_entities_from_package() -> Iterator[Dict[str, Any]]:
    for directory in importlib.resources.files("ipv6_in_real_life.data").glob(
        "??"
    ):
        for packed_file in directory.glob("*.json"):
            for json_entity in json.loads(packed_file.read_text()):
                json_entity.setdefault("country", directory.name)
                json_entity.setdefault("category", packed_file.stem)
                yield json_entity


def _all_toml_entities_from_package() -> Iterator[Dict[str, Any]]:
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
    return _source_from_input(
        itertools.chain(
            _all_json_entities_from_package(), _all_toml_entities_from_package()
        )
    )
