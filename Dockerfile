FROM python:3.9-slim-buster as base

LABEL maintainer="Bing Zhang <bing@illinois.edu>"
LABEL contributor="Puthanveetil Satheesan, Sandeep <sandeeps@illinois.edu>, Mathew, Minu <minum@illinois.edu>, Bing Zhang <bing@illinois.edu>"

# Libraries needed to run python-ldap and GitPython
RUN apt-get update && apt-get install -y \
      libldap-2.4-2 \
      libsasl2-2 \
      git \
 && rm -rf /var/lib/apt/lists/*

FROM base as requirements

# Packages needed to build python-ldap
RUN apt-get update && apt-get install -y \
      gcc \
      libldap2-dev \
      libsasl2-dev \
      libssl-dev \
 && rm -rf /var/lib/apt/lists/*

# Build and install requirements
COPY requirements.txt /app/events-manager/
RUN pip install --user --upgrade pip
RUN pip install --user -r /app/events-manager/requirements.txt
RUN chmod -R oug+r /root/.local
RUN find /root/.local -type d -exec chmod oug+x {} +

FROM base

WORKDIR /app
COPY . /app/events-manager/
RUN python -m compileall .

COPY --from=requirements /root/.local /usr/local

RUN mkdir -p /app/images /app/temp
RUN chown -R nobody:nogroup /app/images /app/temp /app/events-manager
RUN chmod -R 755 /app/images /app/temp

USER nobody

CMD ["gunicorn", "events-manager:create_app()", "--config", "/app/events-manager/gunicorn.config.py", "--timeout", "7200", "--preload"]
