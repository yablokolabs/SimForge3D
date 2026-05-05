FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    SIMFORGE3D_HEADLESS=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libx11-6 \
    libxrandr2 \
    libxinerama1 \
    libxcursor1 \
    libxi6 \
    libxxf86vm1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY simforge3d ./simforge3d
COPY examples ./examples
COPY configs ./configs

RUN python -m pip install --upgrade pip && pip install .

CMD ["python", "examples/random_navigation.py", "--headless", "--episodes", "3"]
