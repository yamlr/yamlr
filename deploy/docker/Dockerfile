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
# Note: We use a simplified inline build command for Docker context
RUN pyinstaller --noconfirm --onefile --clean \
    --name akeso \
    --paths src \
    --add-data "catalog:akeso/catalog" \
    --collect-all rich \
    --strip \
    src/akeso/cli/main.py

# Stage 2: Runner
# Uses Google Distroless for maximum security (CNCF Best Practice)
# "cc" image includes basic libraries needed for Python binaries
FROM gcr.io/distroless/cc-debian12

WORKDIR /app

# Copy binary from builder
COPY --from=builder /app/dist/akeso /usr/local/bin/akeso

# Create alias symlink
# Distroless shell is limited, so we copy instead
COPY --from=builder /app/dist/akeso /usr/local/bin/kubecuro

# Verify
ENTRYPOINT ["/usr/local/bin/akeso"]
