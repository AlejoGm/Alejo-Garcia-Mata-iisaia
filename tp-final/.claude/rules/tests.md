---
paths:
  - "tests/**/*.py"
  - "backend/stats/**/*.py"
---

# Tests

- `backend/stats/` se escribe con TDD: el test en rojo va en su propio commit antes que la implementación.
- Los tests miran comportamiento, no implementación: dadas estas series y esta fecha, qué ranking sale.
- Los tests de API usan el modo dev de auth y una base en memoria (fixtures en `tests/conftest.py`).
- Cada status code del contrato tiene al menos un test.
