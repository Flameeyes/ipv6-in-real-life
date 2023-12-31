<!--
SPDX-FileCopyrightText: 2023 Diego Elio Pettenò

SPDX-License-Identifier: 0BSD
-->

# IPv6 In Real Life (Generator)

This is the backend, generator part of [IPv6 In Real Life].
The website is project by [Flameeyes] to track the usefulness of an IPv6 network across a number
of different services and classes of sites.

For a background and details of what this project is about see [the launch blog post].

## Contributing

To contribute information for a new country or expand an existing country, edit or create the JSON
files inside `ipv6_in_real_life/data/`.

For each country there has to be a directory with the lowercase [ISO 3166-1 alpha-2] code, inside
which there has to be an empty `__init__.py` file.
Within these directories there should be one JSON file per category, according to the already
existing categories for other countries.

The format of the JSON file should follow:

```
[
    {
        "main_host": "www.someservice.example",
        "additional_hosts": [
            "users.someservice.example",
            "login.someservice.example"
        ]
    }
]
```

Include additional hosts that are necessary to make use of the service, for instance an user area
or the authentication host. If no additional hosts are necessary, omit the field.

Please follow the [REUSE] specifications, including a `.license` file next to the existing JSON
files.

## Additional Repositories

The [IPv6 In Real Life] website is rendered from the frontend available at
https://github.com/Flameeyes/ipv6-in-real-life-frontend.


[IPv6 In Real Life]: https://ipv6-in-real.life/?mtm_campaign=social&mtm_kwd=github&mtm_cid=ipv6-in-real-life
[Flameeyes]: https://flameeyes.blog/?mtm_campaign=social&mtm_kwd=github&mtm_cid=ipv6-in-real-life
[the launch blog post]: https://flameeyes.blog/2023/04/30/ipv6-in-real-life/?mtm_campaign=social&mtm_kwd=github&mtm_cid=ipv6-in-real-life
[ISO 3166-1 alpha-2]: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
[REUSE]: https://reuse.software/
