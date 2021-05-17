<!--
SPDX-FileCopyrightText: 2021 Diego Elio Pettenò

SPDX-License-Identifier: 0BSD
-->

# IPv6 In Real Life

Hello! My name is [Flameeyes](https://www.flameeyes.com/) and I have [strong opinions about IPv6](https://flameeyes.blog/tag/ipv6/).

In particular, I've been arguing with many people over the years that, despite increasing adoption from the point of view of providers, there's very little interest from the point of view of end users, since outside of big tech, most of the websites people need to visit for their "daily life" do not support IPv6 at all.

Full disclosure here: both my [current](https://www.facebook.com/ipv6/) and [previous](https://www.google.com/ipv6/) employers are interested in IPv6 enough to have public trackers on adoption, and this project is totally unrelated to both, measuring a completely different metric and it is **my personal opinion, not reflecting my employer's**.

## Metric and Measurement

Finding IPv6 trackers for ISP adoption is easy (see above), and it's also very easy to find trackers that look for "Alexa Top XX" domains.
Both of these types of tracking are easy to execute in bulk, becuase they don't need manual curation at all. On the other hand, I would argue they provide a much less useful picture when it comes to "daily usage".

What I'm focusing on for this project, is to gather not just domains and sites, but whole services, and collect them by country.
This has the unfortuate effect of requiring a lot more manual work, and a lot of country specific knowledge, which is why you'll find the selection fairly biased towards the countries I have first hand knowledge of.

The reason why I'm gathering services togehter, is because it's not uncommon for many services to use different hostnames and hosting providers between their "showroom" website and the site that includes user management.
This is to be expected as, for many years now, we have been using hostnames (or domain names in some other cases) as security boundaries.
So for instance, many banks would have one domain to show off their current account offers, which would be including scripts for analytics and similar, while a completely different domain would be used for online banking, which wouldn't be loading any of that.

## Results

Generated at {{generation_timestamp.isoformat()}}

{% for country_data in source.countries_data.values() %}
# {{country_data.country_name}}

| Category | IPv6 Ready |
| --- | --- |
{%- for category in country_data.categories.values() %}
| {{category.category}} | {{category.ready_percentage}} ({{category.ready_count}} / {{category.total_count}}) |
{%- endfor %}

{% endfor %}
