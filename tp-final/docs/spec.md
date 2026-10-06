# Spec — Gym-bro

Cómo se construye lo que pide el [PRD](prd.md), con las decisiones del [grill](grill.md). Es la referencia para implementar: si el código y este archivo no coinciden, se corrige uno de los dos en el mismo PR.

## Estructura

```
tp-final/
├── backend/
│   ├── main.py        app, lifespan, seed del catálogo, estáticos
│   ├── config.py      variables de entorno y modo de auth
│   ├── auth.py        validación del token y usuario actual
│   ├── db.py          engine y sesión por request
│   ├── models.py      tablas
│   ├── schemas.py     entrada y salida de la API
│   ├── stats.py       el módulo profundo: funciones puras
│   ├── queries.py     lecturas que arman la entrada de stats
│   └── routes/        un router por recurso
├── frontend/
│   ├── index.html     una sola página; las vistas se montan por hash
│   ├── css/
│   └── js/            api, auth, router y una vista por archivo
└── tests/
```

Límites: archivos de menos de 300 líneas, funciones de menos de 50.

## Auth

- **Configuración.** `AUTH0_DOMAIN`, `AUTH0_CLIENT_ID` y `AUTH0_AUDIENCE` como variables de entorno o en `.env`. Si falta `AUTH0_DOMAIN`, el modo es `dev`.
- **Lo público.** `GET /api/config` devuelve `{"auth": "auth0" | "dev", "domain", "client_id", "audience"}`. Es lo único público de la API junto con los estáticos.
- **Frontend en modo `auth0`.** Usa `auth0-spa-js` por CDN, con `loginWithRedirect`, la conexión `google-oauth2` y `getTokenSilently` antes de cada request.
- **Frontend en modo `dev`.** Pide un nombre y usa el token `dev:<nombre>`.
- **Backend.** Lee `Authorization: Bearer <token>`.
  - En modo `auth0` valida RS256 con `PyJWKClient` sobre `https://<domain>/.well-known/jwks.json`, con audiencia e issuer, y usa `sub`.
  - En modo `dev` acepta `dev:<nombre>` y usa `sub = "dev|<nombre en minúscula>"`.
  - Sin token o con token inválido: `401`.
- **Usuario.** `current_user` busca el `User` por `sub`. Si no existe, las rutas que necesitan perfil devuelven `409` con `detail` = `"perfil incompleto"`. El frontend, al recibirlo, manda a completar el perfil.

## Datos

| Tabla | Campos | Restricciones |
|---|---|---|
| `User` | `sub`, `display_name`, `sex` (`M`/`F`), `unit` (`kg`/`lb`), `created_at` | `sub` único |
| `GoalChange` | `user_id`, `goal` (1–7), `week` (lunes desde el que rige) | único (`user_id`, `week`) |
| `Group` | `code`, `name`, `created_at` | `code` único |
| `Member` | `group_id`, `user_id`, `is_admin`, `joined_at`, `routine_id` | único (`group_id`, `user_id`) |
| `Exercise` | `name`, `bodyweight` (bool) | `name` único sin mayúsculas |
| `Challenge` | `group_id`, `exercise_id` | máximo 4 por grupo |
| `Routine` | `group_id`, `name`, `created_by` | |
| `RoutineDay` | `routine_id`, `name`, `position` | |
| `RoutineItem` | `day_id`, `exercise_id`, `sets` (1–10), `position` | |
| `WorkoutSession` | `user_id`, `date`, `bodyweight_kg`, `routine_day_id`, `created_at` | |
| `WorkSet` | `session_id`, `exercise_id`, `weight_kg`, `reps`, `position` | |
| `Reaction` | `group_id`, `set_id`, `user_id`, `kind` (`fuerza`/`fuego`/`dudoso`) | único (`group_id`, `set_id`, `user_id`) |
| `Duel` | `group_id`, `challenger_id`, `opponent_id`, `exercise_id`, `mode` (`absolute`/`dots`), `days` (3/7/14), `status` (`pending`/`active`/`rejected`), `created_at`, `start` | |
| `Campaign` | `group_id`, `name`, `start`, `end`, `tables` (JSON), `routine_id`, `winner_id`, `frozen_at` | |

- **Borrar una sesión** borra sus series y las reacciones a esas series.
- **Objetivo semanal.**
  - El primer objetivo rige desde la semana en curso.
  - Un cambio rige desde el lunes siguiente.
  - Dos cambios en la misma semana: el segundo pisa al primero.

## Validaciones

- **Serie.**
  - Reps de 1 a 50.
  - Peso de más de 0 a 500 kg. En un ejercicio de peso corporal, el peso es el lastre: puede ser 0.
- **Sesión.** Fecha no futura según el servidor, peso corporal de 30 a 300 kg y al menos una serie.
- **Perfil.** Nombre de 1 a 30 caracteres, sexo `M` o `F`, objetivo de 1 a 7 y unidad `kg` o `lb`.
- **Grupo.** Nombre de 1 a 40 caracteres.
- **Rutina.** Nombre de 1 a 40, de 1 a 7 días, de 1 a 12 ítems por día y series de 1 a 10.
- **Campaña.** Nombre de 1 a 40, `start` anterior o igual a `end`, y al menos una tabla.

Lo inválido en el body es `422`; un recurso del path que no existe es `404`.

## Módulo de estadísticas

`stats.py` no importa nada de la base ni de FastAPI. Recibe listas de `SetRecord` y diccionarios, y devuelve dataclasses.

```python
SetRecord(set_id, session_id, user_id, exercise_id, date, weight_kg, reps,
          bodyweight_kg, bodyweight_exercise, position)
load = weight_kg + (bodyweight_kg if bodyweight_exercise else 0)
```

### Fórmulas

- **1RM.** Epley: `load × (1 + reps / 30)`. Con 1 rep es `load`, y con más de 10 reps no se estima.
- **DOTS.** `x × 500 / poly(bw)`, con los coeficientes de OpenPowerlifting según el sexo, y `bw` llevado a [40, 210] en hombres y a [40, 150] en mujeres. `x` es el 1RM estimado de la serie y `bw` es el peso corporal de su sesión.

### Orden y PRs

- **Orden cronológico.** Por (`date`, `session_id`, `position`).
- **Mejor absoluto.** Es la serie con mayor (`load`, `reps`). Si empatan, gana la de fecha más temprana.
- **PRs.** Se recorren las series de cada usuario y ejercicio en orden cronológico:
  - **`weight`:** la serie supera al mejor absoluto previo, es decir más `load`, o el mismo `load` con más reps.
  - **`1rm`:** el 1RM estimado supera al mejor previo, sin ser `weight`.
  - La primera serie de un usuario en un ejercicio no es PR.
  - Varias series de una misma sesión se comparan contra lo anterior a cada una.
- **Exclusión.** Las series que el grupo marcó como dudosas se sacan de la entrada antes de calcular cualquier ranking de ese grupo.

### Períodos

Un período es un rango de meses de calendario `[from, to]`.

| Valor | Rango |
|---|---|
| `month` | el mes pedido |
| `6m` | de 5 meses antes al actual |
| `12m` | de 11 meses antes al actual |
| `all` | del mes de la primera sesión del grupo al actual |
| `custom` | `from` y `to` en formato `YYYY-MM` |

### Rankings

Todos reciben las series del período, salvo donde se aclara.

- **Fuerza, por cada desafío.**
  - **DOTS:** el mejor DOTS de cada usuario en el período, de mayor a menor.
  - **Absoluto:** el mejor absoluto de cada usuario, ordenado por (`load`, `reps`, fecha más temprana).
  - Los miembros sin datos van al final, como "sin datos".
- **Progreso.** Para cada usuario y ejercicio, el mejor 1RM del último mes del período contra el mejor del mes anterior al período: `100 × (b / a − 1)`. Se promedian los ejercicios con datos en los dos meses, y quien no tiene ninguno va como "sin datos". Con `period=month`, compara ese mes contra el anterior.
- **Semana.** Siempre la semana en curso según el servidor, no depende del período.
  - **Sesiones:** días distintos con sesión en la semana.
  - **Objetivo:** el vigente esa semana.
  - **Estado:**
    - `done` si las sesiones llegan al objetivo;
    - `out` si `objetivo − sesiones > días que quedan`, contando hoy;
    - `on` en otro caso.
  - **Orden:** por sesiones y, si empatan, por `sesiones / objetivo`.
- **Constancia.** Toma las semanas cerradas que tocan el período.
  - **Porcentaje:** semanas en que se llegó al objetivo vigente, sobre el total de semanas.
  - **Racha:** semanas cerradas seguidas cumpliendo, hacia atrás desde la última.
  - Las semanas anteriores a la primera sesión del usuario no cuentan.
  - **Orden:** por porcentaje y, si empatan, por racha.

### Stats personales

- **Por mes.** Para un usuario y un ejercicio:
  - **Mejor:** el mejor 1RM del mes.
  - **Promedio:** el promedio del mejor 1RM de cada sesión.
  - **Serie mensual:** del período, para el gráfico.
- **Por semana.** El mejor 1RM de cada semana del período.
- **Peso corporal.** El último peso de cada semana.

### Duelos

- **Plazo.** Va de `start` a `start + days − 1`. `start` es el día en que el retado acepta.
- **Resultado.** Gana la mejor serie del ejercicio dentro del plazo, en el modo del duelo.
  - Si uno no tiene series, pierde.
  - Si no las tiene ninguno, o empatan, es empate.
  - Mientras el plazo corre, el resultado es parcial.
- **Desbalance.** Compara el mejor del mes en curso de cada uno, en el modo del duelo: `|a − b| / max(a, b)`.

| Nivel | Valor |
|---|---|
| `low` | 0,10 o menos |
| `medium` | 0,25 o menos |
| `high` | más de 0,25 |
| `none` | falta un dato |

- **Sugerencias.** Los miembros ordenados por desbalance.

### Campañas

- **Tablas.** Cada una es una clave:
  - `dots:<exercise_id>`
  - `absolute:<exercise_id>`
  - `progress`
  - `consistency`
- **Período de cálculo.** Los meses que cubren [`start`, `end`], filtrando las series por fecha dentro del rango.
- **Rutina obligatoria.** Si la campaña exige una rutina, cuentan solo los miembros que la siguen.
- **Puntos.** Por posición en cada tabla: 10, 8, 6, 5, 4, 3, 2 y 1. Quien está "sin datos" no suma.
- **Orden.** Por puntos y, si empatan, por cantidad de primeros puestos.
- **Cierre.** Después de `end`, el primero se congela en `winner_id` la primera vez que alguien lee la campaña.

## Contrato

Todo bajo `/api`, con el token. Los grupos se identifican por `code`.

- **Grupo inexistente:** `404`.
- **No sos miembro:** `403`.
- **Hace falta ser admin y no lo sos:** `403`.

| Method | Path | Qué hace · respuestas |
|---|---|---|
| `GET` | `/config` | modo de auth, público |
| `GET` | `/me` | perfil, objetivo vigente, último peso corporal · `409` sin perfil |
| `PUT` | `/me` | crea o actualiza el perfil · `200` · `422` |
| `GET` | `/me/groups` | mis grupos con mi rol |
| `GET` | `/me/sessions?limit=20` | mis sesiones con series, de la más nueva a la más vieja |
| `POST` | `/me/sessions` | `201` con 1RM, DOTS y PR por serie · `422` |
| `DELETE` | `/me/sessions/{id}` | `204` · `404` si no existe o no es mía |
| `GET` | `/me/stats?exercise_id&period…` | stats personales y series para gráficos |
| `GET` | `/exercises` | catálogo |
| `POST` | `/exercises` | `201` · `409` nombre repetido · `422` |
| `POST` | `/groups` | crea, y quien lo crea queda como admin · `201` |
| `GET` | `/groups/{code}` | grupo, miembros, desafíos, rutinas y mi rol |
| `POST` | `/groups/{code}/join` | `201` · `409` si ya sos miembro |
| `DELETE` | `/groups/{code}/members/me` | salir · `204` |
| `DELETE` | `/groups/{code}/members/{user_id}` | sacar a un miembro, solo el admin · `204` · `403` · `404` |
| `PUT` | `/groups/{code}/challenges` | `{"exercise_ids": [...]}`, solo el admin · `422` si son más de 4 |
| `GET` | `/groups/{code}/last?exercise_id` | mi última serie y la de hasta 2 miembros más |
| `GET` | `/groups/{code}/rankings?period&month&from&to` | fuerza, progreso, semana y constancia |
| `GET` | `/groups/{code}/feed?limit=30` | PRs con reacciones, mi reacción y si quedó excluido |
| `PUT` | `/groups/{code}/feed/{set_id}/reaction` | `{"kind"}` · `200` · `404` si no está en el feed |
| `DELETE` | `/groups/{code}/feed/{set_id}/reaction` | `204` |
| `GET` | `/groups/{code}/routines` | rutinas con sus días e ítems, y quién sigue cada una |
| `POST` | `/groups/{code}/routines` | `201` |
| `PUT` | `/groups/{code}/routines/{id}` | reemplaza la rutina entera · `200` |
| `DELETE` | `/groups/{code}/routines/{id}` | `204`; quien la seguía queda sin rutina |
| `PUT` | `/groups/{code}/members/me/routine` | `{"routine_id": id \| null}` |
| `GET` | `/groups/{code}/duels` | duelos con su resultado o parcial |
| `GET` | `/groups/{code}/duels/suggestions?exercise_id&mode` | rivales con su desbalance |
| `POST` | `/groups/{code}/duels` | `201` · `409` si ya hay uno pendiente o activo con ese rival · `422` si te retás a vos mismo |
| `POST` | `/groups/{code}/duels/{id}/accept` | solo el retado · `403` · `409` si no está pendiente |
| `POST` | `/groups/{code}/duels/{id}/reject` | ídem |
| `GET` | `/groups/{code}/campaigns` | campañas con su tabla de posiciones |
| `POST` | `/groups/{code}/campaigns` | solo el admin · `201` · `403` · `422` |

## Frontend

Una sola página con vistas por hash, en ES modules y sin build. Primero está pensado para el celular: una columna, botones de al menos 48 px de alto, y las acciones de la carga al alcance del pulgar.

| Hash | Vista |
|---|---|
| `#/login` | login con Google, o el nombre en modo dev |
| `#/perfil` | nombre, sexo, objetivo semanal y unidad; obligatorio en el primer login |
| `#/` | mis grupos, crear grupo, unirse con código |
| `#/g/CODE/entrenar` | elegir día de rutina o carga libre |
| `#/g/CODE/carga` | carga guiada o libre, con borrador en `localStorage` |
| `#/g/CODE/rankings` | selector de período, desafíos con DOTS/absoluto, progreso, semana y constancia |
| `#/g/CODE/feed` | PRs con reacciones |
| `#/g/CODE/duelos` | duelos, retar y aceptar |
| `#/g/CODE/campanas` | campañas y su tabla |
| `#/g/CODE/grupo` | miembros, código, desafíos y rutinas (lo de admin, solo para el admin) |
| `#/stats` | mis gráficos por ejercicio, en SVG propio |

- **Polling.** Cada 30 segundos en rankings, feed y duelos, solo con la pestaña visible.
- **Libras.** Se convierten en la vista con `1 lb = 0,45359237 kg`. Lo que se manda a la API va siempre en kg.

## Tests

- **`tests/test_stats.py`.** Cada regla de arriba con casos borde, escrito antes que la función.
- **`tests/test_api.py` y siguientes.** Los status codes del contrato con el `TestClient` y una base en memoria, en modo dev.
- **Frontend.** Se prueba en el navegador con un agente que hace de usuario.
