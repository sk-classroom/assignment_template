#!/bin/bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
uv venv --clear
uv pip install marimo
uv pip install -r requirements.txt