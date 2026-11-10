FROM debian:bookworm-slim

ARG TARGETARCH

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN case "${TARGETARCH}" in \
      "amd64") ARCH="x86_64" ;; \
      "arm64") ARCH="aarch64" ;; \
      *) echo "Unsupported architecture: ${TARGETARCH}" && exit 1 ;; \
    esac \
    && curl -fsSL "https://github.com/yamlr/yamlr/releases/download/v0.1.0/yamlr-linux-${ARCH}.tar.gz" | tar -xz -C /usr/local/bin \
    && chmod +x /usr/local/bin/yamlr \
    && /usr/local/bin/yamlr version

WORKDIR /work

ENTRYPOINT ["/usr/local/bin/yamlr"]
CMD ["--help"]
