---
name: nuevo-ranking
description: Usar cuando haya que sumar o cambiar un ranking o una estadística de Gym-bro (fuerza, progreso, semana, constancia, duelos, campañas). Lleva la regla del spec a backend/stats/ con TDD y la expone en la API.
---

# Nuevo ranking

1. **Regla.** Leé la regla en `docs/spec.md`. Si no está o es ambigua, preguntá antes de escribir código y dejá la respuesta en el spec.
2. **Test en rojo.** En `tests/test_stats.py`, un test por caso: el normal, empates, miembro sin datos, bordes de fecha (fin de mes, lunes, semana en curso). Corré `uv run pytest tests/test_stats.py` y confirmá que falla por la razón correcta. Commit `test(tp-final): ...`.
3. **Implementación.** Una función pura en el módulo que corresponda de `backend/stats/` (core, periods, rankings, competition), reexportada en `__init__.py`, que recibe `SetRecord`s y diccionarios y devuelve dataclasses. Sin imports de la base ni de FastAPI. Commit `feat(tp-final): ...` con los tests en verde.
4. **API.** La ruta solo lee con `queries.py`, llama a `stats` y serializa. Test de API para el status code nuevo si lo hay.
5. **Vista.** La tabla en el frontend, con "sin datos" al final y nunca como último puesto.
