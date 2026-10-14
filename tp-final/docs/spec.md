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
│   ├── schemas/       entrada y salida de la API, un módulo por recurso
│   ├── stats/         el módulo profundo: funciones puras (core, periods, rankings, competition)
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

- **Configuración.** `AUTH0_DOMAIN`, `AUTH0_CLIENT_ID` y `AUTH0_AUDIENCE` como variables de entorno o en `.env`. Si falta `AUTH0_DOMAIN`, el modo es `local` (usuario y contraseña). `GYMBRO_AUTH=dev` fuerza el modo `dev`, que usan los tests y los scripts de datos.
- **Lo público.** `GET /api/config` devuelve `{"auth": "auth0" | "local" | "dev", "domain", "client_id", "audience"}`. Es lo único público de la API junto con los estáticos y las rutas de `/api/auth`.
- **Frontend en modo `auth0`.** Usa `auth0-spa-js` por CDN, con `loginWithRedirect`, la conexión `google-oauth2` y `getTokenSilently` antes de cada request.
- **Frontend en modo `local`.** "Entrar" o "Crear cuenta" con usuario y contraseña; guarda el token de sesión y lo manda en cada request. "Cerrar sesión" lo invalida en el servidor.
- **Frontend en modo `dev`.** Pide un nombre y usa el token `dev:<nombre>`.
- **Backend.** Lee `Authorization: Bearer <token>`.
  - En modo `auth0` valida RS256 con `PyJWKClient` sobre `https://<domain>/.well-known/jwks.json`, con audiencia e issuer, y usa `sub`.
  - En modo `local` busca el token en `AuthToken` (se guarda su sha256, no el token) y usa su `sub`. Los tokens `dev:` dan `401`.
  - En modo `dev` acepta `dev:<nombre>` y usa `sub = "dev|<nombre en minúscula>"`.
- **Cuentas locales.**
  - `POST /api/auth/register {username, password}`: usuario de 3 a 30 caracteres `[a-z0-9._-]` (se pasa a minúscula) y contraseña de 6 a 128. `201` con `{token}` · `409` si el usuario existe · `422`.
  - `POST /api/auth/login`: `200` con `{token}` · `401` si el usuario o la contraseña no coinciden, sin decir cuál.
  - `POST /api/auth/logout`: borra el token · `204`.
  - La contraseña se guarda con scrypt y sal propia en `Credential`. El `sub` de una cuenta local es `dev|<usuario>`, el mismo del modo `dev`: registrarse con un nombre que ya tenía historia se queda con ese usuario.
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
| `Credential` | `username` (minúscula), `sub`, `password_hash`, `created_at` | `username` y `sub` únicos |
| `AuthToken` | `token_hash`, `sub`, `created_at` | `token_hash` único |
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

`backend/stats/` no importa nada de la base ni de FastAPI. Recibe listas de `SetRecord` y diccionarios, y devuelve dataclasses.

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
- **PRs.** Se comparan contra las sesiones anteriores del usuario en ese ejercicio, a lo sumo uno por ejercicio y sesión (cambio por la devolución del gym-bro):
  - **`weight`:** la serie más pesada de la sesión tiene más `load` que el mejor absoluto previo.
  - **`reps`:** la serie más pesada tiene el mismo `load` que el mejor absoluto previo, con más reps (separado de `weight` en la quinta pasada).
  - **`1rm`:** si no hubo PR de peso ni de reps, el mejor 1RM estimado de la sesión supera al mejor previo.
  - La primera sesión de un usuario en un ejercicio es la línea base y no tiene PRs.
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
- **Progreso.** `100 × (b / a − 1)` por ejercicio, promediado entre los ejercicios con datos en los dos meses. Quien no tiene ninguno va como "sin datos".
  - Con `period=month`: el mejor 1RM de ese mes contra el del mes anterior.
  - Con un período de varios meses: el primer mes con datos del período contra el último.
- **Semana.** Siempre la semana en curso según el servidor, no depende del período.
  - **Días:** días distintos con sesión en la semana. Dos sesiones el mismo día cuentan como un día.
  - **Objetivo:** el vigente esa semana.
  - **Estado:**
    - `done` si las sesiones llegan al objetivo;
    - `out` si `objetivo − sesiones > días que quedan`, contando hoy;
    - `on` en otro caso.
  - **Orden:** por sesiones y, si empatan, por `sesiones / objetivo`.
- **Constancia.** Toma las semanas cerradas que tocan el período.
  - **Porcentaje:** semanas en que se llegó al objetivo vigente, sobre el total de semanas. El primer objetivo rige también para las semanas anteriores a fijarlo, así cuentan las sesiones cargadas hacia atrás.
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

### Panel del grupo

- **Volumen:** suma de `load × reps` de las series. Sin las dudosas del grupo.
- **Sesiones:** pares distintos (usuario, fecha).
- **Serie de 8 semanas:** sesiones y volumen por semana de lunes a domingo, de la más vieja a la actual (incluida, aunque esté en curso).
- **Días de la semana en curso:** para cada día de lunes a domingo, cuántos miembros distintos entrenaron.
- **Objetivo del grupo:** `Σ min(días_u, objetivo_u) / Σ objetivo_u`, sobre los miembros con objetivo vigente. Sin objetivos, no hay valor.
- **PRs del mes:** series con PR (según la regla de PRs) con fecha en el mes en curso; también los del mes anterior, para comparar.
- **Mejor racha:** el miembro con la racha de constancia más larga.
- **Líderes:** el primero en DOTS de cada desafío, en el mes en curso.
- **Semana pasada:** ver más arriba.
- **Medallas recientes:** las de los miembros ganadas en los últimos 14 días, de la más nueva a la más vieja.

### Objetivo para PR

Sobre el historial del usuario en un ejercicio sin peso corporal. Con `(L, R)` el mejor absoluto, `M` el mejor 1RM estimado y `s` el salto (2,5 kg, o 5 lb en kg si el perfil está en libras):
- **Más reps:** `(L, R + 1)`, si `R + 1 ≤ 50`.
- **Más peso:** `(L + s, r)`, con `r` la menor cantidad de reps entre 1 y 10 cuyo 1RM estimado supera a `M`. Siempre hay una, porque con 10 reps la carga más pesada supera cualquier 1RM de una carga menor. Si no hay `M` (todas las series tienen más de 10 reps), `r = R`.
- Sin historial, o en ejercicios con tu peso, no hay objetivo.

### Medallas

Personales, sobre todo el historial del usuario. Cada una tiene el día en que se ganó: el primero en que se cumple la condición.

| Clave | Condición | Día |
|---|---|---|
| `first` | una sesión | el de la primera sesión |
| `sessions_10`, `sessions_50`, `sessions_100` | días distintos entrenados | el día número N |
| `streak_4`, `streak_12` | semanas cerradas seguidas que cumplen el objetivo vigente | el domingo de la semana N de la racha |
| `prs_10` | PRs según la regla de PRs | el del PR número 10 |
| `bench_bw` | press banca con `load ≥ bw` | el de la serie |
| `squat_1_5` | sentadilla con `load ≥ 1,5 × bw` | ídem |
| `deadlift_2` | peso muerto con `load ≥ 2 × bw` | ídem |
| `ton` | `Σ load × reps ≥ 10 000` en una sesión | el de la sesión |

`bw` es el peso corporal de la sesión de la serie.

### Cara a cara

Entre dos miembros, en los ejercicios que hicieron los dos dentro de los últimos 6 meses de calendario, sin las series dudosas del grupo:
- el mejor 1RM estimado de cada uno, en kg;
- el mejor DOTS de cada uno, y gana el mayor;
- el marcador: cuántos ejercicios gana cada uno.

Ejercicios con 1RM en uno solo de los dos no entran.

### Semana pasada

Para la última semana cerrada (lunes a domingo), sin las series dudosas:
- **Más días:** los miembros con más días entrenados.
- **Más volumen:** los de mayor volumen.
- **Más PRs:** los de más PRs con fecha en esa semana.
- **Objetivo cumplido:** los que llegaron a su objetivo vigente.

Cada premio lista a todos los empatados en el máximo, y queda vacío si el máximo es 0.

### Calendario

Los días con series de las últimas 26 semanas, de lunes a la semana en curso, con la cantidad de series de cada día.

### Series por músculo

Cada ejercicio del catálogo tiene un músculo principal (`MUSCLES` en `backend/catalog.py`); los que agrega un usuario cuentan como "Otros". Para cada músculo:
- **Promedio:** series de las últimas 4 semanas cerradas, dividido 4, con un decimal.
- **Esta semana:** series de lunes a hoy.

Ordenados por promedio y después por esta semana. Un músculo sin series en ese rango no aparece.

### Posición en vivo

Para una serie todavía no guardada (ejercicio, peso, reps y peso corporal del día):
- **PR:** el que daría según la regla de PRs contra el historial guardado del usuario.
- **Valor:** el DOTS del 1RM estimado de la serie. Con más de 10 reps no hay valor, ni posición.
- **Posición:** sobre el mejor DOTS del mes en curso de cada miembro en ese ejercicio, sin las series dudosas. Mi valor es el mayor entre mi mejor del mes y el de la serie. La posición es 1 más la cantidad de miembros con un valor estrictamente mayor, así que un empate comparte el lugar. También se devuelve la posición antes de la serie (vacía si no tenía valor).
- **A quién pasé:** los miembros cuyo valor era mayor o igual que el mío antes de la serie y queda por debajo del de la serie.
- **El siguiente:** el miembro con el menor valor que siga por encima del mío. Para pasarlo, a mis mismas reps: el 1RM que hace falta es `dots_siguiente × poly(bw) / 500`, y el peso es `1RM / (1 + reps / 30)` (igual al 1RM con 1 rep), redondeado hacia arriba al salto de discos (2,5 kg o 5 lb) hasta superarlo. En ejercicios con tu peso no se calcula el peso.

### Comparar en el panel

Para un ejercicio y un período, sin las series dudosas del grupo:
- **Fuerza por mes:** para cada miembro y cada mes del período, el mejor 1RM estimado, o su DOTS (`metric = 1rm | dots`). Sin dato ese mes, `null`.
- **Días por semana:** para cada miembro, los días distintos entrenados en cada una de las últimas 12 semanas, de la más vieja a la actual.
- **Ejercicios:** los que tienen 1RM estimable en el grupo, del más cargado al menos. Si no se pide uno, el primero.

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
| `GET` | `/me/stats?exercise_id&period…` | stats personales, series para gráficos, calendario, medallas y series por músculo |
| `GET` | `/exercises` | catálogo, con `barbell` según el catálogo |
| `POST` | `/exercises` | `201` · `409` nombre repetido · `422` |
| `POST` | `/groups` | crea, y quien lo crea queda como admin · `201` |
| `GET` | `/groups/{code}` | grupo, miembros, desafíos, rutinas y mi rol |
| `POST` | `/groups/{code}/join` | `201` · `409` si ya sos miembro |
| `DELETE` | `/groups/{code}/members/me` | salir · `204` |
| `DELETE` | `/groups/{code}/members/{user_id}` | sacar a un miembro, solo el admin · `204` · `403` · `404` |
| `PUT` | `/groups/{code}/challenges` | `{"exercise_ids": [...]}`, solo el admin · `422` si son más de 4 |
| `GET` | `/groups/{code}/last?exercise_id` | mi última serie, la de hasta 2 miembros más y mi objetivo para PR |
| `POST` | `/groups/{code}/standing` | `{exercise_id, weight_kg, reps, bodyweight_kg}`: PR, posición antes y después, a quién pasé y la serie para pasar al siguiente, sin guardar nada · `200` · `422` |
| `GET` | `/groups/{code}/compare?exercise_id&metric&period` | líneas por miembro: fuerza por mes y días por semana · `422` con métrica o período inválidos |
| `GET` | `/groups/{code}/members/{user_id}` | perfil de un miembro: semana, racha, medallas, cara a cara conmigo y últimas sesiones · `404` si no es miembro |
| `GET` | `/groups/{code}/rankings?period&month&from&to` | fuerza, progreso, semana y constancia |
| `GET` | `/groups/{code}/dashboard` | indicadores, series de 8 semanas, días de la semana, objetivo del grupo, líderes, semana pasada y medallas recientes |
| `GET` | `/groups/{code}/feed?limit=30` | PRs con reacciones, mi reacción y si quedó excluido; el cliente los agrupa por sesión |
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
| `DELETE` | `/groups/{code}/duels/{id}` | el retador cancela un reto pendiente · `204` · `403` · `409` si ya fue aceptado |
| `GET` | `/groups/{code}/campaigns` | campañas con su tabla de posiciones |
| `POST` | `/groups/{code}/campaigns` | solo el admin · `201` · `403` · `422` |

## Frontend

Una sola página con vistas por hash, en ES modules y sin build. Primero está pensado para el celular: una columna, botones de al menos 48 px de alto, y las acciones de la carga al alcance del pulgar.

| Hash | Vista |
|---|---|
| `#/login` | login con Google, entrar o crear cuenta con contraseña, o el nombre en modo dev |
| `#/perfil` | nombre, sexo, objetivo semanal y unidad; obligatorio en el primer login |
| `#/` | mis grupos, crear grupo, unirse con código |
| `#/g/CODE/entrenar` | elegir día de rutina o carga libre |
| `#/g/CODE/carga` | carga guiada o libre, con borrador en `localStorage`; al guardar cada serie, PR y posición en vivo |
| `#/g/CODE/rankings` | selector de período, desafíos con DOTS/absoluto, progreso, semana y constancia |
| `#/g/CODE/panel` | portada del grupo: indicadores, gráficos, "Hoy toca", comparar entre miembros, líderes, campaña y últimos PRs |
| `#/g/CODE/feed` | PRs agrupados por sesión, con reacciones (desde "Ver todo" del panel) |
| `#/g/CODE/bro/ID` | perfil de un miembro y cara a cara |
| `#/g/CODE/duelos` | duelos, retar y aceptar |
| `#/g/CODE/campanas` | campañas y su tabla |
| `#/g/CODE/grupo` | miembros, código, desafíos y rutinas (lo de admin, solo para el admin) |
| `#/stats` | mis gráficos por ejercicio, series por músculo, calendario y medallas, en SVG propio |

- **Polling.** Cada 30 segundos en rankings, feed y duelos, solo con la pestaña visible.
- **Discos.** En ejercicios con barra, debajo del peso: los discos por lado con barra de 20 kg (25, 20, 15, 10, 5, 2,5 y 1,25) o de 45 lb (45, 35, 25, 10, 5 y 2,5).
- **Instalable.** `manifest.webmanifest` con ícono y color de tema. Sin service worker.
- **Animaciones.** Rebote de números, tilde al guardar, confeti con PR o medalla nueva, y vibración. Con `prefers-reduced-motion` no hay animación.
- **Libras.** Se convierten en la vista con `1 lb = 0,45359237 kg`. Lo que se manda a la API va siempre en kg.

## Tests

- **`tests/test_stats.py`, `test_rankings_stats.py` y `test_competition_stats.py`.** Cada regla de arriba con casos borde, escrito antes que la función.
- **`tests/test_api.py` y siguientes.** Los status codes del contrato con el `TestClient` y una base en memoria, en modo dev.
- **Frontend.** Se prueba en el navegador con un agente que hace de usuario.
