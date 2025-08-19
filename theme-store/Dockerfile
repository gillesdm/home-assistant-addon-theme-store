ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.19
FROM ${BUILD_FROM}

SHELL ["/bin/ash", "-o", "pipefail", "-c"]

# Minimal runtime: Python + uvicorn for FastAPI
RUN apk add --no-cache bash tini curl jq python3 py3-pip

WORKDIR /usr/src/app

# Install only needed packages
RUN pip3 install --no-cache-dir fastapi==0.115.5 uvicorn[standard]==0.30.6 pydantic==2.8.2

# Copy our files
COPY run.sh /run.sh
COPY app /usr/src/app/app
RUN chmod +x /run.sh

EXPOSE 8080
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/run.sh"]
