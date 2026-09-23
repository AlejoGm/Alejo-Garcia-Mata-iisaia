# PRD — Gym-bro

## Problem Statement

Entreno con amigos, pero cada uno anota sus series en una app distinta o en una nota del celular. No hay forma de compararse, y comparar kilos no sirve: el que pesa más siempre levanta más. La competencia y la motivación entre bros quedan en el chat del grupo, a ojo, y se pierden cuando alguien deja de ir.

## Solution

Una app web donde un grupo de amigos registra lo que entrena, se motiva viendo lo que hace el otro y compite de forma justa.

- **Rutinas:** cada uno sigue su rutina o la misma que su bro. La carga es guiada serie por serie y, en cada serie, muestra lo que hicieron vos y tus amigos la última vez.
- **Rankings:** el grupo elige hasta cuatro ejercicios de desafío y compite en ellos por fuerza DOTS, por fuerza absoluta y por progreso contra uno mismo. Aparte hay un ranking de la semana y la constancia respecto del objetivo semanal de cada uno.
- **Feed:** muestra los PRs y se puede reaccionar a cada uno.
- **Duelos:** retos uno contra uno en un ejercicio.
- **Campañas:** competencias con fecha de inicio, fecha de fin y un ganador.

## Releases

| Versión | Qué agrega |
|---|---|
| **v1 (MVP)** | Grupos con código · carga libre con peso corporal por sesión y "la última vez" · fuerza DOTS y absoluta por desafío · PR de peso y PR de 1RM con feed · progreso mes contra mes · ranking de la semana · gestión de desafíos · borrar sesión |
| **v1.1** | Primero: rutinas del grupo y carga guiada con borrador local. Después: constancia por objetivo semanal |
| **v2** | Duelos con sugerencia de rival y nivel de desbalance · reacciones · gráficos por mes y por semana · períodos de 6 meses, 12 meses y elegido · admin del grupo · polling |
| **v3** | Cuentas y varios grupos por persona · campañas · validación social de PRs dudosos · ejercicios con lastre · libras |

La v1 y la v1.1 apuntan al Demo Day. Si no llega todo, lo primero que se cae es la constancia, que se nota menos que las rutinas.

La exposición de la idea mostró un corte de la v1: crear o unirse a un grupo, cargar una sesión y un ranking de fuerza relativa simple, que en la v1 pasa a DOTS.

## User Stories

### Grupo y miembros

1. **[v1]** Como usuario, quiero crear un grupo y recibir un código corto, para invitar a mis amigos por el chat.
2. **[v1]** Como amigo, quiero unirme con el código, un nickname, mi sexo, mi peso y mi objetivo semanal, para empezar a cargar.
3. **[v1]** Como amigo, quiero que me avise si el nickname ya está tomado, para elegir otro.
4. **[v1]** Como miembro, quiero que la app me recuerde en este navegador, para no reingresar el código.
5. **[v1]** Como miembro, quiero cambiar mi objetivo semanal, para ajustarlo si cambio de rutina.
6. **[v2]** Como creador del grupo, quiero ser admin, para decidir los desafíos y sacar a alguien que ya no va.
7. **[v3]** Como usuario, quiero una cuenta y estar en varios grupos, para competir con los del gym y con los del laburo.

### Ejercicios y rutinas

8. **[v1]** Como miembro, quiero que el grupo arranque con sentadilla, press banca, peso muerto y press militar como desafíos, para no configurar nada al principio.
9. **[v1]** Como miembro, quiero agregar ejercicios y marcar hasta cuatro como desafío, para que el grupo elija con qué se compara.
10. **[v1.1]** Como miembro, quiero crear una rutina con días y ejercicios con cantidad de series, para no pensar qué toca hoy.
11. **[v1.1]** Como miembro, quiero seguir la misma rutina que mi bro, para comparar serie por serie.
12. **[v1.1]** Como miembro, quiero que me avise si edito una rutina que siguen otros, para no cambiársela sin querer.
13. **[v3]** Como miembro, quiero cargar dominadas con lastre, para que cuenten mi peso más el lastre.

### Carga

14. **[v1]** Como miembro, quiero cargar una sesión libre con fecha, peso corporal y varias series, para registrar lo que entrené.
15. **[v1]** Como miembro, quiero que el peso corporal venga prellenado con el último, para cambiarlo solo cuando me peso.
16. **[v1]** Como miembro, quiero ver al elegir un ejercicio mi última serie y la de mis amigos, para saber qué peso poner y a quién le tengo que ganar.
17. **[v1]** Como miembro, quiero cargar una sesión de un día anterior, para no perderla si me olvidé.
18. **[v1]** Como miembro, quiero que la app rechace pesos, reps o fechas imposibles, para que un error de tipeo no rompa el ranking.
19. **[v1]** Como miembro, quiero borrar una sesión, para corregir una carga equivocada.
20. **[v1]** Como miembro, quiero ver el 1RM estimado de cada serie, para saber cuánto levantaría a una repetición.
21. **[v1.1]** Como miembro, quiero elegir el día de mi rutina y que la app me lleve serie por serie, para cargar tocando y siguiendo.
22. **[v1.1]** Como miembro, quiero saltear un ejercicio, sumar una serie o agregar uno que no estaba, porque en el gimnasio nunca sale igual.
23. **[v1.1]** Como miembro, quiero que lo que cargo no se pierda si se corta la señal o cierro la pestaña, para no volver a cargar la sesión entera.
24. **[v3]** Como miembro, quiero ver los pesos en libras, porque así están los discos de mi gimnasio.

### Rankings

25. **[v1]** Como miembro, quiero un ranking DOTS por desafío, para compararme de forma justa con alguien de otro peso.
26. **[v1]** Como miembro, quiero cambiar a ranking absoluto, para ver quién mueve más hierro.
27. **[v1]** Como miembro, quiero un ranking de progreso de este mes contra el anterior, para competir aunque sea el más débil.
28. **[v1]** Como miembro, quiero ver mi mejor 1RM y mi promedio del mes por ejercicio, para saber dónde estoy.
29. **[v1]** Como miembro, quiero un ranking de la semana con mis sesiones contra mi objetivo, para ver día a día quién va mejor.
30. **[v1]** Como miembro, quiero que se marque quién ya no llega a su objetivo, para presionar al que falta.
31. **[v1]** Como miembro sin datos, quiero aparecer como "sin datos" y no último, para que no parezca que me fue mal.
32. **[v1.1]** Como miembro, quiero un ranking de constancia por semanas cumplidas y racha, para que cumplir mi plan valga aunque entrene menos días que otros.
33. **[v2]** Como miembro, quiero elegir el período (6 meses, 12 meses o fechas a mano) y que cambien todas las tablas, para ver cómo me fue en el año.
34. **[v2]** Como miembro, quiero gráficos de mi mejor 1RM y mi promedio por mes, y una línea por semana, para ver la tendencia.

### Feed y lo social

35. **[v1]** Como miembro, quiero ver al cargar si hice un PR de peso o de 1RM, para festejarlo.
36. **[v1]** Como miembro, quiero un feed con los PRs del grupo, para enterarme cuando alguien rompe una marca.
37. **[v2]** Como miembro, quiero reaccionar a un PR con fuerza, fuego o dudoso, para festejar o bardear sin ir al chat.
38. **[v2]** Como miembro, quiero retar a alguien a un duelo de absoluto o DOTS en un ejercicio, para tener una competencia puntual.
39. **[v2]** Como retador, quiero que me sugiera rivales parejos y me muestre el desbalance, para elegir un duelo con gracia.
40. **[v2]** Como retado, quiero ver el desbalance antes de aceptar o rechazar, para no meterme en uno perdido.
41. **[v3]** Como admin, quiero crear una campaña con fechas, tablas que suman puntos y rutina opcional, para organizar una competencia del grupo.
42. **[v3]** Como miembro, quiero ver en vivo la tabla de la campaña y el ganador al cierre, para saber si voy ganando.
43. **[v3]** Como miembro, quiero que un PR que la mayoría marca como dudoso deje de contar, para que nadie infle sus marcas.

### Transversal

44. **[v1]** Como miembro, quiero mensajes de error claros, para saber qué corregir.
45. **[v1]** Como miembro, quiero usar la app cómodo desde el celular, porque cargo en el gimnasio.

## Implementation Decisions

### Arquitectura

- **Stack.** FastAPI con SQLModel sobre SQLite. Frontend en HTML, CSS y JavaScript con ES modules, sin paso de build. Un solo proceso sirve la API bajo `/api` y los estáticos en `/`.
- **Módulo de estadísticas.** Es el módulo profundo del proyecto. Son funciones puras que reciben series ya leídas y la fecha de hoy, y devuelven 1RM, DOTS, PRs, rankings, stats del mes y, desde v2, duelos y desbalance. No conoce la base ni HTTP. Las rutas solo leen, llaman y serializan.
- **Todo lo derivable se calcula.** PRs, rankings, resultados de duelos y posiciones de campaña salen de las series. La única excepción es el ganador de una campaña cerrada, que se congela porque es un premio.
- **El path identifica, el body transporta.** El grupo y el miembro van en el path y no se repiten en el body.
- **Identidad.** Nickname por grupo, sin contraseña. El navegador guarda el código y el nickname. El riesgo está asumido hasta las cuentas de la v3.

### Datos

- **v1.**
  - `Group`: nombre y código.
  - `Member`: nickname, sexo y objetivo semanal.
  - `Exercise`: nombre y si es desafío.
  - `WorkoutSession`: miembro, fecha y peso corporal.
  - `WorkSet`: sesión, ejercicio, peso y reps.
- **v1.1.**
  - `Routine`: grupo y nombre.
  - `RoutineDay`: rutina, nombre y orden.
  - `RoutineItem`: día, ejercicio, series y orden.
  - `WorkoutSession` suma el día de rutina, opcional.
  - `WeeklyGoalChange`: miembro, objetivo y semana desde la que rige.
- **v2.**
  - `Duel`: retador, retado, ejercicio, modo, duración, inicio y estado.
  - `Reaction`: miembro, serie y tipo.
  - `Member` suma el rol de admin.
- **v3.**
  - `User`: la cuenta, que pasa a ser la identidad.
  - `Member` pasa a ser la relación entre `User` y `Group`.
  - `Campaign`: fechas, tablas que suman, rutina opcional y ganador congelado.
  - `Exercise` suma el flag "con lastre".

### Reglas

- **1RM.** Epley. Las series de más de 10 reps no estiman.
- **DOTS.** Se calcula sobre el 1RM estimado, con el peso corporal de la sesión de esa serie y los coeficientes de OpenPowerlifting por sexo. El peso se lleva al rango de la fórmula: de 40 a 210 kg en hombres y de 40 a 150 kg en mujeres.
- **Absoluto.** El mayor peso levantado en una serie. Desempata más reps y, si siguen iguales, la fecha más temprana.
- **PRs.** Se evalúan en orden cronológico:
  - **"PR de peso":** más kilos, o los mismos kilos con más reps.
  - **"PR de 1RM":** sube el 1RM estimado sin subir el peso.

  Si una serie cumple las dos, se muestra solo "de peso". La primera serie de un ejercicio es línea base.
- **Meses.** Son de calendario, y la zona horaria es la del servidor. Stats del mes: el mejor 1RM y el promedio del mejor 1RM de cada sesión.
- **Progreso.** Mejor del mes contra mejor del mes anterior, en porcentaje, promediado entre los ejercicios con datos en los dos meses.
- **Ranking de la semana.** Lunes a domingo, ordenado por sesiones. Muestra "x / objetivo". Estados:
  - **"cumplido":** llegó a su objetivo.
  - **"ya no llega":** le faltan más sesiones que días quedan.

  Desempata el porcentaje del objetivo cumplido.
- **Constancia (v1.1).** Porcentaje de semanas cerradas en que se cumplió el objetivo vigente, más la racha. La semana en curso no cuenta. Un cambio de objetivo rige desde la semana siguiente.
- **Carga guiada (v1.1).** Borrador en el navegador y un solo `POST` al terminar, con reintento. La rutina es una guía, no se valida contra lo cargado.
- **Duelos (v2).** Modo absoluto o DOTS. Duran 3, 7 o 14 días. Gana la mejor serie en el plazo. Quien no hace el ejercicio pierde, y si no lo hace ninguno es empate. El desbalance es bajo hasta 10%, medio hasta 25% y alto por encima.
- **Campañas (v3).** Puntos 10, 8, 6... por posición en las tablas elegidas. Desempata la cantidad de primeros puestos.
- **Validaciones.** Reps de 1 a 50, peso de más de 0 a 500 kg, peso corporal de más de 0 a 300 kg, fecha no futura, al menos una serie.

### Contrato de la v1

| Method | Path | Respuestas |
|---|---|---|
| `POST` | `/api/groups` | `201` grupo con código · `422` |
| `GET` | `/api/groups/{code}` | `200` grupo, miembros y ejercicios · `404` |
| `POST` | `/api/groups/{code}/members` | `201` · `404` · `409` nickname tomado · `422` |
| `PATCH` | `/api/groups/{code}/members/{nickname}` | `200` objetivo semanal actualizado · `404` · `422` |
| `POST` | `/api/groups/{code}/exercises` | `201` · `404` · `409` nombre repetido o quinto desafío · `422` |
| `PATCH` | `/api/groups/{code}/exercises/{id}` | `200` · `404` · `409` quinto desafío |
| `GET` | `/api/groups/{code}/exercises/{id}/recent` | `200` última serie de hasta tres miembros · `404` |
| `POST` | `/api/groups/{code}/members/{nickname}/sessions` | `201` sesión con 1RM, DOTS y PRs por serie · `404` · `422` |
| `DELETE` | `/api/groups/{code}/members/{nickname}/sessions/{id}` | `204` · `404` |
| `GET` | `/api/groups/{code}/rankings?month=2026-09` | `200` DOTS y absoluto por desafío, progreso, stats del mes y ranking de la semana · `404` · `422` mes inválido |
| `GET` | `/api/groups/{code}/feed` | `200` últimos 20 PRs con su tipo · `404` |

Un ejercicio de otro grupo en el body es `422`, no `404`, porque lo inválido es el contenido. En la v1.1 se suman `routines` bajo el grupo y el día de rutina opcional en el body de la sesión. En la v2 se suman `duels` y `reactions`. En la v3 aparecen `/api/auth` y `campaigns`.

## Testing Decisions

- Un buen test mira comportamiento externo: dado un conjunto de series y una fecha, qué ranking sale. No mira cómo está hecho por dentro.
- **Módulo de estadísticas:** con TDD y pytest, y el test en rojo antes de cada función. Es donde está la lógica que el agente puede errar: coeficientes y rango de DOTS, desempates del absoluto, los dos tipos de PR, bordes de mes, "ya no llega" según el día de la semana, miembros sin datos. En la v1.1 se suman la constancia con cambios de objetivo, y en la v2 los duelos y el desbalance.
- **DOTS:** se verifica contra valores calculados a mano. Por ejemplo, un hombre de 95 kg con 170 da 107,1, y uno de 65 kg con 130 da 103,0.
- **API:** con el `TestClient` de FastAPI sobre una base en memoria. Se cubren los status codes del contrato, sobre todo `404`, `409` y `422`.
- **Frontend:** sin tests automáticos. Se verifica en el navegador, en desktop y en mobile. La carga guiada se prueba además cortando el servidor a mitad de sesión.
- **Prior art:** `tests/test_stats.py` y `tests/test_api.py`, del corte de la exposición.

## Out of Scope

Quedan fuera del producto en cualquier versión:
- Notificaciones push y app móvil nativa.
- Planes de entrenamiento generados por la app y nutrición.
- Tiempo real con WebSockets; alcanza con polling.
- Comentarios libres en el feed; para eso está el chat del grupo.
- Integración con relojes o apps de fitness.
- Sincronización en segundo plano; alcanza con borrador local y reintento.

## Further Notes

- **Decisiones.** Están con su porqué, y con qué cambió en el repaso, en [grill.md](grill.md).
- **Del corte de la exposición a la v1.** El corte usa el ratio simple y el peso del perfil. Hay que migrar ese ranking a DOTS con el peso por sesión, y sumar sexo y objetivo al unirse.
- **Trabajo en grupo.** El proyecto es con Gustavo Campero. La carpeta vive en este repo y él trabaja como colaborador.
