# Ejercicio E2E: proyecto Python + Docker en VS Code

Este ejercicio junta todo:

- VS Code (layout + terminal + shortcuts)
- Python (entorno virtual + dependencias)
- Docker (imagen reproducible)

La meta no es “aprender FastAPI” ni “aprender una librería”. La meta es dominar el **flujo de trabajo**.

---

::::exercise{title="E2E: construir, ejecutar y debuggear (Python + Docker)" difficulty="4"}

## Parte A — Crear el proyecto (local)

1. Crea el directorio del proyecto y ábrelo en VS Code:

```bash
mkdir -p ~/e2e_ide_python_docker
cd ~/e2e_ide_python_docker
code .
```

2. Crea un entorno virtual e instala dependencias:

```bash
uv venv
source .venv/bin/activate
uv pip install requests pytest
uv pip freeze > requirements.txt
```

3. Crea esta estructura:

```
e2e_ide_python_docker/
├── src/
│   └── app.py
├── tests/
│   └── test_app.py
└── requirements.txt
```

4. Crea `src/app.py`:

```python
import os
import requests


def normalize_name(name: str) -> str:
    return " ".join(name.strip().split())


def main() -> None:
    name = normalize_name(os.getenv("NAME", "mundo"))
    ip = requests.get("https://httpbin.org/ip", timeout=10).json()["origin"]
    print(f"Hola, {name}. Tu IP pública es: {ip}")


if __name__ == "__main__":
    main()
```

5. Crea `tests/test_app.py`:

```python
from src.app import normalize_name


def test_normalize_name():
    assert normalize_name("  ana   garcia  ") == "ana garcia"
```

6. Corre local:

```bash
python src/app.py
pytest -q
```

Si `python src/app.py` falla por falta de internet/DNS (porque usa `https://httpbin.org/ip`), no es un error “de Python”: es conectividad. Para seguir el ejercicio, puedes:
- Reintentar en otra red, o
- Cambiar temporalmente la línea del request por un string fijo (solo para el ejercicio).

Si `pytest` falla con import errors, asegúrate de ejecutar desde la raíz del proyecto y de que estás usando el Python de tu `.venv` (ver sección de Python en VS Code).

---

## Parte B — Dockerizar (reproducible)

1. Crea `.dockerignore`:

```dockerignore
.venv
__pycache__/
*.pyc
.pytest_cache/
.mypy_cache/
.ruff_cache/
.git/
.vscode/
```

2. Crea `Dockerfile` (optimizado por capas):

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Dependencias primero (mejor cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código después
COPY src/ src/
COPY tests/ tests/

ENV PYTHONUNBUFFERED=1
CMD ["python", "src/app.py"]
```

3. Construye y ejecuta:

```bash
docker build -t e2e-ide:latest .
docker run --rm -e NAME="VS Code" e2e-ide:latest
```

4. Corre tests dentro del contenedor:

```bash
docker run --rm e2e-ide:latest pytest -q
```

> Conexión con el módulo de contenedores: fíjate que copiamos `requirements.txt` antes que el código para aprovechar el cache de build.

---

## Parte C — Docker Compose (workflow de dev)

1. Crea `docker-compose.yml`:

```yaml
services:
  app:
    build: .
    environment:
      - NAME=compose
    volumes:
      - .:/app
    command: python src/app.py
```

2. Ejecuta:

```bash
docker compose run --rm app
docker compose run --rm app pytest -q
```

---

## Parte D — Hacerlo desde la IDE (lo importante)

1. Abre la terminal integrada (``Ctrl+` `` / ``Cmd+` ``) y corre tus comandos ahí.
2. Instala la extensión **Docker** si no la tienes.
3. Desde VS Code, verifica que puedes:
   - ver imágenes
   - ver contenedores corriendo
   - abrir logs de un contenedor

No tienes que “clicar todo”. Lo esencial es que entiendas que VS Code te da *UI*, pero la verdad está en los comandos.

---

## Parte E (opcional) — Dev Containers

Si quieres el nivel “pro”, usa la extensión **Dev Containers** para abrir el proyecto dentro del contenedor y que todo (Python, dependencias) viva ahí.

Eso reduce el clásico problema:

> “en mi máquina funciona”

Si lo intentas, documenta:
- qué fue fácil
- qué fue difícil
- y qué parte te pareció más útil para reproducibilidad

::::

