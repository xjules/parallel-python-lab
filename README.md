# Base environment (async only)
uv venv --python 3.12
uv pip install

# CPU acceleration
uv pip install --group numba

# GPU acceleration
uv pip install --group opencl

# Full workshop environment
uv pip install --group all --group dev
