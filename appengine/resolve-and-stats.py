# SPDX-FileCopyrightText: 2021 Diego Elio Pettenò
#
# SPDX-License-Identifier: 0BSD

import asyncio
import collections
import dataclasses
import importlib.resources
import itertools
import logging
import pathlib
import json
from typing import (
    Any,
    Iterator,
    IO,
    List,
    Mapping,
    MutableMapping,
    Sequence,
)

import aiodns
import click
import click_log
import jinja2
import pycmarkgfm
import pycountry


@dataclasses.dataclass
class Host:
    name: str
    has_ipv6_address: bool


@dataclasses.dataclass
class Entity:
    country: str
    category: str
    main_host: Host
    additional_hosts: Sequence[Host]
    ipv6_safe: bool


@dataclasses.dataclass
class Category:
    category: str
    entities: List[Entity] = dataclasses.field(default_factory=list)

    @property
    def ready_percentage(self) -> str:
        ready_ratio = sum(1 for entity in self.entities if entity.ipv6_safe) / len(
            self.entities
        )
        return f"{ready_ratio:.0%}"


@dataclasses.dataclass
class CountryData:
    country_code: str
    categories: Mapping[str, Category]

    @property
    def country_name(self):
        if self.country_code == "xx":
            return "Validation Test"

        return pycountry.countries.get(alpha_2=self.country_code).name


_LOGGER = logging.getLogger(__name__)
click_log.basic_config()


async def resolve_host(resolver: aiodns.DNSResolver, host: str) -> Host:
    try:
        all_results = await resolver.query(host, "AAAA")
        _LOGGER.debug(f"{host} resolved to {all_results!r}")
    except aiodns.error.DNSError:
        return Host(host, False)
    else:
        valid_ipv6 = [
            result.host
            for result in all_results
            if not result.host.startswith("::ffff:")
        ]
        return Host(host, bool(valid_ipv6))


async def resolve_entry(
    resolver: aiodns.DNSResolver, entry: Mapping[str, Any]
) -> Entity:

    main_host = await resolve_host(resolver, entry["main_host"])
    additional_hosts = await asyncio.gather(
        *(resolve_host(resolver, host) for host in entry.get("additional_hosts", ()))
    )

    ipv6_safe = bool(
        main_host.has_ipv6_address
        and all(host.has_ipv6_address for host in additional_hosts)
    )

    return Entity(
        entry["country"], entry["category"], main_host, additional_hosts, ipv6_safe
    )


async def resolve_file(
    resolver: aiodns.DNSResolver, data: Mapping[str, Any]
) -> Sequence[Entity]:
    return await asyncio.gather(*(resolve_entry(resolver, entry) for entry in data))


async def resolve_files(
    input_data: Sequence[Mapping[str, Any]],
) -> Iterator[Entity]:
    resolver = aiodns.DNSResolver()

    all_data = await asyncio.gather(
        *(resolve_file(resolver, input_file) for input_file in input_data)
    )

    return itertools.chain(*all_data)


async def categorize_entities(
    entities: Iterator[Entity],
) -> Sequence[CountryData]:
    country_data: MutableMapping[
        str, MutableMapping[str, Category]
    ] = collections.defaultdict(dict)

    for entity in entities:
        if entity.category not in country_data[entity.country]:
            country_data[entity.country][entity.category] = Category(entity.category)
        country_data[entity.country][entity.category].entities.append(entity)

    return [
        CountryData(country, categories) for country, categories in country_data.items()
    ]


def load_input_data(input_files: Sequence[IO[str]]):
    return [json.load(input_file) for input_file in input_files]


def load_packaged_data():
    for directory in importlib.resources.files("data").glob("??"):
        for packed_file in directory.glob("*.json"):
            yield json.loads(packed_file.read_text())


async def amain(input_files: Sequence[IO[str]], output_directory: pathlib.Path) -> None:

    if input_files:
        input_data = load_input_data(input_files)
    else:
        input_data = list(load_packaged_data())

    categorized = await categorize_entities(await resolve_files(input_data))

    jinja_env = jinja2.Environment(loader=jinja2.PackageLoader("templates", "."))
    template = jinja_env.get_template("index.md")

    rendered_markdown = template.render(categorized=categorized)

    (output_directory / "index.html").write_text(pycmarkgfm.gfm_to_html(rendered_markdown))


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
