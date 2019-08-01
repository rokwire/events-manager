FROM python:3

LABEL maintainer="Bing Zhang <bing@illinois.edu>"
LABEL contributor="Siheng Pan <span14@illinois.edu>, Han Jiang <hanj2@illinois.edu>, Phoebe Tang <panqiut2@illinois.edu>, Bing Zhang <bing@illinois.edu>"

RUN apt-get update && apt-get install -y libldap2-dev libsasl2-dev libssl-dev

WORKDIR /app
COPY . /app/events-manager/
RUN pip install -r /app/events-manager/requirements.txt

CMD ["gunicorn", "events-manager:create_app()", "--config", "/app/events-manager/gunicorn.config.py"]
