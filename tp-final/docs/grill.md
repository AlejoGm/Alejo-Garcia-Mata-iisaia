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
- **"PR de peso":** más kilos que nunca en ese ejercicio.
- **"PR de reps":** los mismos kilos de tu mejor serie, con más reps. Antes contaba como "PR de peso" y el gym-bro lo leyó como un error, así que en la quinta pasada lo separé. Cuenta igual que antes; solo cambia la etiqueta.
- **"PR de 1RM":** subió el 1RM estimado pero no el peso.

Si una serie cumple más de una condición, se muestra "PR de peso" o "PR de reps", no "PR de 1RM". La primera serie de un ejercicio es línea base, no PR. Los PRs se calculan, no se guardan.

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

## Más completa (quinta pasada)

Pedido: darle otra vuelta a la app para que sea más completa. Lo cerré con un auto-grill, partiendo de qué hace un gym-bro que la app todavía no cubre.

**¿Qué falta?**
- **En el gimnasio:** saber qué levantar para romper la marca, y cuántos discos poner en la barra.
- **Mirar al otro:** hoy un bro aparece solo como fila de una tabla. Falta su perfil y un cara a cara.
- **Logros que no dependan de ganarle a nadie:** medallas.
- **Cerrar la semana:** quién fue el que más entrenó, levantó y rompió marcas.
- **Mis stats:** ver la constancia de un vistazo, como un calendario.
- **Lo pendiente:** agrupar en el feed los PRs de una sesión, confirmar antes de cancelar un reto, e instalarla en el celular.

**¿Qué sugiere el "objetivo para PR"?** Las dos series más chicas que la regla de PRs cuenta como récord, y se cargan con un toque:
- **Más reps:** tu mejor carga, con una rep más que tu mejor serie con esa carga.
- **Más peso:** tu mejor carga más un salto (2,5 kg o 5 lb), con las reps justas para superar también tu mejor 1RM estimado.

Se calcula sobre todo tu historial, igual que los PRs. En ejercicios con tu peso no hay sugerencia: la carga depende del peso corporal del día. La regla vive en `backend/stats/` con TDD y llega en la respuesta de `/last`.

**¿Calculadora de discos?** Sí, en ejercicios con barra: "por lado: 20 + 10 + 2,5" debajo del peso. Barra de 20 kg o 45 lb, discos comunes de gimnasio. Qué ejercicio usa barra lo dice el catálogo, sin columna nueva en la base, así una base existente sigue sirviendo. Los ejercicios que agrega un usuario no muestran discos.

**¿Perfil del bro?** Tocar un nombre en rankings, panel, feed o miembros lleva a su perfil:
- su semana contra su objetivo y su racha;
- sus medallas;
- el **cara a cara**: en cada ejercicio que hicieron los dos en los últimos 6 meses, el mejor 1RM de cada uno y quién gana en DOTS, con un marcador total;
- sus últimas sesiones, con el día de rutina, las series y los PRs.

Se cuentan las series del grupo, sin las dudosas, igual que en los rankings. Las sesiones de un miembro ya se veían por el feed y por "la última vez", así que mostrarlas no abre nada nuevo.

**¿Qué medallas?** Hitos fijos, cada uno con el día en que se ganó:

| Medalla | Condición |
|---|---|
| Primera sesión | una sesión |
| 10, 50 y 100 sesiones | días distintos entrenados |
| 4 y 12 semanas | semanas cerradas seguidas cumpliendo el objetivo |
| 10 PRs | PRs acumulados |
| Banca con tu peso | press banca con carga igual o mayor a tu peso del día |
| Sentadilla 1,5× | sentadilla con 1,5 veces tu peso del día |
| Peso muerto 2× | peso muerto con el doble de tu peso del día |
| Tonelada | 10 000 kg de volumen en una sesión |

Las de fuerza son relativas al peso, para que no las ganen solo los pesados. Las medallas son personales: se calculan con todo tu historial, no con lo que filtra cada grupo. Se ven en tu perfil, en el del bro y en el panel, que muestra las ganadas en los últimos 14 días.

**¿Cierre de la semana?** Una tarjeta del panel, "La semana pasada", sobre la última semana cerrada:
- más días entrenados;
- más volumen;
- más PRs;
- quiénes cumplieron su objetivo.

Un empate muestra a todos los empatados. No suma puntos a nada: es para el chat.

**¿Calendario?** En mis stats, las últimas 26 semanas en una grilla de días, con la intensidad según la cantidad de series. Es lo que más rápido muestra si uno viene constante.

**¿Volumen por músculo?** Al principio quedó afuera, como en el panel, porque hacía falta asignarle un músculo a cada ejercicio. Después Alejo pidió sumarlo:
- **Músculo de cada ejercicio.** Uno solo, el principal, asignado en el catálogo con nueve grupos: pecho, espalda, hombros, bíceps, tríceps, cuádriceps, isquios y glúteos, gemelos y core. Va en el código y no en una columna, así una base existente sigue sirviendo. Un ejercicio que agrega un usuario cae en "Otros".
- **Qué se mide.** Series por semana de cada músculo, que es como se cuenta el volumen para ganar músculo. Se muestra el promedio de las últimas 4 semanas cerradas y lo que va de la semana en curso.
- **Dónde.** En mis stats, con la guía común de 10 a 20 series por semana como referencia.

**¿Feed agrupado?** Una tarjeta por sesión: la persona, el día, y cada PR en su línea con sus reacciones. Las reacciones siguen siendo por PR, porque el "dudoso" excluye una serie, no una sesión.

**¿Cancelar un reto?** Pide un segundo toque, como "Confirmar" en un peso sospechoso.

**¿Instalable?** Un manifest con ícono y color, para "Agregar a la pantalla de inicio" y abrirla sin la barra del navegador. Sin service worker: el borrador local ya cubre cortes de señal, y el PRD deja afuera la sincronización en segundo plano.

## Más juego (sexta pasada)

Pedido: que la app se sienta más como un juego. No con features nuevas, sino con experiencia de uso. El ejemplo de Alejo: que al cargar una serie te muestre cómo te fue contra el resto del grupo. Lo cerré con un auto-grill.

**¿Qué hace que algo se sienta juego?** Respuesta inmediata a lo que hacés, saber contra quién vas, y un cierre que celebra. Hoy todo eso pasa tarde: la posición en el grupo se ve en Rankings, el PR aparece recién al terminar y el resumen es una lista. La idea es llevar esa respuesta al momento de cargar.

**¿Qué ves al guardar una serie?** Una tarjeta corta, abajo y cerca del pulgar, que dura unos segundos:
- **PR:** si la serie es un récord, se celebra al instante con animación y vibración, en lugar de esperar al final.
- **Tu lugar en el grupo** en ese ejercicio: "3º de 7 en Press banca este mes".
- **A quién pasaste** con esa serie: "¡Pasaste a Tomi!".
- **A quién tenés adelante y qué serie te falta** para pasarlo, a tus mismas reps: "Para pasar a Nacho: 85 × 6". Un toque la carga en los campos, como "Para PR".
- **Si sos el primero:** "Primero del grupo en Press banca".

**¿Contra qué se compara?** Contra el ranking de fuerza del mes en DOTS: el mismo de Rankings y de "Líderes del mes", así la tarjeta no contradice a las tablas. Lo que te falta se dice en kilos y reps, a tu peso del día, porque nadie piensa en DOTS en el gimnasio. Con más de 10 reps no hay 1RM estimado y no hay comparación; la tarjeta lo dice.

**¿Dónde se calcula?** En el servidor, con un endpoint que recibe la serie sin guardarla y devuelve el PR, el lugar antes y después, a quién pasaste y la serie para pasar al siguiente. Las reglas (posición, inversa de Epley para la serie objetivo) van a `backend/stats/` con TDD. El cliente no duplica fórmulas. Si no hay señal, la serie se guarda igual en el borrador y la tarjeta no aparece.

**¿Cómo cierra la sesión?** Como el final de un nivel:
- los números (series, volumen, PRs) suben animados;
- **"Subiste en el grupo":** por ejercicio, de qué lugar a qué lugar pasaste y a quién pasaste en la sesión;
- **medalla nueva**, si la sesión desbloqueó alguna;
- tu semana: "Día 3 de 4" y la racha.

**¿Animaciones?** Cortas y con sentido:
- los números rebotan al tocar + o −;
- "Guardar serie" muestra un tilde;
- un PR o una medalla nueva largan papelitos (confeti);
- el celular vibra en los mismos casos.

Con "reducir movimiento" activado en el sistema, no hay animaciones.

**¿Qué queda afuera?** Puntos de experiencia, niveles y sonidos. Son features nuevas con reglas propias, y el pedido es que lo que ya existe se sienta mejor.

**Después de probarlo, Alejo marcó que la carga confundía:** muchos botones, y no se sabía si "Terminar" terminaba la serie o el entrenamiento. Se rehízo con una regla: una sola acción grande por momento.
- **El botón principal dice qué hace:** "✓ Hice la serie 2 de 5". Pasa a "Confirmar 110 kg" con un peso raro, a "Guardar corrección" al editar, y a "Terminar entrenamiento" recién cuando la rutina está completa.
- **"Terminar entrenamiento" vive arriba,** junto al progreso ("6 de 22 series"), y pide confirmación si faltan series. Ya no está al lado de guardar.
- **Modo foco:** mientras cargás se esconde la barra de pestañas, para que no compitan dos botones verdes.
- **El descanso es un texto, no un botón:** "Descanso 1:28", con "+30 s" y "Saltar" como enlaces.
- **Una sola fila "Tocá para cargar"** con los objetivos de PR y el de pasar al siguiente, y puntos que muestran qué series del ejercicio ya hiciste.

## Cuentas propias (séptima pasada)

Al apagar Auth0 (Google no anda desde el celular sin HTTPS), la app volvió a entrar solo con un nombre, y cualquiera entraba como cualquiera. Alejo pidió login y registro.

- **Usuario y contraseña propios.** Es el modo por defecto sin Auth0. Con Auth0 configurado se sigue entrando con Google.
- **Contraseña con scrypt,** de la biblioteca estándar, con sal propia. No suma dependencias.
- **Token de sesión al azar.** En la base se guarda su sha256, no el token. "Cerrar sesión" lo borra. No vence: para un TP local no hace falta.
- **Mismo `sub` que el modo desarrollo** (`dev|usuario`). Registrarse con un nombre que ya tenía historia se queda con ese usuario. Así Alejo recupera lo suyo y se puede entrar como cualquiera de los datos de prueba registrándose con su nombre. En una app pública eso sería un agujero; acá es a propósito.
- **Los tokens `dev:` se rechazan** con cuentas propias. Si no, la contraseña no protegería nada. Los tests y los scripts de datos fuerzan el modo `dev` dentro de su propio proceso.

**Comparar en el panel.** A Alejo le gustaban más las gráficas de mis stats que las tablas, pero quería verlas contra el resto. El panel suma "Comparar":
- **Una línea por miembro,** con un color fijo para cada uno. Se prenden y apagan tocando su nombre. Arranca con vos y los tres que mejor vienen.
- **Fuerza por mes** en el ejercicio que elijas, con el mismo período que en mis stats. Se puede ver en DOTS (por defecto, porque es la comparación justa), en 1RM estimado o en **peso máximo**. Este último lo pidió Alejo: el peso más alto levantado, tal cual, sin cálculos. También se elige entre el mejor del mes y el mejor de cada semana. Se probó sesión por sesión, pero cada uno entrena en días distintos y no se comparan bien; la semana pone a todos en las mismas columnas.
- **Días por semana** en las últimas 12 semanas, para ver la constancia de todos de un vistazo.

Mis stats sigue igual para lo personal (peso corporal, series por músculo, calendario y medallas).
