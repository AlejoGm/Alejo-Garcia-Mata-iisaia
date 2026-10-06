---
paths:
  - "backend/**/*.py"
---

# Backend

- Cada endpoint declara `response_model` y `status_code`.
- El path identifica y el body transporta: lo que ya está en el path no se repite en el body.
- `404` si el recurso del path no existe, `403` si existe pero no te corresponde, `422` si el body es inválido, `409` si choca con el estado actual.
- El usuario sale del token (`current_user`), nunca del body ni del path.
- Si una regla de cálculo cambia, cambia en `stats.py` con su test, no en la ruta.
