# Grill de Gym-bro

Decisiones de diseño con su porqué. Salió en dos pasadas. Primero un auto-grill con la skill `grilling`, donde el agente se hizo las preguntas y propuso cada respuesta. Después lo repasamos pregunta por pregunta: la sección siguiente resume qué cambió en ese repaso, y el resto del documento ya está actualizado.

## Qué cambió al repasarlo

- **Fuerza relativa.** El auto-grill proponía 1RM / peso corporal, pero eso favorece al liviano porque la fuerza no escala lineal con el peso. Pasó a **DOTS**.
- **Peso corporal.** El auto-grill usaba el actual del perfil, y bajar de peso mejoraba marcas viejas. Ahora el peso viaja con cada sesión.
- **Progreso.** El auto-grill lo medía contra el récord histórico, y un veterano daba negativo casi siempre. Ahora es mes de calendario contra mes anterior.
- **Constancia.** El auto-grill contaba días entrenados, lo que premia al que va más, no al que cumple. Ahora es cumplimiento de un objetivo semanal propio.
- **Agregados.** Ranking absoluto, dos tipos de PR, ranking semanal (en lugar del cartel de la vergüenza), rutinas del grupo con carga guiada, y campañas con ganador (en lugar de temporadas mensuales).
- **Descartado.** El PIN por miembro: se queda solo con nickname.

## Tercera pasada: login con Google y app completa

Al encarar la app entera decidí sumar login con Google por Auth0, que tiene plan gratis. Eso adelanta las cuentas de la v3 y cambia la raíz del modelo. Lo cerré con otro auto-grill, cuyas respuestas quedaron en las secciones de abajo:

- **Proveedor.** Auth0 con conexión de Google. El backend no maneja contraseñas.
- **Raíz del modelo.** La identidad deja de ser el nickname dentro del grupo y pasa a ser el usuario. Una persona puede estar en varios grupos.
- **De quién son las sesiones.** Del usuario, no del grupo. Lo que entrenás cuenta en todos tus grupos.
- **Catálogo de ejercicios.** Pasa a ser global. Los desafíos siguen siendo por grupo.
- **Modo desarrollo.** Sin Auth0 configurado, la app entra con un login de desarrollo que pide solo un nombre. Así corre en cualquier máquina, en los tests y en la prueba con agentes.

## Producto

**¿Qué es?** Un lugar donde un grupo de amigos registra lo que entrena, se motiva viendo lo que hace el otro y compite de forma justa. Cada uno puede seguir su rutina o la misma que su bro; los rankings no dependen de la rutina.

**¿Cómo se parte en versiones?**
- **v1:** carga libre y rankings.
- **v1.1:** rutinas con carga guiada, y constancia.
- **v2:** lo social (duelos, reacciones, gráficos).
- **v3:** campañas, validación social, lastre y libras. Las cuentas se adelantaron: entran desde el principio con el login de Google.

**¿Tiempo real, notificaciones, app nativa?** No. Polling cada 30 segundos desde la v2, y una web que se usa desde el celular.

## Identidad

**¿Cómo se identifica cada uno?** Con su cuenta de Google, a través de Auth0. El frontend usa el SDK de Auth0 para SPA y manda un access token en cada request. El backend lo valida contra las claves públicas del tenant (JWKS), con la audiencia de la API. Del token se toma el `sub`: es el usuario.

**¿Por qué Auth0 y no Google directo?** Con Auth0 el login de Google funciona sin crear un proyecto en Google Cloud: en desarrollo usa las credenciales de prueba de Auth0. Y si mañana se suma otro proveedor, es un switch en el panel, no código.

**¿Qué pasa sin Auth0 configurado?** Si no está la variable `AUTH0_DOMAIN`, la app arranca en modo desarrollo: un login que pide un nombre y emite un token `dev:<nombre>`. El servidor lo avisa en el log al arrancar. Con Auth0 configurado, ese token se rechaza.

**¿Qué se guarda del usuario?** El `sub` de Auth0, un nombre para mostrar, el sexo (para DOTS), la unidad preferida y el objetivo semanal. El email no: no hace falta para nada.

**¿Cuándo se completa el perfil?** En el primer login. Hasta que no está el perfil, la app no deja hacer otra cosa, porque sin sexo no hay DOTS y sin objetivo no hay ranking semanal.

**¿Nickname por grupo?** No. Cada usuario tiene un solo nombre para mostrar en todos sus grupos. Dos usuarios pueden llamarse igual: los identifica el id, no el nombre.

**¿Una persona en varios grupos?** Sí. Las sesiones son del usuario, así que una sentadilla cuenta en todos sus grupos. Los rankings de un grupo toman todas las sesiones de sus miembros, incluso las de antes de entrar: el historial es personal.

**¿Quién administra un grupo?** El que lo crea. Si el admin se va, pasa a serlo el miembro más antiguo. El admin elige los desafíos, saca miembros y crea campañas.

**¿Se sigue invitando con código?** Sí. El código de 6 caracteres es la invitación. Unirse requiere estar logueado.

## Fuerza

**¿Cómo se compara la fuerza entre pesos distintos?** Con DOTS, el coeficiente que usa el powerlifting, con los coeficientes de OpenPowerlifting:
- **Fórmula:** `levantado × 500 / (a·p⁴ + b·p³ + c·p² + d·p + e)`, donde `p` es el peso corporal en kg.
- **Rango de p:** de 40 a 210 kg en hombres y de 40 a 150 kg en mujeres. Fuera de rango se usa el extremo más cercano.
- **Aplicación:** DOTS está calibrado para el total de los tres levantamientos. Acá se aplica a un ejercicio suelto: la escala por peso se conserva, los números salen más chicos.

**¿Sobre qué número se aplica?** Sobre el 1RM estimado con Epley: `peso × (1 + reps / 30)`, y con 1 rep es el peso. Las series de más de 10 reps no estiman 1RM.

**¿Qué peso corporal cuenta?** El de la sesión. El formulario lo trae prellenado con el último, y cada serie usa el de su sesión. El historial de peso sale de ahí, sin entidad aparte.

**¿Hay ranking absoluto?** Sí. Es el peso más alto levantado en una serie, con cualquier cantidad de reps. A igual peso gana el que hizo más reps, y si también empatan, el que lo hizo primero. Se elige con un selector **DOTS / Absoluto** en cada desafío.

**¿Qué es un PR?**
- **"PR de peso":** más kilos que nunca en ese ejercicio, o los mismos kilos con más reps.
- **"PR de 1RM":** subió el 1RM estimado pero no el peso.

Si una serie cumple las dos condiciones, se muestra solo "PR de peso". La primera serie de un ejercicio es línea base, no PR. Los PRs se calculan, no se guardan.

## Progreso y períodos

**¿Contra qué se mide?** Contra uno mismo, en meses de calendario. Es tu mejor 1RM del mes contra tu mejor del mes anterior, en porcentaje y promediado entre los ejercicios que hiciste en los dos meses. Después se rankean esos porcentajes.

**¿Qué stats tiene un mes?** El mejor 1RM y el promedio del mejor 1RM de cada sesión.

**¿Y períodos largos?** En la v2 llegan 6 meses, 12 meses y un período elegido a mano, con un selector que cambia todas las tablas juntas. En ese caso se compara el mes actual contra el mes con el que arranca el período. Los gráficos muestran el mejor y el promedio por mes, y una línea semana a semana.

## Constancia (v1.1)

**¿Qué mide?** El cumplimiento de tu objetivo semanal: el porcentaje de semanas del período en que llegaste a tu objetivo. La racha son las semanas seguidas cumpliéndolo. Así el que va 3 veces y nunca falla le gana al que va 6 y falla la mitad.

**¿Y la semana en curso?** No cuenta hasta que termina.

**¿Si cambio el objetivo?** Rige desde la semana siguiente. Por eso se guarda el historial de objetivos.

## Ranking de la semana (v1)

**¿Qué muestra?** Las sesiones de cada uno de lunes a domingo, con "x / objetivo" al lado. Hay dos estados:
- **"cumplido":** llegaste a tu objetivo.
- **"ya no llega":** te faltan más sesiones que días quedan en la semana.

A igual cantidad de sesiones, queda arriba el que tiene más porcentaje del objetivo cumplido. Reemplaza al cartel de la vergüenza.

## Rutinas (v1.1)

**¿De quién son?** Del grupo. Cualquiera crea una y cada miembro elige cuál sigue: la misma que su bro, otra, o ninguna. Si alguien edita una rutina que siguen otros, la app avisa.

**¿Qué tiene una rutina?** Nombre y días. Cada día es una lista de ejercicios con cantidad de series.

**¿Cómo es la carga guiada?** Se elige el día y la app va serie por serie: ejercicio y "Serie 1 de 3", peso y reps, con los botones "Siguiente serie" y "Terminar ejercicio". El peso viene prellenado con tu última vez.

**¿Qué pasa si me salgo de la rutina?** La rutina es una guía. Podés saltear un ejercicio, sumar series, agregar uno que no estaba o cambiar el orden. La sesión guarda lo que hiciste y no hay métrica de cumplimiento de la rutina.

**¿Cuándo se guarda?** Al final, en un solo `POST`, como la carga libre. Cada serie queda en un borrador en el navegador. Si falla la conexión, aparece "Reintentar". Si se cierra la pestaña, al volver la app pregunta si seguís.

**¿"La última vez"?** Va desde la v1, también en la carga libre. Al elegir un ejercicio muestra tu última serie y la de hasta dos miembros más que lo hayan hecho hace poco.

## Duelos (v2)

**¿Cómo se gana?** El retador elige el modo: absoluto o DOTS. Gana la mejor serie del ejercicio dentro del plazo. Progreso queda afuera.

**¿Cuánto dura?** 3, 7 o 14 días; 7 por defecto.

**¿Sin datos?** Si uno no hace el ejercicio, pierde. Si no lo hace ninguno, o empatan exacto, es empate.

**¿Se garantiza que sea parejo?** No. La app sugiere rivales parejos y muestra el desbalance entre los mejores del mes de cada uno, en el modo elegido:

| Nivel | Diferencia |
|---|---|
| Bajo | hasta 10% |
| Medio | de 10 a 25% |
| Alto | más de 25% |
| Sin datos | alguno no hizo el ejercicio en el mes |

Cualquiera puede retar a cualquiera. El retado ve el nivel antes de aceptar. Hay un solo duelo activo por par.

## Campañas (v3)

**¿Qué son?** Una competencia del grupo con fecha de inicio, fecha de fin y ganador. Pueden exigir que todos sigan la misma rutina o ser indistintas. Reemplazan a las temporadas mensuales.

**¿Cómo se define el ganador?** Por puntos de posición, como en la Fórmula 1 (10, 8, 6...), en las tablas que se eligen al crear la campaña:
- **Tablas por defecto:** DOTS en los desafíos, progreso y constancia. El absoluto queda afuera por defecto, porque ya lo gana el más pesado.
- **Empate:** gana el que tenga más primeros puestos.
- **Durante la campaña:** la tabla de posiciones se ve en vivo.
- **Al terminar:** el ganador queda congelado. Es lo único derivado que se guarda, porque es un premio.
- **Quién la crea:** el admin del grupo.

## Otros

**Ejercicios.** El catálogo es global, porque las sesiones son del usuario y una sentadilla tiene que ser la misma en todos sus grupos. Viene precargado con los ejercicios comunes y cualquiera puede sumar uno; el nombre es único sin importar mayúsculas. Los desafíos son por grupo: arranca con sentadilla, press banca, peso muerto y press militar, con un máximo de 4.

**Validación.** Reps de 1 a 50, peso mayor a 0 y hasta 500 kg, fecha no futura, al menos una serie. Todo eso es `422`. Un ejercicio de otro grupo en el body también es `422`, no `404`: el recurso del path existe, lo inválido es el contenido.

**Borrar sesión.** Sí; editar, no. Se borra y se vuelve a cargar.

**Admin del grupo.** Es el creador: elige los desafíos, puede sacar miembros y crea campañas. Si se va, hereda el rol el miembro más antiguo.

**Reacciones.** Un set fijo: fuerza, fuego y dudoso, una por persona y por PR. Las reacciones son por grupo, porque el mismo PR aparece en el feed de cada grupo del usuario. Si más de la mitad de los miembros de un grupo lo marca como dudoso, esa serie deja de contar para los rankings de ese grupo.

**Ejercicios con lastre.** Un ejercicio del catálogo puede ser "de peso corporal", como dominadas o fondos. En esos, el peso cargado es el lastre (puede ser 0) y la carga real es peso corporal más lastre. Esa carga es la que usan el 1RM, DOTS y el absoluto.

**Libras.** Es una preferencia del perfil, solo de visualización. El formulario acepta libras y las convierte; la API y la base trabajan siempre en kg.

**"Hoy".** Lo define el servidor. La fecha de la sesión la manda el cliente.

## Panel del grupo (cuarta pasada)

Pedido: que el grupo tenga un panel con gráficos y más información, no solo rankings, ordenado en horizontal en escritorio y en vertical en el celular. Lo cerré con un auto-grill, con dashboards de fitness de referencia.

**¿Pestaña nueva o reemplazo?** El panel reemplaza al Feed en la barra y pasa a ser la portada del grupo. Los últimos PRs quedan dentro del panel, con "Ver todo" al feed completo. La barra queda así: Panel, Rankings, Entrenar al centro, Duelos y Grupo.

**¿Qué muestra?** Solo lo que sale de datos que ya tenemos:
- **Cuatro indicadores** con su curva de las últimas 8 semanas:
  - sesiones del grupo en la semana;
  - volumen de la semana;
  - PRs del mes;
  - mejor racha de constancia, con su dueño.

  Cada uno se compara con la semana o el mes anterior.
- **Barras de la semana:** cuántos miembros entrenaron cada día, de lunes a domingo, y los días tuyos marcados.
- **Medidor del objetivo del grupo:** suma de las sesiones de cada uno, topeadas en su objetivo, sobre la suma de los objetivos. El que entrena de más no tapa al que falta.
- **"Hoy toca":** el día de tu rutina que sigue al último que hiciste, con sus ejercicios y series. Cierra el issue "Sugerir qué día de la rutina toca hoy".
- **Líderes del mes:** el primero en DOTS de cada desafío.
- **La campaña activa y los últimos PRs.**

**¿Qué es el volumen?** La suma de carga × reps de las series, en kg, sin contar las que el grupo marcó como dudosas. En ejercicios con tu peso, la carga incluye el peso corporal, igual que para el 1RM.

**¿Mapa muscular, como el de la referencia?** No. Los ejercicios del catálogo no tienen músculo asignado, e inventarlo sería decoración sin datos.

**¿Dónde se calcula?** Un endpoint `GET /groups/{code}/dashboard`, con las cuentas en `backend/stats/` y TDD, igual que los rankings. "Hoy toca" se arma en el cliente con las sesiones y la rutina, que ya están en la API.

**¿Layout?** En el celular, todo en una columna con los indicadores de a dos. En escritorio, una grilla de 12 columnas:
- los cuatro indicadores en una fila;
- abajo las barras, el medidor y "Hoy toca";
- después los líderes, la campaña y los PRs.
