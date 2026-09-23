# Trabajo Práctico Final — Gym-bro

Alejo García Mata y Gustavo Campero.

Tracker de gimnasio para grupos de amigos que se comparan de forma justa: cada uno con su rutina, rankeados por fuerza relativa al peso corporal. Backend en FastAPI con SQLite, frontend en HTML, CSS y JavaScript sin paso de build.

> En construcción. Este README va a ser el informe de la entrega; por ahora dice cómo se corre y en qué estado está.

## Cómo se ejecuta

Hace falta Python 3.11 o superior y [uv](https://docs.astral.sh/uv/).

```bash
cd tp-final
uv sync
uv run fastapi dev backend/main.py
```

Abrir `http://127.0.0.1:8000`. La documentación de la API está en `http://127.0.0.1:8000/docs`. La base `gymbro.db` se crea al arrancar; para empezar de cero alcanza con borrarla.

Tests:

```bash
uv run pytest
```

## Estado

Hecho, el corte vertical para la exposición de la idea:
- Crear un grupo y unirse con el código.
- Cargar una sesión con varias series; la respuesta trae el 1RM estimado de cada una.
- Ranking de fuerza relativa en los cuatro ejercicios de desafío.

Pendiente para la v1: pasar el ranking a DOTS con peso corporal por sesión, ranking absoluto, PRs y feed, progreso mes contra mes, ranking de la semana, gestión de desafíos y borrar sesión. Lo que viene después está en el [PRD](docs/prd.md).

## Documentos

- [pitch.md](pitch.md): la idea como se presenta en clase.
- [docs/prd.md](docs/prd.md): el PRD con el contrato completo de la API.
- [docs/grill.md](docs/grill.md): las decisiones de diseño con su porqué.
