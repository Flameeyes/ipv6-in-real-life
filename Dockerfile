# SPDX-FileCopyrightText: 2023 Diego Elio Pettenò
#
# SPDX-License-Identifier: 0BSD

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY . .
RUN uv sync --no-dev
ENTRYPOINT ["uv", "run", "python", "manual_generate.py"]
