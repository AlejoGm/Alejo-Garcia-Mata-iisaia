# Grill de Gym-bro

Preguntas que había que cerrar antes del PRD, cada una con la decisión tomada. Primero las del producto completo; después las que hacen falta para construir la v1. Hecho con la skill `grilling` en modo auto: el agente se hizo las preguntas y propuso cada respuesta.

## Producto

**¿Qué es el producto terminado?** Un lugar donde un grupo de amigos registra lo que entrena y compite de forma justa: rankings, duelos, un feed con reacciones y temporadas mensuales. No es una app de rutinas ni de nutrición.

**¿Cómo se parte en versiones?** Por lo que hace falta para que el grupo compita:
- **v1:** carga y rankings.
- **v2:** lo social (duelos, reacciones, gráficos).
- **v3:** lo que exige cuentas o cambia el modelo de datos.

**¿Cuentas de usuario?** Sí, en v3. Hacen falta para que una persona esté en varios grupos y para que nadie cargue a nombre de otro. Hasta entonces alcanza con nickname y código de grupo.

**¿Quién administra el grupo?** En v1, cualquiera. En v2 el creador pasa a ser admin: elige los desafíos y puede sacar miembros.

**¿Duelos?** En v2. Uno contra uno, en un ejercicio, durante 7 días. Gana el que más mejora en porcentaje sobre su mejor 1RM previo. El retado acepta o rechaza, y cada par puede tener un solo duelo activo.

**¿Reacciones en el feed?** En v2, con un set fijo: fuerza, fuego y dudoso. No hay comentarios libres; eso sería un chat y ya tienen uno.

**¿Qué pasa con una carga absurda que pasa la validación?** En v3 entra la validación social. Si la mayoría del grupo marca un PR como dudoso, deja de contar para los rankings. En v1 y v2 solo la frena el rango de validación.

**¿Historial de peso corporal?** En v2, con fecha. La fuerza relativa pasa a usar el peso vigente a la fecha de cada serie, no el actual. Si no, bajar de peso mejora retroactivamente marcas viejas.

**¿Gráficos?** En v2: la evolución del 1RM estimado por ejercicio y la del peso corporal.

**¿Cartel de la vergüenza?** En v2. Muestra a quien no cargó ninguna sesión en la semana en curso, a partir del jueves.

**¿Plantillas de rutina?** En v2. Guardan una sesión tipo para cargarla en dos clics.

**¿Temporadas?** En v3. Los rankings se reinician cada mes y queda guardado el campeón de cada tabla.

**¿Ejercicios con peso corporal, como dominadas?** En v3. Se marcan como "con lastre" y el 1RM se calcula sobre peso corporal más lastre.

**¿Libras?** En v3, como preferencia de visualización. Internamente todo queda en kg.

**¿Tiempo real?** No. El feed y los rankings se actualizan al recargar o cada 30 segundos (polling) desde v2.

**¿Notificaciones y app móvil nativa?** Quedan fuera del producto. Es una web que se usa desde el celular.

## v1: identidad y grupos

**¿Cómo se identifica cada uno?** Nickname por grupo, sin contraseña. El código del grupo funciona como secreto compartido. Cualquiera con el código puede cargar a nombre de otro; entre amigos se acepta hasta que lleguen las cuentas.

**¿Una persona en varios grupos?** No hasta v3. El mismo nickname en otro grupo es otro miembro.

**¿Crear grupo y unirse son un solo paso?** No. `groups` y `members` son recursos separados; la página encadena las dos llamadas.

**¿Cómo es el código?** Seis caracteres en mayúscula, sin los ambiguos (0, O, 1, I). Lo genera el servidor.

## v1: ejercicios

**¿Catálogo global o por grupo?** Por grupo. Al crearlo se cargan sentadilla, press banca, peso muerto y press militar, los cuatro como desafío.

**¿Cuántos desafíos?** Máximo 4. Marcar el quinto devuelve `409`.

## v1: series y sesiones

**¿Qué fórmula de 1RM?** Epley: `peso × (1 + reps / 30)`, y con 1 rep es el peso. Las series de más de 10 reps se guardan pero no cuentan para el 1RM, porque la estimación se degrada.

**¿Qué se valida?** Reps de 1 a 50, peso mayor a 0 y hasta 500 kg, fecha no futura, al menos una serie. Todo eso es `422`.

**¿Un ejercicio de otro grupo en el body?** `422`, no `404`. El recurso del path existe; lo inválido es el contenido.

**¿Se puede borrar una sesión?** Sí. Sin borrado, un 500 por error de tipeo arruina el ranking para siempre. Editar no: se borra y se vuelve a cargar.

## v1: PRs y feed

**¿Qué es un PR?** Una serie cuyo 1RM estimado supera al mejor anterior del mismo miembro en ese ejercicio, en orden cronológico por fecha de sesión. La primera serie de un ejercicio es la línea base, no un PR.

**¿Se guardan o se calculan?** Se calculan. Si se guardaran, borrar una sesión o cargar una atrasada dejaría el feed inconsistente. Cuando lleguen las reacciones en v2, se cuelgan de la serie, no de un evento de PR guardado.

## v1: rankings

**¿Qué peso corporal se usa?** El actual del perfil. En v2 pasa al peso vigente a la fecha de la serie.

**Fuerza relativa.** Por ejercicio de desafío: mejor 1RM estimado histórico dividido por el peso corporal.

**Progreso.** Por ejercicio, el mejor 1RM de los últimos 28 días contra el mejor de antes de esa ventana. Se promedia el porcentaje entre los ejercicios que tienen datos en las dos. Quien no tiene datos comparables aparece como "sin datos".

**Constancia.** Días entrenados en los últimos 28 días y racha de semanas seguidas con al menos una sesión. La semana en curso sin sesión todavía no corta la racha.

**¿"Hoy" lo define quién?** El servidor. La fecha de la sesión la manda el cliente, porque se puede cargar la de ayer.

## Exposición de la idea

**¿Qué se muestra?** Un corte de la v1: crear o unirse a un grupo, cargar una sesión y ver el ranking de fuerza relativa. Está hecho.
