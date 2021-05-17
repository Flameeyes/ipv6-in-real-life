# SPDX-FileCopyrightText: 2021 Diego Elio Pettenò
#
# SPDX-License-Identifier: 0BSD

import importlib.resources
import itertools
import json
from typing import IO, Any, Dict, Iterable, Iterator, Sequence

from . import data_structures


def _source_from_json(json_data: Iterable[Dict[str, Any]]) -> data_structures.Source:
    source = data_structures.Source()
    source.extend_from_json(json_data)
    return source


def load_input_data(input_files: Sequence[IO[str]]) -> data_structures.Source:
    return _source_from_json(
        itertools.chain(*(json.load(input_file) for input_file in input_files))
    )


def _all_json_entities_from_package() -> Iterator[Dict[str, Any]]:
    for directory in importlib.resources.files("ipv6_in_real_life.data").glob("??"):
        for packed_file in directory.glob("*.json"):
            for json_entity in json.loads(packed_file.read_text()):
                json_entity.setdefault("country", directory.name)
                json_entity.setdefault("category", packed_file.stem)
                yield json_entity


def load_packaged_data() -> data_structures.Source:
    return _source_from_json(_all_json_entities_from_package())
