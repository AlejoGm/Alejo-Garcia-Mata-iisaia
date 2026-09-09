# TP 1 — Nimbus, el registro que no te deja registrarte

Una página de registro de un servicio SaaS. Se ve profesional, no esconde nada,
y completar los tres pasos lleva varios minutos.

## Cómo se ejecuta

Doble click en `index.html`. Un solo archivo, sin dependencias.

## Qué me propuse construir

Una bad UI donde la hostilidad esté a la vista y aun así duela. El usuario se
arma carácter por carácter desde seis dropdowns que listan los 95 caracteres
ASCII imprimibles, cada uno en su propio orden barajado: la tabla completa está
ahí, ordenada de la única forma que no ayuda. La contraseña revela sus reglas de
a una. Y el plan es una grilla de addons tipo *Lights Out*, donde apagar uno
prende a sus vecinos y quedarse en el plan gratis es un puzzle.

Lo que me interesaba del último paso es la inversión: en cualquier página normal
sumás lo que querés, acá tenés que restar todo, y restar prende cosas.

## Decisiones que tomé yo

**Prompts chicos en vez de uno grande.** Son tres mecánicas independientes.
Pedirlas juntas me dejaba sin forma de saber cuál de las tres había roto qué.
Cada prompt deja algo verificable antes de apilar el siguiente.

**Corregir el desvío antes de agregar la capa nueva.** Cuando el render quedó
partido en dos lugares, funcionaba igual y podía seguir. Lo arreglé primero,
para no construir seis dropdowns encima de algo que después iba a tener que
rehacer.

**Nombrar la transición de cancelar.** Abrir y elegir son obvias; la que importa
es la tercera. Si solo nombrás la ida, el modelo decide por su cuenta cómo se
sale del estado, y lo normal es que no haya forma de cerrar el dropdown sin
quedarte con un carácter que no querías. Eso vuelve un error irreversible, que
es una crueldad distinta de la que busco: quiero que cueste, no que no se pueda.

**Dropdowns con divs, no `<select>`.** El `<select>` nativo salta a una opción
cuando tipeás su primera letra. Con eso el orden barajado deja de importar y el
paso se resuelve en cinco segundos. Tenía el prompt escrito para prohibirlo y no
lo necesité: el modelo eligió divs solo.

## Qué salió mal y cómo lo corregí

**El código que no pedí fue el que trajo los bugs.** Pedí un esqueleto y llegó
además una función "para más adelante" que escribía el título del `<main>`,
duplicando un texto que ya estaba en el HTML. Dos fuentes de verdad para la
misma línea: según por qué camino cambiaras el estado, el título acompañaba o se
quedaba quieto.

No lo vi leyendo el código. Lo vi corriéndolo, que es la diferencia entre revisar
y probar.

**Corregirlo mudó el bug en lugar de cerrarlo.** Pedí que el título saliera de
una sola función de render y así quedó, pero la tabla de títulos terminó con tres
entradas para un estado que tiene cuatro valores. El cuarto renderiza `undefined`.

Es la lección más concreta de la entrega: el modelo corrige exactamente lo que le
señalás, y el problema real casi nunca es exactamente lo que señalaste. Pedir que
se centralice el render arregla la forma; el caso faltante hay que nombrarlo
aparte.

**Cuando se adelanta, se adelanta a medias.** El botón "Continuar" apareció un
prompt antes de lo que correspondía, habilitándose al completar los seis
caracteres — pero sin nada atrás. Se prende y no lleva a ningún lado.

## Prompts

El registro completo está en [prompts.md](prompts.md).
