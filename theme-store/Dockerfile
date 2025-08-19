ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.19
FROM ${BUILD_FROM}

SHELL ["/bin/ash", "-o", "pipefail", "-c"]

# System deps: python, pip, and runtime tools
RUN apk add --no-cache bash tini curl jq python3 py3-pip

WORKDIR /usr/src/app

# Create a virtual environment for the app
RUN python3 -m venv /opt/venv
# Make sure venv pip/setuptools/wheel are up to date
RUN /opt/venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel

# Install only needed packages into the venv
RUN /opt/venv/bin/pip install --no-cache-dir fastapi==0.115.5 uvicorn[standard]==0.30.6 pydantic==2.8.2

# Copy our app code and runner
COPY run.sh /run.sh
COPY app /usr/src/app/app
RUN chmod +x /run.sh

# Ensure the venv is used for all subprocesses
ENV PATH="/opt/venv/bin:${PATH}"

EXPOSE 8080

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/run.sh"]
