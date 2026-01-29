#!/bin/bash
# [2026-01-21] Akeso Forge Production Build System
# Version: 4.2 (Production-Hardened, Self-Registering Identity)
# Restores: Cleanup, Pre-flight checks, and Size Analytics.

# --- OS DETECTION ---
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    PYINSTALLER_SEPARATOR=";"
    PYTHON_EXE="python"
    VENV_BIN="Scripts"
else
    PYINSTALLER_SEPARATOR=":"
    PYTHON_EXE="python3"
    VENV_BIN="bin"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# --- CLEANUP TRAP ---
LOG_FILE=$(mktemp)
cleanup() {
    local exit_code=$?
    tput cnorm 
    if [ "$exit_code" -ne 0 ] && [ "$exit_code" -ne 130 ]; then
        echo -e "\n\033[31m💥 Build failed. See logs at: $LOG_FILE\033[0m"
    fi
    rm -f "$LOG_FILE"
    exit "$exit_code"
}
trap cleanup EXIT INT TERM

spinner() {
    local pid="$1"
    local delay=0.1
    local spinstr='|/-\\'
    tput civis 
    while ps -p "$pid" > /dev/null 2>&1; do
        local temp="${spinstr#?}"
        printf " [%c] " "$spinstr"
        spinstr="$temp${spinstr%"$temp"}"
        sleep "$delay"
        printf "\b\b\b\b\b"
    done
    wait "$pid"
    return "$?"
}

echo -e "\033[1;35m🧬 Akeso Forge Build System\033[0m"
echo "--------------------------------------"

# 1. Pre-flight Checks (RESTORED)
echo -n "🔍 Verifying System Dependencies..."
MISSING_TOOLS=()
! command -v $PYTHON_EXE &> /dev/null && MISSING_TOOLS+=("python3")
! command -v patchelf &> /dev/null && MISSING_TOOLS+=("patchelf")
! command -v strip &> /dev/null && MISSING_TOOLS+=("binutils")

if [ ${#MISSING_TOOLS[@]} -ne 0 ]; then
    echo -e "[\033[33m${MISSING_TOOLS[*]} MISSING\033[0m]"
    sudo apt-get update && sudo apt-get install -y python3-full python3-venv python3-pip python3-dev patchelf binutils musl-tools
else
    echo -e "[DONE]"
    sudo -v &>/dev/null
fi

# 2. Cleaning (RESTORED)
echo -n "🧹 Purging old build artifacts..."
rm -rf build/ dist/ *.spec src/*.egg-info > /dev/null 2>&1
echo -e "[DONE]"

# 3. Environment Setup
VENV_DIR="$SCRIPT_DIR/.venv_build"
VP_PYINSTALLER="$VENV_DIR/$VENV_BIN/pyinstaller"
VP_STATICX="$VENV_DIR/$VENV_BIN/staticx"

echo -n "🌐 Preparing Build Sandbox..."
{
    rm -rf "$VENV_DIR"
    $PYTHON_EXE -m venv "$VENV_DIR"
    source "$VENV_DIR/$VENV_BIN/activate"
    pip install --upgrade pip setuptools wheel pyinstaller staticx
    pip install -r "$SCRIPT_DIR/requirements.txt"
} > "$LOG_FILE" 2>&1 &
spinner "$!" || { echo -e "[\033[31mFAIL\033[0m]"; cat "$LOG_FILE"; exit 1; }
echo -e "[DONE]"

# 4. Build Primary Binary
echo -n "🐍 Compiling 'kubecuro' (Identity-Aware)..."
{
    source "$VENV_DIR/$VENV_BIN/activate"
    # We explicitly include the 'src' path and the 'akeso' package root
    export PYTHONPATH="$SCRIPT_DIR/src"
    
    "$VP_PYINSTALLER" --onefile --clean --name kubecuro \
                --paths "$SCRIPT_DIR/src" \
                --add-data "$SCRIPT_DIR/catalog${PYINSTALLER_SEPARATOR}akeso/catalog" \
                --collect-all rich \
                --collect-all ruamel.yaml \
                --hidden-import akeso.models \
                --hidden-import akeso.core.models \
                --hidden-import akeso.core.pipeline \
                --hidden-import akeso.parsers.lexer \
                --hidden-import akeso.ui.formatter \
                --strip \
                "$SCRIPT_DIR/src/akeso/cli/main.py"
} > "$LOG_FILE" 2>&1 &
spinner "$!" || { echo -e "[\033[31mFAIL\033[0m]"; cat "$LOG_FILE"; exit 1; }
echo -e "[DONE]"

# 5. Hardening (StaticX)
if [ -f "$VP_STATICX" ]; then
    echo -n "🛡️  Hardening to Static Binary..."
    {
        "$VP_STATICX" --strip --tmpdir /tmp dist/kubecuro dist/kubecuro_static
        mv dist/kubecuro_static dist/kubecuro
    } > "$LOG_FILE" 2>&1 &
    spinner "$!" && echo -e "[DONE]" || echo -e "[SKIPPED]"
fi

# 6. Global Deployment & Self-Registration
echo -n "🚚 Installing to /usr/local/bin..."
if sudo cp dist/kubecuro /usr/local/bin/kubecuro && sudo chmod +x /usr/local/bin/kubecuro; then
    # Manually create the symlink via sudo so the binary doesn't have to fight permissions
    sudo ln -sf /usr/local/bin/kubecuro /usr/local/bin/akeso
    INSTALLED=true
    echo -e "[DONE]"
else
    echo -e "[\033[33mSKIPPED\033[0m]"
fi

# 7. Size Analytics (RESTORED)
FINAL_SIZE_HUMAN=$(du -h "dist/kubecuro" | cut -f1)

echo "--------------------------------------"
echo -e "✅ \033[1;32mBuild & Deployment Complete!\033[0m"
echo -e "📦 Final Size: \033[1;33m$FINAL_SIZE_HUMAN\033[0m"
if [ "$INSTALLED" = true ]; then
    echo -e "🚀 Commands: \033[1;32mkubecuro, akeso\033[0m"
fi
echo "--------------------------------------"