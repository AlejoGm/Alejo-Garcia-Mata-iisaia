# PRD — Gym-bro

## Problem Statement

Entreno con amigos, pero cada uno anota sus series en una app distinta o en una nota del celular. No hay forma de compararse, y comparar kilos no sirve: el que pesa más siempre levanta más. La competencia queda en el chat del grupo, a ojo, y se pierde cuando alguien deja de ir.

## Solution

Una app web donde un grupo de amigos registra lo que entrena y compite de forma justa. Cada uno sigue su rutina, y el grupo elige hasta cuatro ejercicios de desafío que hacen todos.

- **Rankings:** hay tres, fuerza relativa al peso corporal, progreso contra uno mismo y constancia.
- **Feed:** muestra los PRs y se puede reaccionar a cada uno.
- **Duelos:** dos amigos se retan en un ejercicio por una semana.
- **Temporadas:** cada mes los rankings se reinician y queda guardado el campeón.

El producto se construye en tres versiones. La v1 es el MVP que se presenta en el Demo Day.

## Releases

| Versión | Qué agrega | Para qué |
|---|---|---|
| **v1 (MVP)** | Grupos con código, carga de sesiones, 1RM estimado, los tres rankings, feed de PRs, gestión de ejercicios de desafío | Que el grupo pueda compararse de forma justa |
| **v2** | Duelos, reacciones, gráficos de progresión, historial de peso corporal, cartel de la vergüenza, plantillas de rutina, admin del grupo, polling | Que compararse sea social y tenga motivo para volver |
| **v3** | Cuentas y varios grupos por persona, validación social de cargas, temporadas mensuales, ejercicios con lastre, libras | Que el producto aguante grupos que no se conocen tanto y dure más de un mes |

La exposición de la idea muestra un corte de la v1, ya hecho: crear o unirse a un grupo, cargar una sesión y ver el ranking de fuerza relativa.

## User Stories

### Grupo y miembros

1. **[v1]** Como usuario, quiero crear un grupo con un nombre, para invitar a mis amigos.
2. **[v1]** Como usuario, quiero recibir un código corto al crear el grupo, para pasarlo por el chat.
3. **[v1]** Como amigo, quiero unirme con el código, un nickname y mi peso corporal, para empezar a cargar.
4. **[v1]** Como amigo, quiero que me avise si el nickname ya está tomado, para elegir otro.
5. **[v1]** Como miembro, quiero que la app me recuerde en este navegador, para no reingresar el código cada vez.
6. **[v1]** Como miembro, quiero actualizar mi peso corporal, para que la fuerza relativa siga siendo justa.
7. **[v2]** Como creador del grupo, quiero ser admin, para decidir los desafíos y sacar a alguien que ya no va.
8. **[v2]** Como miembro, quiero registrar mi peso con fecha, para que una marca vieja se compare con el peso que tenía entonces.
9. **[v3]** Como usuario, quiero una cuenta con contraseña, para que nadie cargue a mi nombre.
10. **[v3]** Como usuario, quiero estar en varios grupos con la misma cuenta, para competir con los del gym y con los del laburo.

### Ejercicios

11. **[v1]** Como miembro, quiero que el grupo arranque con sentadilla, press banca, peso muerto y press militar como desafíos, para no configurar nada al principio.
12. **[v1]** Como miembro, quiero agregar ejercicios de mi rutina, para cargar lo que hago aunque nadie más lo haga.
13. **[v1]** Como miembro, quiero marcar o desmarcar un ejercicio como desafío, sin pasar de cuatro, para que el grupo elija con qué se compara.
14. **[v3]** Como miembro, quiero cargar dominadas con lastre, para que cuenten mi peso corporal más el lastre.

### Sesiones

15. **[v1]** Como miembro, quiero cargar una sesión con fecha y varias series de peso y repeticiones, para registrar lo que entrené.
16. **[v1]** Como miembro, quiero cargar una sesión de un día anterior, para no perderla si me olvidé.
17. **[v1]** Como miembro, quiero que la app rechace pesos, repeticiones o fechas imposibles, para que un error de tipeo no rompa el ranking.
18. **[v1]** Como miembro, quiero borrar una sesión, para corregir una carga equivocada.
19. **[v1]** Como miembro, quiero ver el 1RM estimado de cada serie, para saber cuánto levantaría a una repetición.
20. **[v2]** Como miembro, quiero guardar una sesión como plantilla, para cargar mi rutina de siempre en dos clics.
21. **[v3]** Como miembro, quiero ver los pesos en libras, porque así están los discos de mi gimnasio.

### Rankings

22. **[v1]** Como miembro, quiero un ranking de fuerza relativa por cada desafío, para compararme con alguien más pesado.
23. **[v1]** Como miembro, quiero un ranking de progreso del último mes, para competir aunque sea el más débil del grupo.
24. **[v1]** Como miembro, quiero un ranking de constancia con días entrenados y racha semanal, para que ir seguido también cuente.
25. **[v1]** Como miembro sin datos suficientes, quiero aparecer como "sin datos" y no en último lugar, para que no parezca que me fue mal.
26. **[v2]** Como miembro, quiero ver en un gráfico cómo evolucionó mi 1RM en un ejercicio, para ver si estoy estancado.
27. **[v2]** Como miembro, quiero que los rankings se actualicen solos, para verlos cambiar mientras alguien carga en el gimnasio.
28. **[v3]** Como miembro, quiero temporadas mensuales con campeón guardado, para que el que arrancó tarde tenga chance.

### Feed y lo social

29. **[v1]** Como miembro, quiero ver al cargar si hice un PR, para festejarlo.
30. **[v1]** Como miembro, quiero un feed con los últimos PRs del grupo, para enterarme cuando alguien rompe una marca.
31. **[v2]** Como miembro, quiero reaccionar a un PR con fuerza, fuego o dudoso, para festejar o bardear sin ir al chat.
32. **[v2]** Como miembro, quiero retar a alguien a un duelo de una semana en un ejercicio, para tener una competencia puntual.
33. **[v2]** Como retado, quiero aceptar o rechazar el duelo, para no quedar metido en uno que no puedo entrenar.
34. **[v2]** Como miembro, quiero que el resultado del duelo aparezca en el feed, para que el perdedor quede expuesto.
35. **[v2]** Como miembro, quiero un cartel con quién no fue en la semana, para presionar al que falta.
36. **[v3]** Como miembro, quiero que un PR que la mayoría marca como dudoso deje de contar, para que nadie infle sus marcas.

### Transversal

37. **[v1]** Como miembro, quiero mensajes de error claros cuando algo falla, para saber qué corregir.
38. **[v1]** Como miembro, quiero usar la app cómodo desde el celular, porque cargo las series en el gimnasio.

## Implementation Decisions

### Arquitectura (todas las versiones)

- **Stack.** FastAPI con SQLModel sobre SQLite, frontend en HTML, CSS y JavaScript con ES modules sin paso de build. Un solo proceso sirve la API bajo `/api` y los estáticos en `/`.
- **Módulo de estadísticas.** Es el módulo profundo del proyecto: funciones puras que reciben series ya leídas de la base y la fecha de hoy, y devuelven 1RM estimado, PRs, rankings y, desde v2, el resultado de los duelos. No conoce la base ni HTTP. Las rutas solo leen, llaman y serializan.
- **Todo lo derivable se calcula.** PRs, rankings, resultados de duelos y campeones de temporada salen de las series. No se guardan eventos derivados, así borrar o cargar una sesión atrasada nunca deja datos inconsistentes. La excepción es el campeón de una temporada cerrada, que se congela en v3 porque es un premio.
- **El path identifica, el body transporta.** El grupo y el miembro viajan en el path y no se repiten en el body.

### Datos por versión

- **v1.**
  - `Group`: nombre y código único.
  - `Member`: grupo, nickname único en el grupo y peso corporal actual.
  - `Exercise`: grupo, nombre único en el grupo y si es desafío.
  - `WorkoutSession`: miembro y fecha.
  - `WorkSet`: sesión, ejercicio, peso y repeticiones.
- **v2.**
  - `BodyweightEntry`: miembro, fecha y peso. El peso actual pasa a ser el último registro.
  - `Duel`: retador, retado, ejercicio, inicio, estado.
  - `Reaction`: miembro, serie y tipo.
  - `Template`: miembro y series tipo.
  - `Member` suma el rol de admin.
- **v3.**
  - `User`: cuenta con contraseña.
  - `Member` pasa a ser la relación entre `User` y `Group`.
  - `Exercise` suma el flag "con lastre".
  - `SeasonChampion`: grupo, mes, tabla y miembro.

### Reglas de la v1

- **1RM.** Epley. Las series de más de 10 repeticiones no cuentan.
- **PRs.** Orden cronológico por fecha de sesión. La primera serie de un ejercicio es línea base.
- **Fuerza relativa.** Mejor 1RM histórico en cada desafío, dividido por el peso corporal actual.
- **Progreso.** Mejor 1RM de los últimos 28 días contra el mejor anterior, promediado entre los ejercicios con datos en las dos ventanas.
- **Constancia.** Días entrenados en 28 días, con la racha de semanas como desempate. La semana en curso no corta la racha.
- **Validaciones.** Repeticiones de 1 a 50, peso mayor a 0 y hasta 500 kg, fecha no futura, al menos una serie por sesión.
- **Fechas.** La fecha de la sesión la manda el cliente, sin hora. "Hoy" lo define el servidor.
- **Identidad.** Nickname por grupo, sin contraseña; el navegador guarda código y nickname.

### Reglas que llegan después

- **Duelos (v2).** 7 días desde que el retado acepta. Gana el que más mejora en porcentaje sobre su mejor 1RM previo al duelo. Un duelo activo por par.
- **Peso vigente (v2).** La fuerza relativa usa el peso registrado más reciente a la fecha de cada serie.
- **Validación social (v3).** Un PR con reacciones "dudoso" de más de la mitad del grupo deja de contar.
- **Temporadas (v3).** Mes calendario. Al cerrar, se congela el primero de cada tabla.

### Contrato de la v1

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

Un ejercicio de otro grupo en el body es `422`, no `404`, porque lo inválido es el contenido. En v2 se suman los recursos `duels`, `reactions`, `bodyweight` y `templates` bajo el grupo o el miembro. En v3 aparecen `/api/auth` y el grupo deja de ser la raíz de la identidad.

## Testing Decisions

- Un buen test mira comportamiento externo: dado un conjunto de series y una fecha, qué ranking sale. No mira cómo está hecho por dentro.
- **Módulo de estadísticas:** con TDD y pytest, test en rojo antes de cada función. Es donde está la lógica que el agente puede errar: línea base de PRs, series de más de 10 repeticiones, ventanas de 28 días, racha, miembros sin datos y, en v2, el resultado de los duelos y el peso vigente por fecha.
- **API:** con el `TestClient` de FastAPI sobre una base en memoria. Se cubren los status codes del contrato, sobre todo `404`, `409` y `422`.
- **Frontend:** sin tests automáticos. Se verifica en el navegador, en desktop y en mobile.
- **Prior art:** `tests/test_stats.py` y `tests/test_api.py`, del corte de la exposición.

## Out of Scope

Quedan fuera del producto en cualquier versión:
- Notificaciones push y app móvil nativa.
- Rutinas armadas por la app, planes de entrenamiento y nutrición.
- Tiempo real con WebSockets: alcanza con polling.
- Comentarios libres en el feed: para eso ya está el chat del grupo.
- Integración con relojes o apps de fitness.

## Further Notes

- **Decisiones.** Están con su porqué en [grill.md](grill.md).
- **Pendiente de la devolución.** Si la identidad por nickname alcanza para la v1 o las cuentas tienen que adelantarse, y si los tres rankings entran en la v1.
- **Trabajo en grupo.** El proyecto es con Gustavo Campero. La carpeta vive en este repo y él trabaja como colaborador.
