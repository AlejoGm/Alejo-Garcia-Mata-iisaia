# Grill del MVP

Preguntas que había que cerrar antes del PRD, cada una con la decisión tomada. Hecho con la skill `grilling` en modo auto: el agente se hizo las preguntas y propuso cada respuesta.

## Identidad y grupos

**¿Login o nickname?** Nickname por grupo, sin contraseña. El código del grupo funciona como secreto compartido. Cualquiera con el código puede cargar a nombre de otro; entre amigos se acepta. Queda como pregunta para la devolución.

**¿Una persona en varios grupos?** No en el MVP. El mismo nickname en otro grupo es otro miembro.

**¿Crear grupo y unirse son un solo paso?** No. `groups` y `members` son recursos separados; la página encadena las dos llamadas.

**¿Cómo es el código?** Seis caracteres en mayúscula, sin los ambiguos (0, O, 1, I). Lo genera el servidor.

## Ejercicios

**¿Catálogo global o por grupo?** Por grupo. Al crearlo se cargan sentadilla, press banca, peso muerto y press militar, los cuatro como desafío.

**¿Cuántos desafíos?** Máximo 4. Marcar el quinto devuelve `409`.

**¿Ejercicios con peso corporal, como dominadas?** Fuera del MVP. Todo se carga como peso externo.

## Series y sesiones

**¿Qué fórmula de 1RM?** Epley: `peso × (1 + reps / 30)`, y con 1 rep es el peso. Las series de más de 10 reps se guardan pero no cuentan para el 1RM, porque la estimación se degrada.

**¿Qué se valida?** Reps de 1 a 50, peso mayor a 0 y hasta 500 kg, fecha no futura, al menos una serie. Todo eso es `422`.

**¿Un ejercicio de otro grupo en el body?** `422`, no `404`. El recurso del path existe; lo inválido es el contenido.

**¿Se puede borrar una sesión?** Sí. Sin borrado, un 500 por error de tipeo arruina el ranking para siempre.

## PRs y feed

**¿Qué es un PR?** Una serie cuyo 1RM estimado supera al mejor anterior del mismo miembro en ese ejercicio, en orden cronológico por fecha de sesión. La primera serie de un ejercicio es la línea base, no un PR.

**¿Se guardan o se calculan?** Se calculan. Si se guardaran, borrar una sesión o cargar una atrasada dejaría el feed inconsistente.

## Rankings

**¿Qué peso corporal se usa?** El actual del perfil, no el del día de la sesión. Es más simple y alcanza para amigos.

**Fuerza relativa.** Por ejercicio de desafío: mejor 1RM estimado histórico dividido por el peso corporal.

**Progreso.** Por ejercicio, el mejor 1RM de los últimos 28 días contra el mejor de antes de esa ventana. Se promedia el porcentaje entre los ejercicios que tienen datos en las dos. Quien no tiene datos comparables aparece como "sin datos".

**Constancia.** Días entrenados en los últimos 28 días y racha de semanas seguidas con al menos una sesión. La semana en curso sin sesión todavía no corta la racha.

**¿"Hoy" lo define quién?** El servidor. La fecha de la sesión la manda el cliente, porque se puede cargar la de ayer.

## Alcance de mañana

**¿Qué se muestra en la exposición?** Un corte vertical: crear o unirse a un grupo, cargar una sesión y ver el ranking de fuerza relativa. Progreso, constancia y feed vienen después.
