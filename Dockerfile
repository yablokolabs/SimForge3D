FROM python:3.12-slim AS base

LABEL org.opencontainers.image.title="SimForge3D" \
      org.opencontainers.image.description="Panda3D-based 3D simulation platform for AI training" \
      org.opencontainers.image.source="https://github.com/yablokolabs/SimForge3D" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
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

RUN groupadd --gid 1000 simforge \
    && useradd --uid 1000 --gid simforge --shell /bin/bash --create-home simforge

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY simforge3d ./simforge3d

RUN python -m pip install --upgrade pip && pip install .

COPY examples ./examples
COPY configs ./configs

RUN chown -R simforge:simforge /app
USER simforge

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import simforge3d; print('ok')" || exit 1

CMD ["python", "examples/random_navigation.py", "--headless", "--episodes", "3"]
