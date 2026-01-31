# Stage 1: Builder
# Uses full Python image to compile the binary
FROM python:3.11-slim as builder

WORKDIR /app

# Install build tools
RUN pip install --no-cache-dir pyinstaller

# Copy project files
COPY pyproject.toml .
COPY src/ src/
COPY catalog/ catalog/

# Install dependencies
RUN pip install .

# Build binary
# Build binary
# Must match hack/build_binaries.py logic
RUN pyinstaller --noconfirm --onefile --clean \
    --name yamlr \
    --exclude-module yamlr.pro \
    --collect-all rich \
    --add-data "src/yamlr/core/data:yamlr/core/data" \
    --add-data "catalog:Yamlr/catalog" \
    src/yamlr/__main__.py

# Stage 2: Runner
# Uses Google Distroless for maximum security (CNCF Best Practice)
# "cc" image includes basic libraries needed for Python binaries
FROM gcr.io/distroless/cc-debian12

WORKDIR /app

# Copy binary from builder
COPY --from=builder /app/dist/yamlr /usr/local/bin/yamlr

# Verify
ENTRYPOINT ["/usr/local/bin/yamlr"]
