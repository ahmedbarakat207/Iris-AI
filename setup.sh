#!/usr/bin/env bash
# =============================================================================
# setup.sh — Iris AI One-Shot Setup
# Initialises git submodules, builds llama.cpp, and installs Python deps.
# Usage:  bash setup.sh [--no-pip] [--no-build] [--jobs N]
# =============================================================================

set -euo pipefail

# ── Colour helpers ────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${CYAN}[INFO]${RESET}  $*"; }
ok()      { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; exit 1; }
section() { echo -e "\n${BOLD}${CYAN}══ $* ══${RESET}"; }

# ── Parse flags ───────────────────────────────────────────────────────────────
SKIP_PIP=false
SKIP_SCRIPT=false

for arg in "$@"; do
  case "$arg" in
    --no-pip)   SKIP_PIP=true ;;
    --no-build|--no-script) SKIP_SCRIPT=true ;;
    -h|--help)
      echo "Usage: bash setup.sh [--no-pip] [--no-script]"
      echo ""
      echo "  --no-pip    Skip Python dependency installation"
      echo "  --no-script Skip download of the GGUF converter script"
      exit 0 ;;
  esac
done

echo -e "${BOLD}"
echo "  ╔══════════════════════════════════════════╗"
echo "  ║         Iris AI — Setup Script           ║"
echo "  ╚══════════════════════════════════════════╝"
echo -e "${RESET}"

section "Step 1/3 — Verify Environment"

if [ ! -d ".git" ]; then
  error "Run this script from the root of the Iris AI repository."
fi

if ! command -v curl &>/dev/null; then
  error "curl is required to download setup scripts."
fi

# Inform about quantization dependencies
if ! command -v llama-quantize &>/dev/null && ! command -v quantize &>/dev/null; then
  warn "llama-quantize tool not found in PATH."
  warn "If you plan to perform GGUF quantization (e.g. Q4_K_M), please install llama.cpp:"
  if [ "$(uname)" = "Darwin" ]; then
    warn "  brew install llama.cpp"
  else
    warn "  Follow instructions at https://github.com/ggerganov/llama.cpp to install or compile it."
  fi
else
  ok "llama-quantize found in PATH."
fi

section "Step 2/3 — GGUF Converter Script"

SCRIPT_DIR="$(pwd)/scripts"
mkdir -p "$SCRIPT_DIR"

if [ "$SKIP_SCRIPT" = true ]; then
  warn "--no-script passed. Skipping download of convert_hf_to_gguf.py."
else
  info "Downloading convert_hf_to_gguf.py (build b9000)..."
  curl -s -L -o "$SCRIPT_DIR/convert_hf_to_gguf.py" "https://raw.githubusercontent.com/ggerganov/llama.cpp/b9000/convert_hf_to_gguf.py"
  chmod +x "$SCRIPT_DIR/convert_hf_to_gguf.py"
  
  if [ -f "$SCRIPT_DIR/convert_hf_to_gguf.py" ]; then
    ok "convert_hf_to_gguf.py downloaded successfully to ./scripts/"
  else
    error "Failed to download convert_hf_to_gguf.py."
  fi
fi

section "Step 3/3 — Python Dependencies"

if [ "$SKIP_PIP" = true ]; then
  warn "--no-pip passed. Skipping Python installation."
else
  if ! command -v python3 &>/dev/null; then
    error "python3 not found. Please install Python 3.10+."
  fi

  PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
  info "Python ${PYTHON_VER} detected."

  info "Installing requirements..."
  python3 -m pip install --upgrade pip -q
  python3 -m pip install -r requirements.txt

  # Platform-specific extras
  if [[ "$(uname)" == "Darwin" && "$(uname -m)" == "arm64" ]]; then
    info "Apple Silicon detected — installing mlx-lm..."
    python3 -m pip install mlx-lm
  fi

  ok "Python dependencies installed."
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}  ✓ Setup complete!${RESET}"
echo ""
echo -e "  Next steps:"
echo -e "   ${CYAN}1.${RESET} Add your GGUF model files to ${BOLD}./src/models/${RESET}"
echo -e "   ${CYAN}2.${RESET} (Optional) Add training data to ${BOLD}./training/${RESET} subdirectories"
echo -e "   ${CYAN}3.${RESET} Run the app:  ${BOLD}python app.py${RESET}"
echo -e "   ${CYAN}4.${RESET} Train a role: ${BOLD}python train.py --train-role general${RESET}"
echo ""
