FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY pyproject.toml README.md CHANGELOG.md LICENSE ./
COPY agents ./agents
COPY analytics ./analytics
COPY benchmarks ./benchmarks
COPY cli ./cli
COPY dashboard ./dashboard
COPY events ./events
COPY examples ./examples
COPY exporters ./exporters
COPY memory ./memory
COPY reports ./reports
COPY runtime ./runtime
COPY scripts ./scripts
COPY tools ./tools
COPY visualization ./visualization
COPY runtime-search runtime-inspect ./
COPY tests ./tests

RUN python -m pip install --upgrade pip && \
    python -m pip install -e . pytest pytest-cov mypy ruff

CMD ["python", "examples/multi_agent_demo.py"]
