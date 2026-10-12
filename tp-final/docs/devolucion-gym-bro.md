# Devolución del agente gym-bro

Prueba de punta a punta con el sub-agente `gym-bro` (`.claude/agents/gym-bro.md`). Hizo de "Nico", que entrena 4 veces por semana. Usó la app solo por lo que veía en pantalla, sin leer código, sobre un grupo de demo con 8 semanas de historia (`scripts/seed_demo.py`):
- **En el gimnasio:** celular de 375×812 y una mano, para cargar una sesión Push con errores a propósito, una serie extra y un reload a mitad de carga.
- **En casa:** celular y después escritorio de 1280×800, para revisar rankings, feed, duelos, campañas, mis stats y el perfil.

## Lo que funcionó

- **Entrada y carga.** Se entra rápido, y el código de grupo se pasa solo a mayúsculas. Repetir una serie es 1 toque.
- **Carga guiada.** Los chips de avance y el paso automático al ejercicio siguiente se entienden.
- **Peso corporal.** Los ejercicios de peso corporal usan lastre, y no te deja cerrar la sesión sin peso corporal.
- **Borrador.** Sobrevive al reload.
- **Resumen y feed.** El resumen muestra los PRs, y las reacciones andan.
- **Campañas.** Los puntos cuadran con los rankings.
- **Libras.** Se respetan en todas las vistas.
- **Filtros.** Los de rankings se recuerdan.

## Lo que encontró, por gravedad

- **"Guardar serie" no está en la zona del pulgar.** La tapaba a medias la barra con "Descartar / Terminar". Lo destructivo quedaba más cerca del pulgar que lo que más se usa.
- **El campo de peso no selecciona al tocarlo.** Escribir "60" sobre "22,5" dejaba **2260,5**, y se guardaba sin aviso.
- **Corregir una serie es caro.** No hay forma de editarla, y la "×" borra sin deshacer. Así terminó borrando una serie buena.
- **Serie extra.** En un ejercicio completo decía "Serie 4 de 4" y saltaba al siguiente ejercicio, que ya estaba completo.
- **Peso corporal desparejo.** Lo pedía de nuevo en la segunda sesión del día.
- **Constancia y progreso vacíos.** Constancia salía siempre en "sin datos", y progreso quedaba vacío con 6 meses o Todo.
- **"Sesiones" que en realidad son días.** "La semana" contaba días; "Mis stats" contaba todas las sesiones del período, no las del ejercicio.
- **DOTS sin explicar.** Lo dedujo por el texto del perfil.
- **Demasiados PRs.** En la primera sesión cada serie más pesada contaba como PR, y el feed se llenaba de tarjetas iguales.
- **Duelos.** No había confirmación al retar, el formulario se reseteaba y un reto pendiente no se podía cancelar.
- **Detalles.**
  - En libras la barra arrancaba en 44,1 lb.
  - Coma decimal en los campos y punto en las listas.
  - La rutina se abría directo en el editor.
  - Las campañas estaban escondidas.
  - El historial no decía qué día de la rutina era.
  - En escritorio, la barra de pestañas se estiraba a 1280 px.
  - No había timer de descanso.

El informe original con las mediciones (toques por serie, pasos para reproducir) quedó en la conversación del agente. Este archivo resume lo que se tomó.

## Qué se cambió

Todo en el PR que cierra el issue de esta prueba:
- **Barra inferior fija** con "Guardar serie" grande. "Terminar" va al lado y "Descartar" pasa a la tarjeta de la sesión.
- **Campos numéricos.** Seleccionan todo al tocarlos. Un peso de más de 1,5 veces tu última vez, o de más de 300 kg, pide un segundo toque.
- **Borrar serie** con "Deshacer". Tocar una serie la carga de nuevo para corregirla.
- **Serie extra.** Dice "(extra)" y no salta al ejercicio siguiente. Al completar uno, avanza al próximo incompleto.
- **Timer de descanso** de 90 s después de cada serie, que vibra al terminar.
- **Peso corporal.** Se refresca después de guardar cada sesión.
- **Constancia.** El primer objetivo rige también para las sesiones cargadas antes.
- **Progreso.** En períodos largos compara el primer mes con datos contra el último. Con "Mes" sigue siendo contra el mes anterior.
- **PRs.** Se comparan contra las sesiones anteriores, con a lo sumo uno por ejercicio y sesión.
- **Textos.**
  - DOTS explicado en una línea.
  - "Días" en la semana y "Sesiones con este ejercicio" en mis stats.
  - Campañas visibles arriba de Rankings.
  - Números con coma decimal.
- **Duelos.** Confirmación al retar, el formulario se mantiene y el retador puede cancelar un reto pendiente.
- **Libras.** La barra arranca en 45 lb.
- **Rutinas.** Se ven en modo lectura, con "Editar" aparte, y el historial muestra el día.

## Segunda pasada

Volvió a probar como usuario nuevo. Sobre 14 puntos: 11 arreglados y 3 a medias, que se resolvieron en el PR siguiente:
- **Corregir una serie:** queda en su lugar con un aviso "Editando serie N", y no reinicia el timer.
- **El campo de peso:** selecciona todo también con tecleo rápido.
- **"0 kg":** en ejercicios con tu peso ahora dice "peso corporal + lastre".

El mes en curso quedó marcado como parcial en rankings y gráficos.

Lo pendiente quedó en issues:
- La vista de escritorio a dos columnas.
- Agrupar en el feed los PRs de una misma sesión.
- Que la app sugiera qué día de la rutina toca hoy.
- Confirmar antes de cancelar un reto.

## Tercera pasada: lo nuevo de la quinta ronda

Probó como "nico", un usuario nuevo que se une al grupo de demo. Cargó dos sesiones (ayer y hoy), usó "Para PR", se equivocó a propósito, y en casa recorrió todo en el celular y en escritorio.

**Mediciones.** La primera sesión, sin historial, le llevó unos 2,6 toques por serie. La segunda, con "Para PR" y los valores precargados, 1,8. Cargar una serie nueva con "Para PR" son 2 toques: el chip y Guardar.

**Lo que más le gustó:** "Para PR", los discos por lado, el cara a cara ("Vos 0 – 3 Bruno"), el feed agrupado y "La semana pasada".

**Qué se cambió:**
- **La barra fija tapaba Reps al abrir la carga.** Los números suben arriba de todo. "Para PR", los discos y "La última vez" pasan abajo, cerca del pulgar. El fondo de la página crece con la barra cuando aparece el descanso o un aviso, y la tarjeta de la sesión muestra una flecha que dice que se abre.
- **Campo de peso.** Cada toque selecciona todo, también con el campo ya activo. Un peso absurdo ya no dibuja 800 discos.
- **Avisos.** "El máximo es 500 kg" se va al corregir el peso, la etiqueta dice "Editando serie 3" mientras se edita, y "Deshacer" dura 10 segundos.
- **"Para PR"** dice qué es cada chip ("+1 rep" y "+peso") y marca el elegido.
- **Ejercicios con tu peso.** El feed, el panel y el resumen muestran la carga total y "peso corporal + 5 kg", no un "0 kg" gigante.
- **Cara a cara.** Cuando gana el que levanta menos kilos, aparece una línea que explica que DOTS ajusta por peso corporal y sexo.
- **Duelos.**
  - "Retar" desde un perfil llega con ese rival marcado, en DOTS y en el ejercicio más parejo.
  - Con quien ya tenés un reto aparece "Pendiente" o "En curso", en lugar de un botón que fallaba en silencio.
  - Los duelos en juego van arriba.
  - El ejercicio arranca en el que más cargaste, no en Sentadilla.
- **Entrenar** marca con "Toca hoy" el día de la rutina que sigue.
- **Detalles.**
  - Fechas legibles en todos lados, con el año solo si no es el actual.
  - Las medallas ganadas mantienen la descripción.
  - Los nombres linkeados se ven subrayados.
  - Los gráficos no exageran diferencias de 1 kg y no se agrandan de más en escritorio.

**Lo que no se cambió:**
- **"PR de peso" con el mismo peso y más reps.** Tocaba una decisión del grill, así que lo consulté: Alejo eligió sumar "PR de reps". Se hizo en el PR siguiente.
- **Fondos con más de 10 reps no tiene 1RM ni objetivo para PR.** Es a propósito: Epley no es confiable con más de 10 reps, y en ejercicios con tu peso la carga depende del peso del día.
- **"Peso muerto" no se compite en el demo.** La rutina del demo tiene peso muerto rumano y el desafío es peso muerto convencional. Es un tema de los datos de prueba, no de la app.
- **Quedaron en issues:**
  - [Mostrar el progreso hacia cada medalla](https://github.com/AlejoGm/Alejo-Garcia-Mata-iisaia/issues/54)
  - [Constancia sin datos en la primera semana](https://github.com/AlejoGm/Alejo-Garcia-Mata-iisaia/issues/55)
  - [Rankings en escritorio: que se entienda qué filtra el período](https://github.com/AlejoGm/Alejo-Garcia-Mata-iisaia/issues/56)
