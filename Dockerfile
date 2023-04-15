# SPDX-FileCopyrightText: 2023 Diego Elio Pettenò
#
# SPDX-License-Identifier: 0BSD

FROM python:3

WORKDIR /app

COPY . .
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "manual_generate.py"]
