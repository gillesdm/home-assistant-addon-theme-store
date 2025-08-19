ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.19
FROM ${BUILD_FROM}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apk add --no-cache bash tini curl jq

WORKDIR /usr/src/app
COPY run.sh /run.sh
RUN chmod +x /run.sh

EXPOSE 8080

ENTRYPOINT ["/sbin/tini", "--"]
CMD [ "/run.sh" ]