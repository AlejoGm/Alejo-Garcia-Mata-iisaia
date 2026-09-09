# Prompts — TP 1

Registro del proceso, en orden. Una sola conversación de Gemini Canvas.

Va sin editar, defectos incluidos.

---

## 1a — El esqueleto (Patrón 1: describir el artefacto)

```
Construí una página de registro para un servicio SaaS llamado "Nimbus".
El registro va a tener tres pasos; en este prompt construí solo el
esqueleto de la página, sin el contenido de los pasos.

Estructura:
- <header> con el nombre "Nimbus" y el subtítulo "Creá tu cuenta en tres
  pasos".
- Un indicador de progreso con los tres pasos: "Usuario", "Contraseña",
  "Plan". El paso activo se destaca; los otros dos se ven apagados.
- <main> vacío por ahora, con un título "Elegí tu nombre de usuario".
- <footer> con un <button> "Continuar", deshabilitado.

Estilo:
- SaaS moderno y prolijo: fondo blanco, tipografía sans-serif, bordes
  suaves, un color de acento azul. La página tiene que verse profesional
  y confiable.
- Ancho máximo del contenido de unos 640px, centrado.

Comportamiento:
- Estado: `paso`, con los valores "usuario", "password", "addons" y
  "confirmado". Arranca en "usuario".
- El indicador de progreso se renderiza a partir de `paso`.

Constraints:
- Un solo archivo HTML, con el CSS en un <style> y el JS en un <script>.
- Vanilla JS, sin frameworks ni dependencias externas.
```

**Qué intentaba lograr:** el marco y los constraints de empaque antes que nada, no el artefacto entero. El paso 1 es la parte cara y no quería descubrir un CDN escondido recién con 800 líneas encima.

**Qué devolvió:** la página prolija, los tres constraints respetados, y el indicador leyendo `paso`. Agregó además una función `cambiarPaso()` que no pedí.

**Qué hice con eso:** lo probé antes de aceptarlo, y los dos problemas que aparecieron estaban justo en el código que no había pedido. Están en el README.

---

## 1b — Consolidar el estado y llenar el paso usuario (Patrón 2: iterar sobre el estado)

```
Dos cosas.

Juntá el estado en un objeto `estado` y hacé una sola `render()` que
dibuje todo desde ahí. Sacá `cambiarPaso`: el título sale de render(),
no escrito en dos lados.

Y llená el paso usuario: 6 dropdowns en fila, uno por carácter. Cada
dropdown lista los 95 ASCII imprimibles (0x20-0x7E) en un orden
barajado distinto para cada uno, generado una vez al cargar.

Estado: `ordenes` (los 6 arrays), `usuario` (6 posiciones, char o null),
`abierto` (índice desplegado o null).

Click en dropdown cerrado abre y cierra el que estuviera abierto. Click
en opción la escribe y cierra. Click en el ya abierto cierra sin elegir.

Debajo, el usuario armado con "_" en los huecos. El espacio se muestra
como "␣".
```

**Qué intentaba lograr:** arreglar el render partido antes de apilar la capa nueva encima. Si construía los seis dropdowns sobre el desvío, corregirlo después era una regresión esperando.

**Por qué las tres líneas de click:** son la ida y **dos** vueltas — completar la selección y cancelarla. Nombrar solo la ida deja al modelo inventando cómo se sale del estado, y lo normal es que no haya forma de cerrar sin quedarte con un carácter que no querías.

**Qué devolvió:** el estado consolidado, las tres transiciones correctas, y los dropdowns hechos con divs en lugar de `<select>` — tenía un prompt escrito para forzar eso y no hizo falta. Verifiqué que los seis órdenes fueran independientes: la "A" cayó en las posiciones 74, 64, 19, 54, 62 y 85. Se adelantó al prompt siguiente habilitando el botón "Continuar", a medias y sin handler.
