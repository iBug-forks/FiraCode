FROM python:3.12

WORKDIR /opt

# unused transitive deps without arm64 wheels
ARG TARGETARCH
RUN if [ "$TARGETARCH" = "arm64" ]; then \
        for stub in "resvg-cli 0.44.0" "opentype-sanitizer 9.2.0" "pngquant-cli 3.0.3"; do \
            set -- $stub && \
            mkdir -p /tmp/stub && \
            printf '[project]\nname = "%s"\nversion = "%s"\n' "$1" "$2" > /tmp/stub/pyproject.toml && \
            pip install /tmp/stub && \
            rm -rf /tmp/stub; \
        done; \
    fi

COPY requirements.txt .
COPY script/bootstrap_linux.sh script/
RUN script/bootstrap_linux.sh
