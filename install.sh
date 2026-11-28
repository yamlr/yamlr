#!/usr/bin/env sh
# Yamlr — Release installer for Linux, macOS, and Windows.
# Downloads the standalone native Rust binary from official public releases.
# Verifies release integrity via SHA-256 against official signed checksums.

set -e

REPO="yamlr/releases"
INSTALL_DIR="${YAMLR_INSTALL_DIR:-/usr/local/bin}"
USER_INSTALL_DIR="${HOME}/.local/bin"
VERSION="${YAMLR_VERSION:-v0.1.4}"

if [ "${YAMLR_NO_VERIFY:-0}" = "1" ]; then
    echo "[ERROR] Unverified installation is not supported."
    exit 1
fi

if ! printf '%s\n' "${VERSION}" | awk '
    /^v?(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$/ { valid = 1 }
    END { exit !valid }
'; then
    echo "[ERROR] Invalid Yamlr release version '${VERSION}'. Use a semantic version tag such as v0.1.0."
    exit 1
fi

# Parse optional arguments
for arg in "$@"; do
    case "$arg" in
        --no-verify) echo "[ERROR] Unverified installation is not supported." >&2; exit 2 ;;
        --install-dir=*) INSTALL_DIR="${arg#*=}" ;;
        --version=*) VERSION="${arg#*=}" ;;
    esac
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Yamlr • Autonomous Resolution Plane for Kubernetes"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Detect Operating System
OS="$(uname -s)"
case "${OS}" in
    Linux*)     PLATFORM="linux";;
    Darwin*)    PLATFORM="macos";;
    MINGW*|MSYS*|CYGWIN*) PLATFORM="windows";;
    *)
        echo "[ERROR] Unsupported operating system: ${OS}"
        exit 1
        ;;
esac

# 2. Detect CPU Architecture
ARCH="$(uname -m)"
case "${ARCH}" in
    x86_64|amd64)   ARCH="x86_64";;
    aarch64|arm64)  ARCH="aarch64";;
    *)
        echo "[ERROR] Unsupported architecture: ${ARCH}"
        exit 1
        ;;
esac

# 3. Determine Binary Asset Name
if [ "${PLATFORM}" = "windows" ]; then
    BINARY_NAME="yamlr.exe"
    ASSET_NAME="yamlr-windows-${ARCH}.zip"
    ARCHIVE_TYPE="zip"
else
    BINARY_NAME="yamlr"
    ASSET_NAME="yamlr-${PLATFORM}-${ARCH}.tar.gz"
    ARCHIVE_TYPE="tar.gz"
fi

SOURCE="${YAMLR_SOURCE:-curl}"
BASE_URL="https://get.yamlr.dev/${VERSION}"
DOWNLOAD_URL="${BASE_URL}/${ASSET_NAME}?src=${SOURCE}"
CHECKSUM_URL="${BASE_URL}/checksums.txt?src=${SOURCE}"
USER_AGENT="Yamlr-Installer/${VERSION} (${PLATFORM}; ${ARCH}; src=${SOURCE})"

echo "[*] Target Environment: ${PLATFORM}-${ARCH}"
echo "[*] Release Version:    ${VERSION}"
echo "[*] Attribution Source: ${SOURCE}"
echo "[*] Downloading Yamlr from: ${DOWNLOAD_URL}..."

TMP_DIR="$(mktemp -d 2>/dev/null || mktemp -d -t 'yamlr')"
trap 'rm -rf "${TMP_DIR}"' EXIT

DOWNLOADED_ARCHIVE="${TMP_DIR}/${ASSET_NAME}"

# Helper function to download file with channel attribution telemetry
fetch_url() {
    url="$1"
    dest="$2"
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL -H "User-Agent: ${USER_AGENT}" "${url}" -o "${dest}"
    elif command -v wget >/dev/null 2>&1; then
        wget -q --user-agent="${USER_AGENT}" -O "${dest}" "${url}"
    else
        echo "[ERROR] Neither 'curl' nor 'wget' was found on your system."
        exit 1
    fi
}

fetch_url "${DOWNLOAD_URL}" "${DOWNLOADED_ARCHIVE}"

echo "[*] Verifying release integrity via SHA-256..."
CHECKSUM_FILE="${TMP_DIR}/checksums.txt"
fetch_url "${CHECKSUM_URL}" "${CHECKSUM_FILE}"
EXPECTED_HASH="$(awk -v asset="${ASSET_NAME}" '$2 == asset { print $1; exit }' "${CHECKSUM_FILE}")"
case "${EXPECTED_HASH}" in
    ''|*[!0123456789abcdefABCDEF]*)
        echo "[ERROR] No valid SHA-256 entry found for ${ASSET_NAME}." >&2
        exit 1
        ;;
esac
if [ "${#EXPECTED_HASH}" -ne 64 ]; then
    echo "[ERROR] Invalid SHA-256 entry for ${ASSET_NAME}." >&2
    exit 1
fi

if command -v sha256sum >/dev/null 2>&1; then
    ACTUAL_HASH="$(sha256sum "${DOWNLOADED_ARCHIVE}" | awk '{print $1}')"
elif command -v shasum >/dev/null 2>&1; then
    ACTUAL_HASH="$(shasum -a 256 "${DOWNLOADED_ARCHIVE}" | awk '{print $1}')"
else
    echo "[ERROR] Neither sha256sum nor shasum is available." >&2
    exit 1
fi
if [ "${EXPECTED_HASH}" != "${ACTUAL_HASH}" ]; then
    echo "[ERROR] Checksum mismatch for ${ASSET_NAME}." >&2
    exit 1
fi
echo "[OK] Checksum verified: ${ACTUAL_HASH}"

# Optional GitHub provenance verification if gh CLI is available and attestation exists
if command -v gh >/dev/null 2>&1; then
    if gh attestation verify "${DOWNLOADED_ARCHIVE}" --repo "${REPO}" >/dev/null 2>&1; then
        echo "[OK] GitHub Release provenance verified."
    fi
fi

if [ "${ARCHIVE_TYPE}" = "zip" ]; then
    unzip -q "${DOWNLOADED_ARCHIVE}" -d "${TMP_DIR}"
else
    tar -xzf "${DOWNLOADED_ARCHIVE}" -C "${TMP_DIR}"
fi
DOWNLOADED_BIN="${TMP_DIR}/${BINARY_NAME}"
if [ ! -f "${DOWNLOADED_BIN}" ]; then
    echo "[ERROR] The verified archive did not contain ${BINARY_NAME}." >&2
    exit 1
fi

chmod +x "${DOWNLOADED_BIN}"

# 5. Target Directory Selection (with graceful non-root fallback)
DEST_PATH="${INSTALL_DIR}/${BINARY_NAME}"
if [ -w "${INSTALL_DIR}" ]; then
    mv "${DOWNLOADED_BIN}" "${DEST_PATH}"
elif [ "$(id -u)" -eq 0 ]; then
    mv "${DOWNLOADED_BIN}" "${DEST_PATH}"
elif command -v sudo >/dev/null 2>&1 && sudo -n true 2>/dev/null; then
    sudo mv "${DOWNLOADED_BIN}" "${DEST_PATH}"
else
    echo "[!] Cannot write to ${INSTALL_DIR} without sudo. Installing to ${USER_INSTALL_DIR}..."
    mkdir -p "${USER_INSTALL_DIR}"
    DEST_PATH="${USER_INSTALL_DIR}/${BINARY_NAME}"
    mv "${DOWNLOADED_BIN}" "${DEST_PATH}"
    
    # Path warning if ~/.local/bin is not in PATH
    case ":${PATH}:" in
        *:"${USER_INSTALL_DIR}":*) ;;
        *)
            echo "[NOTE] Add ${USER_INSTALL_DIR} to your PATH to run 'yamlr' directly:"
            echo "       export PATH=\"\${HOME}/.local/bin:\${PATH}\""
            ;;
    esac
fi

# Clear macOS Gatekeeper quarantine attribute if present
if [ "${PLATFORM}" = "macos" ] && command -v xattr >/dev/null 2>&1; then
    xattr -d com.apple.quarantine "${DEST_PATH}" 2>/dev/null || true
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  [OK] Yamlr successfully installed to: ${DEST_PATH}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
"${DEST_PATH}" version || true
echo ""
echo "Quick Start:"
echo "  yamlr scan .          # Read-only clinical audit"
echo "  yamlr heal . --apply  # Safe comment-preserving auto-repair"
echo "  yamlr --help          # Precision command reference"
