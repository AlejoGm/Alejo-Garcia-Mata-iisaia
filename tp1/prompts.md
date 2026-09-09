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

**Qué intentaba lograr:** fijar el marco y los constraints de empaque antes que
nada, y no el artefacto entero. El paso 1 de la página es la parte cara —
seis dropdowns con la tabla ASCII barajada — y no quería descubrir que el
modelo había partido el archivo o metido un CDN recién cuando ya hubiera 800
líneas encima. El esqueleto es barato de tirar.

También quería que el estado `paso` existiera desde el primer output, con los
cuatro valores nombrados, para que los prompts siguientes tuvieran dónde
colgarse en lugar de inventar navegación cada uno por su cuenta.

**Qué devolvió:** la página completa y prolija, con los tres constraints
respetados: un solo archivo, sin dependencias externas, CSS en `<style>` y JS
en `<script>`. El indicador de progreso se renderiza desde `paso` con una
función `renderProgress()` que agrega y saca la clase `.active`, leyendo el
nombre del paso desde un atributo `data-step` en el DOM.

Agregó además una función `cambiarPaso(nuevoPaso)` que yo no había pedido.

**Qué hice con eso:** lo probé antes de aceptarlo, y ahí aparecieron dos
problemas — los dos en el código que no había pedido. Están detallados en el
README, porque son lo más interesante de esta iteración.

Lo que verifiqué:

- Cero dependencias externas: ningún `<script src>`, `<link href>` ni `@import`.
- Estado inicial: `paso` es `"usuario"` y el chip destacado es el de Usuario.
- Seteando `paso = "password"` a mano y llamando a `renderProgress()`, el
  indicador acompaña. El título del `<main>`, no.
- Con `cambiarPaso("confirmado")`, que es uno de los cuatro valores que yo
  mismo declaré, no queda ningún paso destacado y el título se queda pegado
  en el anterior.

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

**Qué intentaba lograr:** dos cosas en un prompt, a propósito. Primero arreglar
el desvío que había detectado en el 1a — el render partido en dos lugares — y
recién después apilar la capa nueva encima. Si construía los seis dropdowns
sobre el render roto, arreglarlo después iba a ser una regresión esperando.

Las tres líneas de click son la ida y **dos** vueltas distintas: completar la
selección, y cancelar sin elegir. Nombrar solo la ida deja al modelo inventando
cómo se sale del estado, y lo más común es que no haya forma de cerrar el
dropdown sin quedarse con un carácter que no querías.

**Qué devolvió:** el estado consolidado en un objeto `estado`, una sola
`render()` que dibuja desde ahí, y los seis dropdowns funcionando con las tres
transiciones correctas.

Lo interesante es lo que hizo sin que se lo pidiera: **construyó los dropdowns
con divs en lugar de `<select>` nativo**. Yo tenía preparado un prompt para
forzar ese cambio y no hizo falta. Con `<select>` el ejercicio se caía solo,
porque el select del navegador permite saltar a una opción tipeando su primera
letra y el orden barajado dejaba de importar.

Agregó también dos cosas que no pedí: cerrar el dropdown al clickear fuera, y
habilitar el botón "Continuar" cuando los seis caracteres están elegidos.

**Qué hice con eso:** lo acepté, pero verificando primero lo que importaba:

- Los seis órdenes son independientes de verdad. La letra "A" cayó en las
  posiciones 74, 64, 19, 54, 62 y 85. Si hubieran salido iguales, el barajado
  estaba compartido y la dificultad se evaporaba después del primer dropdown.
- Cero `<select>` y cero `<datalist>` en todo el archivo.
- Las tres transiciones de click andan: abrir cierra el que estuviera abierto,
  elegir escribe y cierra, y volver a clickear el abierto lo cierra sin tocar
  `usuario`.
- 570 nodos `.dropdown-item` viven en el DOM permanentemente — 95 por dropdown,
  los seis renderizados aunque estén cerrados.

Y dos problemas que quedan abiertos, anotados en el README: el objeto `titulos`
sigue sin cubrir el cuarto valor de `paso`, y el botón "Continuar" se habilita
pero todavía no lleva a ningún lado.
