# Gym-bro

App web para que grupos de amigos registren lo que entrenan y se comparen de forma justa. TP final de IISAIA.

## Antes de tocar código

- El spec manda: `docs/spec.md` tiene el modelo, el contrato, las fórmulas y las vistas. Si el código se aparta del spec, se corrige uno de los dos en el mismo PR.
- El porqué de cada decisión está en `docs/grill.md`. No cambies una decisión de ahí sin preguntar.
- Cada cambio va en una branch con PR que cierra su issue. Un commit por pieza que funciona.

## Comandos

```bash
uv sync
uv run pytest
uv run fastapi dev backend/main.py   # http://127.0.0.1:8000
```

Sin `AUTH0_DOMAIN` la app corre en modo dev: login con un nombre, sin Google.

## Stack y límites

- FastAPI + SQLModel + SQLite. Frontend en HTML, CSS y JS con ES modules, sin build.
- Archivos de menos de 300 líneas, funciones de menos de 50.
- La lógica de rankings vive en `backend/stats/`, sin imports de la base ni de FastAPI.
