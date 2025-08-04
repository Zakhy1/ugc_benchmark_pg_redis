FROM python:3.12-slim

ENV APP_HOME=/home/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH=/opt/venv/bin:$PATH \
    VIRTUAL_ENV=/opt/venv

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv $VIRTUAL_ENV

RUN mkdir -p /home/app && \
    echo 'app:x:1000:1000::/home/app:/bin/bash' >> /etc/passwd && \
    echo 'app:x:1000:' >> /etc/group && \
    chown 1000:1000 /home/app

WORKDIR $APP_HOME
COPY --chown=1000:1000 ./requirements.txt .

RUN . $VIRTUAL_ENV/bin/activate && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

USER 1000:1000
COPY --chown=1000:1000 . $APP_HOME
