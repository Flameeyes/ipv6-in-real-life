# SPDX-FileCopyrightText: 2021 Diego Elio Pettenò
#
# SPDX-License-Identifier: 0BSD

import asyncio
import dataclasses
import datetime
import logging
from typing import Any, Dict, Iterable, List, Optional, Sequence

import aiodns
import pycountry

_LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class Host:
    name: str
    has_ipv6_address: Optional[bool] = None

    async def resolve(self, resolver: aiodns.DNSResolver) -> None:
        try:
            all_results = await resolver.query(self.name, "AAAA")
            _LOGGER.debug(f"{self.name} resolved to {all_results!r}")
        except aiodns.error.DNSError:
            try:
                await resolver.query(self.name, "A")
            except aiodns.error.DNSError:
                _LOGGER.warning(f"{self.name} IPv4 DNS record not found either")
            self.has_ipv6_address = False
        else:
            valid_ipv6 = [
                result.host
                for result in all_results
                if not result.host.startswith("::ffff:")
            ]
            self.has_ipv6_address = bool(valid_ipv6)


@dataclasses.dataclass
class Entity:
    country: str
    category: str
    main_host: Host
    additional_hosts: Sequence[Host]
    ipv6_ready: Optional[bool] = None

    @classmethod
    def from_json(cls, json_entity: Dict[str, Any]) -> "Entity":
        return cls(
            json_entity["country"],
            json_entity["category"],
            Host(json_entity["main_host"]),
            tuple(Host(host) for host in json_entity.get("additional_hosts", [])),
        )

    async def resolve(self, resolver: aiodns.DNSResolver) -> None:
        await self.main_host.resolve(resolver)
        await asyncio.gather(
            *(host.resolve(resolver) for host in self.additional_hosts)
        )

        self.ipv6_ready = self.main_host.has_ipv6_address and all(
            host.has_ipv6_address for host in self.additional_hosts
        )


@dataclasses.dataclass
class Category:
    category: str
    entities: List[Entity] = dataclasses.field(default_factory=list)

    def register(self, entity: Entity):
        self.entities.append(entity)

    @property
    def ready_count(self) -> int:
        return sum(1 for entity in self.entities if entity.ipv6_ready)

    @property
    def total_count(self) -> int:
        return len(self.entities)

    @property
    def ready_percentage(self) -> str:
        ready_ratio = self.ready_count / self.total_count
        return f"{ready_ratio:.0%}"


@dataclasses.dataclass
class CountryData:
    country_code: str
    categories: Dict[str, Category] = dataclasses.field(default_factory=dict)

    @property
    def country_name(self):
        if self.country_code == "xx":
            return "Validation Test"

        return pycountry.countries.get(alpha_2=self.country_code).name

    def register(self, entity: Entity) -> None:
        if entity.category not in self.categories:
            self.categories[entity.category] = Category(entity.category)
        self.categories[entity.category].register(entity)


@dataclasses.dataclass
class Source:
    countries_data: Dict[str, CountryData] = dataclasses.field(default_factory=dict)
    last_resolved: Optional[datetime.datetime] = None

    def extend_from_json(self, json_entities: Iterable[Dict[str, Any]]) -> None:
        for json_entity in json_entities:
            entity = Entity.from_json(json_entity)
            if entity.country not in self.countries_data:
                self.countries_data[entity.country] = CountryData(entity.country)

            self.countries_data[entity.country].register(entity)

    async def resolve_all(self) -> None:
        resolver = aiodns.DNSResolver()

        await asyncio.gather(
            *(
                entity.resolve(resolver)
                for country in self.countries_data.values()
                for category in country.categories.values()
                for entity in category.entities
            )
        )

        self.last_resolved = datetime.datetime.now()
