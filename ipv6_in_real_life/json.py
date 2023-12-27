# SPDX-FileCopyrightText: 2021 Diego Elio Pettenò
#
# SPDX-License-Identifier: 0BSD

import json
import time
from typing import Dict, List, Union

from . import data_structures

HostJson = Dict[str, Union[bool, str, None]]
EntityJson = Dict[str, Union[str, List[HostJson], HostJson]]
CategoryJson = List[EntityJson]
CountryDataJson = Dict[str, CategoryJson]
SourceJson = Dict[str, CountryDataJson]


def host_to_json(host: data_structures.Host) -> HostJson:
    return {
        "name": host.name,
        "has_ipv4_address": host.has_ipv4_address,
        "has_ipv6_address": host.has_ipv6_address,
    }


def entity_to_json(entity: data_structures.Entity) -> EntityJson:
    return {
        "name": entity.name,
        "main_host": host_to_json(entity.main_host),
        "additional_hosts": [host_to_json(host) for host in entity.additional_hosts],
    }


def category_to_json(category: data_structures.Category) -> CategoryJson:
    return [entity_to_json(entity) for entity in category.entities]


def country_data_to_json(country_data: data_structures.CountryData) -> CountryDataJson:
    return {
        key: category_to_json(category)
        for key, category in country_data.categories.items()
    }


def source_to_json(source: data_structures.Source) -> SourceJson:
    return {
        code: country_data_to_json(country)
        for code, country in source.countries_data.items()
    }


def generate_json(source: data_structures.Source) -> str:
    return json.dumps(
        {"results": source_to_json(source), "timestamp": int(time.time())}
    )
