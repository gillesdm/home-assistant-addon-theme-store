# IMPORTANT: Use a multi-arch friendly base; Supervisor will replace BUILD_FROM per arch
ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.19
FROM ${BUILD_FROM}

SHELL ["/bin/ash", "-o", "pipefail", "-c"]

# Keep dependencies minimal; no netcat needed
RUN apk add --no-cache bash tini curl jq python3

WORKDIR /usr/src/app

# Copy run.sh as the only process executor
COPY run.sh /run.sh
RUN chmod +x /run.sh

EXPOSE 8080
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/run.sh"]
