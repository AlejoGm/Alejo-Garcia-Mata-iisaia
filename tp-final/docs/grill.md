# Grill de Gym-bro

Decisiones de diseño con su porqué. Salió en dos pasadas. Primero un auto-grill con la skill `grilling`, donde el agente se hizo las preguntas y propuso cada respuesta. Después lo repasamos pregunta por pregunta: la sección siguiente resume qué cambió en ese repaso, y el resto del documento ya está actualizado.

## Qué cambió al repasarlo

- **Fuerza relativa.** El auto-grill proponía 1RM / peso corporal, pero eso favorece al liviano porque la fuerza no escala lineal con el peso. Pasó a **DOTS**.
- **Peso corporal.** El auto-grill usaba el actual del perfil, y bajar de peso mejoraba marcas viejas. Ahora el peso viaja con cada sesión.
- **Progreso.** El auto-grill lo medía contra el récord histórico, y un veterano daba negativo casi siempre. Ahora es mes de calendario contra mes anterior.
- **Constancia.** El auto-grill contaba días entrenados, lo que premia al que va más, no al que cumple. Ahora es cumplimiento de un objetivo semanal propio.
- **Agregados.** Ranking absoluto, dos tipos de PR, ranking semanal (en lugar del cartel de la vergüenza), rutinas del grupo con carga guiada, y campañas con ganador (en lugar de temporadas mensuales).
- **Descartado.** El PIN por miembro: se queda solo con nickname.

## Producto

**¿Qué es?** Un lugar donde un grupo de amigos registra lo que entrena, se motiva viendo lo que hace el otro y compite de forma justa. Cada uno puede seguir su rutina o la misma que su bro; los rankings no dependen de la rutina.

**¿Cómo se parte en versiones?**
- **v1:** carga libre y rankings.
- **v1.1:** rutinas con carga guiada, y constancia.
- **v2:** lo social (duelos, reacciones, gráficos).
- **v3:** lo que exige cuentas o cambia el modelo (campañas, validación social).

**¿Tiempo real, notificaciones, app nativa?** No. Polling cada 30 segundos desde la v2, y una web que se usa desde el celular.

## Identidad

**¿Cómo se identifica cada uno?** Solo con nickname dentro del grupo, sin contraseña ni PIN. El riesgo está asumido: cualquiera con el código puede cargar o borrar a nombre de otro. Entre amigos se acepta.

**¿Cuentas?** En la v3, cuando haga falta estar en varios grupos.

**¿Qué se pide al unirse?** Nickname, sexo (para DOTS), peso corporal y objetivo semanal de sesiones.

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

**Ejercicios.** Por grupo. El grupo arranca con sentadilla, press banca, peso muerto y press militar como desafíos, con un máximo de 4: el quinto devuelve `409`.

**Validación.** Reps de 1 a 50, peso mayor a 0 y hasta 500 kg, fecha no futura, al menos una serie. Todo eso es `422`. Un ejercicio de otro grupo en el body también es `422`, no `404`: el recurso del path existe, lo inválido es el contenido.

**Borrar sesión.** Sí; editar, no. Se borra y se vuelve a cargar.

**Admin del grupo.** Existe desde la v2 y es el creador: elige los desafíos, puede sacar miembros y crea campañas.

**Reacciones.** Desde la v2, con un set fijo: fuerza, fuego y dudoso. En la v3, un PR que más de la mitad del grupo marca como dudoso deja de contar.

**Ejercicios con lastre y libras.** Los dos en la v3.

**"Hoy".** Lo define el servidor. La fecha de la sesión la manda el cliente.
