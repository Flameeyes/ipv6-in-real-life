<!--
SPDX-FileCopyrightText: 2021 Diego Elio Pettenò

SPDX-License-Identifier: 0BSD
-->

# IPv6 In Real Life, Detailed Results

Generated based on DNS resolution at {{source.last_resolved.isoformat()}}.

{% for country_data in source.countries_data.values() %}
## {{country_data.country_name}}

{% for category in country_data.categories.values() %}

### {{category.category}}

| Main Host | Additional Host | IPv6 Ready |
| -- | -- | -- |
{%- for entity in category.entities %}
| [{{entity.main_host.name}}](https://{{entity.main_host.name}}/) |  | {{ "Yes" if entity.main_host.has_ipv6_address else "No" }} |
{%- for additional_host in entity.additional_hosts %}
|  | [{{additional_host.name}}](https://{{additional_host.name}}/) | {{ "Yes" if additional_host.has_ipv6_address else "No" }} |
{%- endfor %}
{%- endfor %}

{%- endfor %}
{%- endfor %}
