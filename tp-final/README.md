# Trabajo Práctico Final — Gym-bro

Alejo García Mata y Gustavo Campero.

Una app web para que un grupo de amigos registre lo que entrena y se compare de forma justa. Cada uno sigue su rutina o la misma que su bro, carga las series desde el celular en el gimnasio, y compite en rankings de fuerza (DOTS y absoluta), progreso, constancia, duelos y campañas. Backend en FastAPI con SQLite, frontend en HTML, CSS y JavaScript sin paso de build, y login con Google por Auth0.

## Cómo se ejecuta

Hace falta Python 3.11 o superior y [uv](https://docs.astral.sh/uv/).

```bash
cd tp-final
uv sync
uv run fastapi dev backend/main.py
```

Abrir `http://127.0.0.1:8000`. Sin configurar nada, la app arranca en **modo desarrollo**: se entra con un nombre, sin Google. La base `gymbro.db` se crea al arrancar; para empezar de cero alcanza con borrarla.

Para ver la app con datos, el script carga un grupo con tres amigos, una rutina, 8 semanas de historia y una campaña, e imprime el código del grupo:

```bash
uv run python -m scripts.seed_demo
```

Entrando como `gustavo`, `mati` o `caro` se ve el grupo desde adentro. Con cualquier otro nombre se entra como alguien nuevo y uno se une con el código.

Tests (96):

```bash
uv run pytest
```

### Login con Google (Auth0)

Auth0 tiene plan gratis y trae una conexión de Google lista para desarrollo.

1. Crear una cuenta en [auth0.com](https://auth0.com) y un tenant.
2. **Applications → Create Application → Single Page Application.** Cargar `http://127.0.0.1:8000/` como Allowed Callback URL y como Allowed Logout URL, y `http://127.0.0.1:8000` como Allowed Web Origin.
3. **Applications → APIs → Create API**, con identifier `https://gymbro/api` y RS256.
4. **Authentication → Social → google-oauth2**: activarla para la aplicación del paso 2.
5. Copiar `.env.example` a `.env` y completar `AUTH0_DOMAIN`, `AUTH0_CLIENT_ID` y `AUTH0_AUDIENCE`.

La validación del token está probada con una clave RSA generada en el test (`tests/test_auth0.py`), no contra un tenant real: crear el tenant requiere una cuenta y queda para hacer a mano.

## Arquitectura

Un solo proceso sirve la API bajo `/api` y la página desde `/`. El detalle del modelo, el contrato completo y las fórmulas están en [docs/spec.md](docs/spec.md).

```
tp-final/
├── backend/
│   ├── auth.py          token de Auth0 (JWKS) o de desarrollo → usuario
│   ├── models.py        usuarios, grupos, sesiones, series, rutinas, duelos, campañas
│   ├── queries.py       lecturas que arman la entrada de stats
│   ├── stats/           reglas de cálculo, funciones puras: core, periods, rankings, competition, personal
│   └── routes/          un router por recurso
├── frontend/
│   ├── index.html       una sola página, vistas por hash
│   └── js/              api, auth, router, una vista por archivo, gráficos en SVG propio
├── tests/               96 tests: stats con TDD y status codes de la API
├── scripts/seed_demo.py
├── docs/                pitch, PRD, grill, spec, bitácora y devolución del gym-bro
└── .claude/             reglas por path, permisos, skill nuevo-ranking y sub-agente gym-bro
```

Lo que pesa de la arquitectura:
- **Las reglas de cálculo viven solas en `backend/stats/`.** No importan la base ni FastAPI: reciben series y una fecha y devuelven tablas. Gracias a eso se pudieron escribir con TDD y cambiar después de la devolución del gym-bro sin tocar las rutas.
- **Todo lo derivable se calcula al leer.** PRs, rankings y resultados de duelos no se guardan, así borrar o cargar una sesión atrasada no deja nada inconsistente. La única excepción es el ganador de una campaña cerrada, que se congela porque es un premio.
- **Las sesiones son del usuario, no del grupo.** Con el login de Google una persona puede estar en varios grupos, y lo que entrena cuenta en todos.

## Decisiones que tomé yo

Salieron de repasar pregunta por pregunta un grill que el agente había hecho solo. El detalle está en [docs/grill.md](docs/grill.md), que arranca con lo que cambié respecto de la propuesta del agente.

**DOTS en vez de dividir por el peso corporal.** El agente propuso 1RM / peso, que favorece al liviano porque la fuerza no escala lineal con el peso. Con DOTS, el de 95 kg que sentadilla 170 le gana al de 65 que sentadilla 130. Con el ratio pasaba al revés.

**El peso corporal viaja con cada sesión.** Con el peso del perfil, bajar de peso mejoraba retroactivamente las marcas viejas.

**Progreso contra uno mismo en meses de calendario, y constancia contra un objetivo semanal propio.** Comparar contra el récord histórico deja al veterano siempre en negativo. Contar días premia al que va más, no al que cumple su plan.

**Un ranking absoluto y dos tipos de PR.** El grupo igual va a hablar de quién levanta más. Separar "PR de peso" de "PR de 1RM" hace que el feed y las tablas cuenten la misma historia.

**Ranking de la semana en lugar del "cartel de la vergüenza".** Muestra día a día quién va mejor, y marca con "ya no llega" al que perdió la semana.

**Rutinas del grupo, opcionales, con carga guiada.** La idea es que los bros sigan la misma rutina y se vean serie por serie ("la última vez: vos 80×8 · Gustavo 85×6"), pero sin obligar a nadie. Los rankings no dependen de la rutina.

**Duelos de absoluto o DOTS, libres pero con nivel de desbalance.** Un duelo de progreso en 7 días no tiene gracia. Prohibir los desparejos es rígido en un grupo chico, así que la app sugiere rivales y muestra el desbalance.

**Login con Google por Auth0.** Empecé con nickname sin contraseña. Para la app completa lo cambié: así una persona puede estar en varios grupos y nadie carga a nombre de otro. Dejé un modo desarrollo para correrla sin cuenta.

## Cómo gestioné el contexto

El orden fue: pitch → PRD → grill → repaso del grill → spec → issues. Todo quedó en disco antes de escribir código de la app completa, y el recorrido está en [docs/proceso.md](docs/proceso.md). El spec es la referencia de implementación: cuando una regla cambió, el spec cambió en el mismo PR.

El spec se partió en 12 issues de cortes verticales. Cada uno se trabajó en una branch con su PR que cierra el issue, con un commit por pieza. En el módulo de estadísticas, el commit del test en rojo va antes que el de la implementación.

La configuración del agente está versionada en `.claude/`:
- **`CLAUDE.md`:** dónde está el spec y los límites (300 líneas por archivo, 50 por función).
- **Reglas por path:** backend, frontend y tests.
- **Permisos:** push y merge piden confirmación, y `.env` no se lee.
- **La skill `nuevo-ranking`:** lleva una regla del spec al módulo de stats con TDD.
- **El sub-agente `gym-bro`:** prueba la app como un usuario real.

Cuando `stats.py` pasó las 300 líneas, lo partí en un paquete antes de seguir, y actualicé las reglas y la skill en el mismo PR.

## Qué salió mal

**Tres reglas del spec estaban mal planteadas, y las encontró el gym-bro, no los tests.**
- **Constancia:** salía siempre en "sin datos". El primer objetivo regía recién desde la semana del registro, así que las sesiones cargadas antes no contaban.
- **Progreso con 6 meses o "Todo":** comparaba contra el mes anterior al período, y en "Todo" ese mes nunca tiene datos.
- **PRs:** cada serie más pesada que la anterior contaba como PR, así que la primera sesión tiraba cuatro y llenaba el feed.

Los tests pasaban porque verificaban exactamente lo que decía el spec. El error estaba en el spec. Corregí las tres reglas con test primero y dejé el cambio anotado en el spec. Lección: un test verde dice que el código cumple la regla, no que la regla sirva.

**El campo de peso dejaba guardar 2260 kg.** Tocar el número no lo seleccionaba, así que escribir "60" sobre "22,5" daba "2260,5", y se guardaba sin aviso. Ahora el campo selecciona todo al tocarlo, un peso sospechoso pide un segundo toque y más de 500 kg se bloquea. El servidor ya rechazaba más de 500, pero el error recién aparecía al terminar la sesión, con todas las series cargadas.

**El navegador servía módulos viejos.** Sin paso de build, los archivos JS no cambian de nombre, y después de cada cambio el navegador seguía usando la versión anterior. Varias veces creí que un arreglo no andaba. Lo resolví con `Cache-Control: no-cache` en los estáticos.

**El peso corporal se pedía de nuevo en la segunda sesión del día.** El perfil quedaba cacheado en el frontend y no se refrescaba después de guardar. Lo encontró el gym-bro: con una sola sesión por prueba no aparecía.

## Prueba con el agente gym-bro

El sub-agente `gym-bro` usó la app como "Nico": primero en el gimnasio, con el celular en una mano, y después en casa, en celular y escritorio. Midió toques por serie, se equivocó a propósito y recargó la página a mitad de carga. Su devolución, con lo que se cambió y lo que quedó pendiente, está en [docs/devolucion-gym-bro.md](docs/devolucion-gym-bro.md).

## Documentos

- [pitch.md](pitch.md) y [pitch.html](pitch.html): la idea como se presentó en clase.
- [docs/prd.md](docs/prd.md): el producto, con releases e historias de usuario.
- [docs/grill.md](docs/grill.md): las decisiones con su porqué.
- [docs/spec.md](docs/spec.md): modelo, contrato y fórmulas.
- [docs/proceso.md](docs/proceso.md): bitácora del armado.
- [docs/devolucion-gym-bro.md](docs/devolucion-gym-bro.md): la prueba de punta a punta.
