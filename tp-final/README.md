# Trabajo Práctico Final — Gym-bro

Alejo García Mata y Gustavo Campero.

Tracker de gimnasio para grupos de amigos que se comparan de forma justa: cada uno con su rutina, rankeados por DOTS, progreso y constancia. Backend en FastAPI con SQLite, frontend en HTML, CSS y JavaScript sin paso de build, y login con Google por Auth0.

> En construcción. Este README va a ser el informe de la entrega; por ahora dice cómo se corre.

## Cómo se ejecuta

Hace falta Python 3.11 o superior y [uv](https://docs.astral.sh/uv/).

```bash
cd tp-final
uv sync
uv run fastapi dev backend/main.py
```

Abrir `http://127.0.0.1:8000`. Sin configurar nada, la app arranca en **modo desarrollo**: se entra con un nombre, sin Google. Sirve para probarla y para los tests.

La base `gymbro.db` se crea al arrancar. Para empezar de cero alcanza con borrarla.

Tests:

```bash
uv run pytest
```

### Login con Google (Auth0)

Auth0 tiene plan gratis y trae una conexión de Google lista para desarrollo, sin crear un proyecto en Google Cloud.

1. Crear una cuenta en [auth0.com](https://auth0.com) y un tenant.
2. **Applications → Create Application → Single Page Application.** En la configuración:
   - Allowed Callback URLs: `http://127.0.0.1:8000/`
   - Allowed Logout URLs: `http://127.0.0.1:8000/`
   - Allowed Web Origins: `http://127.0.0.1:8000`
3. **Applications → APIs → Create API** con identifier `https://gymbro/api` y algoritmo RS256.
4. **Authentication → Social → google-oauth2**: activada para la aplicación del paso 2.
5. Copiar `.env.example` a `.env` y completar `AUTH0_DOMAIN` y `AUTH0_CLIENT_ID`; `AUTH0_AUDIENCE` es el identifier del paso 3.

Con `.env` completo, la app muestra "Entrar con Google" y el backend valida el token contra el tenant.

## Documentos

- [pitch.md](pitch.md) y [pitch.html](pitch.html): la idea como se presentó en clase.
- [docs/prd.md](docs/prd.md): el producto, con releases e historias de usuario.
- [docs/grill.md](docs/grill.md): las decisiones de diseño con su porqué.
- [docs/spec.md](docs/spec.md): modelo, contrato y fórmulas.
- [docs/proceso.md](docs/proceso.md): bitácora del armado.
