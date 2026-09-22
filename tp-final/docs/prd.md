# PRD — Gym-bro

## Problem Statement

Entreno con amigos, pero cada uno anota sus series en una app distinta o en una nota del celular. No hay forma de compararse, y comparar kilos no sirve: el que pesa más siempre levanta más. La competencia queda en el chat del grupo, a ojo.

## Solution

Una app web donde un grupo de amigos carga sus sesiones y se compara de forma justa. Cada uno entrena con su rutina, y el grupo elige hasta cuatro ejercicios de desafío que hacen todos. Hay tres rankings: fuerza relativa al peso corporal, progreso contra uno mismo y constancia. Un feed muestra los PRs del grupo.

## User Stories

1. Como usuario, quiero crear un grupo con un nombre, para invitar a mis amigos.
2. Como usuario, quiero recibir un código corto al crear el grupo, para pasarlo por el chat.
3. Como amigo, quiero unirme a un grupo con el código, un nickname y mi peso corporal, para empezar a cargar.
4. Como amigo, quiero que me avise si el nickname ya está tomado en el grupo, para elegir otro.
5. Como miembro, quiero que la app me recuerde en este navegador, para no reingresar el código cada vez.
6. Como miembro, quiero actualizar mi peso corporal, para que la fuerza relativa siga siendo justa.
7. Como miembro, quiero que el grupo arranque con sentadilla, press banca, peso muerto y press militar como desafíos, para no configurar nada al principio.
8. Como miembro, quiero agregar ejercicios de mi rutina, para cargar lo que hago aunque nadie más lo haga.
9. Como miembro, quiero marcar o desmarcar un ejercicio como desafío, para que el grupo elija con qué se compara.
10. Como miembro, quiero que no se puedan marcar más de cuatro desafíos, para que el ranking siga siendo legible.
11. Como miembro, quiero cargar una sesión con fecha y varias series de peso y repeticiones, para registrar lo que entrené.
12. Como miembro, quiero cargar una sesión de un día anterior, para no perderla si me olvidé.
13. Como miembro, quiero que la app rechace pesos, repeticiones o fechas imposibles, para que un error de tipeo no rompa el ranking.
14. Como miembro, quiero borrar una sesión, para corregir una carga equivocada.
15. Como miembro, quiero ver mi 1RM estimado por serie, para saber cuánto levantaría a una repetición.
16. Como miembro, quiero ver al cargar si hice un PR, para festejarlo.
17. Como miembro, quiero un ranking de fuerza relativa por cada desafío, para compararme con alguien más pesado.
18. Como miembro, quiero un ranking de progreso del último mes, para competir aunque sea el más débil del grupo.
19. Como miembro, quiero un ranking de constancia con días entrenados y racha semanal, para que ir seguido también cuente.
20. Como miembro sin datos suficientes, quiero aparecer como "sin datos" y no en último lugar, para que no parezca que me fue mal.
21. Como miembro, quiero un feed con los últimos PRs del grupo, para enterarme cuando alguien rompe una marca.
22. Como miembro, quiero ver mensajes de error claros cuando algo falla, para saber qué corregir.

## Implementation Decisions

- **Stack.** FastAPI con SQLModel sobre SQLite, frontend en HTML, CSS y JavaScript con ES modules sin paso de build. Un solo proceso sirve la API bajo `/api` y los estáticos en `/`.
- **Identidad.** Nickname por grupo, sin contraseña; el código del grupo es el secreto compartido. El navegador guarda código y nickname. Pendiente de la devolución.
- **Datos.**
  - `Group`: nombre y código único.
  - `Member`: grupo, nickname (único dentro del grupo) y peso corporal actual.
  - `Exercise`: grupo, nombre (único dentro del grupo) y si es desafío.
  - `WorkoutSession`: miembro y fecha.
  - `WorkSet`: sesión, ejercicio, peso y repeticiones.
- **Módulo de estadísticas.** Es el módulo profundo del proyecto: funciones puras que reciben series ya leídas de la base y la fecha de hoy, y devuelven 1RM estimado, PRs y los tres rankings. No conoce la base ni HTTP. Las rutas solo leen, llaman y serializan.
- **1RM.** Epley. Las series de más de 10 repeticiones no cuentan.
- **PRs.** Se calculan en orden cronológico por fecha de sesión, no se guardan. La primera serie de un ejercicio es línea base. Así borrar o cargar una sesión atrasada nunca deja el feed inconsistente.
- **Rankings.**
  - Fuerza relativa: mejor 1RM histórico en cada desafío, dividido por el peso corporal actual.
  - Progreso: mejor 1RM de los últimos 28 días contra el mejor anterior, promediado entre los ejercicios con datos en las dos ventanas.
  - Constancia: días entrenados en 28 días, con la racha de semanas como desempate.
- **Contrato.**

| Method | Path | Respuestas |
|---|---|---|
| `POST` | `/api/groups` | `201` grupo con código · `422` |
| `GET` | `/api/groups/{code}` | `200` grupo, miembros y ejercicios · `404` |
| `POST` | `/api/groups/{code}/members` | `201` · `404` · `409` nickname tomado · `422` |
| `PATCH` | `/api/groups/{code}/members/{nickname}` | `200` peso actualizado · `404` · `422` |
| `POST` | `/api/groups/{code}/exercises` | `201` · `404` · `409` nombre repetido o quinto desafío · `422` |
| `PATCH` | `/api/groups/{code}/exercises/{id}` | `200` · `404` · `409` quinto desafío |
| `POST` | `/api/groups/{code}/members/{nickname}/sessions` | `201` sesión con 1RM por serie y PRs · `404` · `422` |
| `DELETE` | `/api/groups/{code}/members/{nickname}/sessions/{id}` | `204` · `404` |
| `GET` | `/api/groups/{code}/rankings` | `200` los tres rankings · `404` |
| `GET` | `/api/groups/{code}/feed` | `200` últimos 20 PRs · `404` |

- **El path identifica, el body transporta.** El grupo y el miembro viajan en el path y no se repiten en el body. Un ejercicio de otro grupo en el body es `422`, no `404`, porque lo inválido es el contenido.
- **Validaciones.** Repeticiones de 1 a 50, peso mayor a 0 y hasta 500 kg, fecha no futura, al menos una serie por sesión.
- **Fechas.** La fecha de la sesión la manda el cliente, sin hora. "Hoy" para las ventanas de los rankings lo define el servidor.

## Testing Decisions

- Un buen test mira comportamiento externo: dado un conjunto de series y una fecha, qué ranking sale. No mira cómo está hecho por dentro.
- **Módulo de estadísticas:** con TDD y pytest, test en rojo antes de cada función. Es donde está la lógica que el agente puede errar: línea base de PRs, series de más de 10 repeticiones, ventanas de 28 días, racha que no se corta en la semana en curso, miembros sin datos.
- **API:** con el `TestClient` de FastAPI sobre una base temporal. Se cubren los status codes del contrato, sobre todo `404`, `409` y `422`.
- **Frontend:** sin tests automáticos. Se verifica en el navegador con el MCP de Playwright, igual que el ejemplo resuelto del curso.
- No hay tests previos en el repo; esta es la primera entrega con tests.

## Out of Scope

- Login con contraseña, cuentas y una persona en varios grupos.
- Ejercicios con peso corporal, como dominadas con lastre.
- Duelos, reacciones en el feed, gráficos de progresión y "cartel de la vergüenza".
- Editar una sesión: se borra y se vuelve a cargar.
- Unidades distintas de kg.
- Tiempo real: los rankings se actualizan al recargar.

## Further Notes

- **Exposición de la idea.** Se muestra un corte vertical: crear o unirse a un grupo, cargar una sesión y ver el ranking de fuerza relativa. Progreso, constancia y feed vienen después de la devolución.
- **Decisiones.** Están con su porqué en [grill.md](grill.md).
- **Trabajo en grupo.** El proyecto es con Gustavo Campero. La carpeta vive en este repo y él trabaja como colaborador.
