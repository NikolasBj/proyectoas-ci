FROM python:3.14-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .
COPY examples ./examples

ENTRYPOINT ["python", "-m", "ruta_as_core"]
CMD ["examples/seccion_ejemplo.json"]
