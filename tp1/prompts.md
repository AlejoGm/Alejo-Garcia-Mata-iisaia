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
