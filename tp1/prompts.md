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

---

## 1c — Cerrar el paso usuario

```
Dos cosas.

`titulos` no cubre "confirmado" y ahí el título renderiza undefined.
Que los cuatro valores de `paso` tengan título.

El botón Continuar se habilita pero no hace nada. Que además de los 6
caracteres pida que el primero sea letra (A-Z o a-z), y que al click
pase `estado.paso` a "password".
```

**Qué intentaba lograr:** cerrar el paso 1 con la transición al 2 ya cableada, y tapar el `undefined` que había quedado del prompt anterior.

**Qué devolvió:** las dos correcciones. Probé los cuatro casos del botón: incompleto, dígito primero, espacio primero y letra primera. Solo el último lo habilita.

---

## 2 — El paso password (Patrón 2: iterar sobre el estado)

```
Agregale el paso password.

Estado nuevo: `password` (string) y `reglasVisibles` (número, arranca
en 1). Un <input type="text"> y debajo la lista de reglas visibles,
cada una tachada cuando se cumple.

Cuando todas las reglas visibles se cumplen a la vez, `reglasVisibles`
sube en 1 y aparece la siguiente. Una regla revelada no se oculta más.

Las 10 reglas en orden:
1. Empieza con una letra.
2. Mínimo 15 caracteres.
3. Al menos un símbolo de !@#$%^&*()-
4. Más de 7 dígitos en total.
5. No puede tener dos consonantes seguidas (sin distinguir mayúsculas;
   la "y" cuenta como consonante).
6. No puede tener dos caracteres iguales seguidos.
7. No puede tener dos dígitos consecutivos en valor uno al lado del
   otro: ni "12" ni "21", ni "89" ni "98".
8. No puede tener una corrida de exactamente 3 dígitos seguidos.
   Corridas de 1, 2, 4 o más están permitidas.
9. Termina con un dígito que aparece una sola vez en toda la
   contraseña.
10. La cantidad de caracteres de la contraseña tiene que aparecer
    dentro de ella como una corrida de dígitos aislada. Si la
    contraseña mide 17, tiene que haber un "17" con no-dígitos a
    ambos lados (o contra el borde).

Con las 10 cumplidas, Continuar se habilita y pasa `estado.paso` a
"addons".
Sólo mostrar la regla cuando no se cumple
```

**Qué intentaba lograr:** que las reglas se revelen de a una y que la última sea auto-referencial — al agregar un carácter para cumplirla, la longitud cambia y la regla se rompe sola.

**Por qué escribí las reglas así de explícitas:** antes de mandar el prompt verifiqué en Python que el set tuviera solución. Una versión anterior era irresoluble: pedía que la longitud apareciera como corrida aislada mientras otra regla prohibía las corridas de exactamente 2 dígitos, y como toda longitud entre 15 y 99 tiene dos dígitos, no había contraseña posible. Una bad UI sin solución no es bad UI, es un bug.

**Qué devolvió:** las diez reglas implementadas y el paso funcionando. Guardó y restauró la posición del cursor en cada render, que no le pedí y sin lo cual escribir sería imposible, porque el `innerHTML` destruye el input en cada tecla.

Probé escribiendo `f51at28g26*ul0&17` carácter por carácter: las diez reglas se revelan en orden y el botón se habilita. Encontré un agujero: el regex de consonantes no incluye la `ñ`, así que `bñcñdñf` pasa la regla 5 usando la `ñ` como separador. Mi prompt aclaró la `y` y se olvidó de la `ñ`.

---

## 3 — Ocultar la contraseña y cerrar el agujero de la ñ

```
Dos cosas.

En la regla 5, la "ñ" también cuenta como consonante.

Y el input de contraseña ahora es type="password".

Estado nuevo: `passwordVisible` (boolean, arranca en false). A la
derecha del input, un botón con un ojo.

Al click en el ojo: `passwordVisible` pasa a true, el input se vuelve
type="text" y el ojo se tacha. Un segundo después vuelve solo a false
y a type="password".

Si se clickea el ojo mientras ya está visible, el segundo arranca de
nuevo desde ese click.

Escribir en el input no interrumpe el segundo.
```

**Qué intentaba lograr:** con diecisiete caracteres y diez reglas, no ver lo que escribís multiplica el dolor sin agregar ninguna trampa escondida.

**Por qué la última línea:** sin ella el `render()` de cada tecla pisa el timer y el ojo se apaga apenas escribís una letra. Es un bug silencioso: nadie lo pide y siempre aparece.

**Qué devolvió:** las dos cosas. Verifiqué que escribir con el ojo abierto no lo apaga. Efecto lateral que no pedí: al clickear el ojo se pierde el foco del input y hay que volver a clickear adentro para seguir escribiendo.

---

## 4 — El paso addons (Patrón 2: iterar sobre el estado)

```
Agregale el paso addons.

Una grilla de 5x5 con 25 addons. Cada celda muestra el nombre y su
precio mensual. Estos, en este orden:

Blockchain $34   Feng Shui $7    Karaoke $19     Antivirus $23   Riego $5
Tarot $16        Dark Mode $3    Veterinaria $28 Fax $9          Quantum $37
Sommelier $14    Backup $21      Astrología $6   CDN $31         Yoga $11
Metaverso $26    Cerrajería $8   Webhooks $18    Drones $33      Hipnosis $4
Contaduría $24   Ajedrez $13     Clima $29       Podcast $15     Exorcismo $22

Estado nuevo: `addons`, array de 25 booleanos — true es contratado.

Arriba de la grilla: el saldo disponible, fijo en $0, y el total
mensual de los addons contratados. El total en rojo si supera el
saldo.

Click en una celda: se invierte el estado de esa celda y el de sus
vecinos de arriba, abajo, izquierda y derecha. Los vecinos que caen
fuera de la grilla se ignoran. Es la mecánica del juego Lights Out.

Generación del estado inicial: arrancá con las 25 en false y aplicá
10 clicks en celdas al azar, usando la misma función que usa el
click del usuario. No generes los 25 booleanos al azar de forma
independiente: la mayoría de esas grillas no tiene solución y el
paso quedaría imposible. Si después de los 10 clicks quedaron todas
en false, repetí la generación.

Continuar se habilita cuando el total es $0, y pasa `estado.paso` a
"confirmado".
```

**Qué intentaba lograr:** invertir la lógica de cualquier página de precios. En vez de sumar lo que querés, tenés que restar todo — y restar prende cosas. El saldo fijo en $0 es lo que convierte "apagá todo" de capricho en consecuencia: la página te preseleccionó addons que nunca pediste y no cargaste un peso.

**Por qué el párrafo de la generación:** en una grilla de 5x5 solo una de cada cuatro configuraciones de Lights Out tiene solución. Generada al azar, tarde o temprano le toca a alguien un plan gratis inalcanzable, y eso no es bad UI: es un bug. Generarla aplicando clicks sobre la grilla apagada garantiza que el camino de vuelta existe, porque es el mismo camino.

**Qué devolvió:** el paso completo y andando. Generé 300 grillas y verifiqué con un solver que las 300 tuvieran solución, y que ninguna arrancara ya resuelta. El flujo entero cierra: la contraseña abre un plan de $253 con nueve addons puestos por la página, que se apaga en seis clicks.

---

## 5 — Bajar la dificultad del puzzle

```
Achicá la grilla de addons a 3 filas por 5 columnas, 15 addons. Dejá
estos, en este orden:

Blockchain $34   Feng Shui $7    Karaoke $19     Antivirus $23   Riego $5
Tarot $16        Dark Mode $3    Veterinaria $28 Fax $9          Quantum $37
Sommelier $14    Exorcismo $22   Astrología $6   CDN $31         Drones $33

Y en la generación del estado inicial, bajá de 10 clicks aleatorios
a 4. El resto de la mecánica no cambia.
```

**Qué intentaba lograr:** el 5x5 era injugable. Antes de tocarlo medí de dónde venía la dificultad y no era el tamaño: era la generación. Con 10 clicks la solución mínima era de 8, y con 4 baja a 4 sin importar si la grilla es de 15 o de 25 celdas. Achiqué igual porque escanear 25 celdas abruma, y de paso la grilla entra en pantalla junto con el botón.

**Qué devolvió:** los tres cambios, sin tocar el resto. Generé 150 grillas y las verifiqué con un solver exhaustivo: todas resolubles, ninguna arranca resuelta, entre 2 y 4 clicks. El recorrido completo cierra: la contraseña abre un plan de $132 que se apaga en cuatro clicks.

---

## 6 — Arreglar el layout (Patrón 3)

```
Tres contenedores están mal acomodados.

La fila de los 6 dropdowns se desborda en pantallas angostas. Hacela
un flex container con `flex-wrap: wrap`, `justify-content: center` y
`gap: 0.75rem`, para que los dropdowns pasen a dos filas en vez de
salirse.

La grilla de addons también se desborda con 5 columnas fijas.
Cambiá `grid-template-columns` a
`repeat(auto-fit, minmax(96px, 1fr))` y dejá el `gap: 8px`.

La lista desplegada de un dropdown tapa la vista previa del usuario
armado, así que no se ve lo que se lleva elegido mientras se elige.
Movela: en vez de desplegarse hacia abajo, que se despliegue hacia
arriba del toggle (`bottom: calc(100% + 4px)` en vez de `top`).

Nada más cambia: ni el estado, ni las transiciones de click, ni las
reglas.
```

**Qué intentaba lograr:** los tres problemas los encontré midiendo el DOM, no mirando la página. Los dos desbordes solo aparecen abajo de 640px de viewport, así que a ojo no se ven.

**Qué devolvió:** los tres cambios aplicados. Pero el `auto-fit` que pedí fue un error mío: en pantallas angostas la grilla colapsa a 2 columnas mientras la lógica de vecinos sigue calculando sobre 5, así que el puzzle deja de coincidir con lo que se ve. Lo dejé porque la entrega se abre en desktop, donde siguen siendo 5 columnas.

Y hubo una regresión: el prompt decía explícito que las reglas no cambiaban, y aun así el texto de la regla 6 pasó a "No puede tener **two** caracteres iguales seguidos". La línea defensiva estaba escrita y no alcanzó.

---

## 7 — Tematizar y pulir (Patrón 4)

```
Convertí el styling para que use variables CSS de forma completa.

Ya hay algunas en :root. Agregá las que faltan y reemplazá todos los
valores hardcodeados: --color-danger-bg: #fef2f2, --color-danger-border:
#fca5a5, --color-danger-text: #991b1b, --color-selected-bg: #eff6ff,
--color-over-budget: #dc2626, --space-sm: 8px, --space-md: 16px,
--space-lg: 24px, --radius: 8px, --radius-lg: 12px.

No debe quedar ningún color, radio ni espaciado escrito a mano fuera
de :root.

Y una corrección aparte: en la regla 6 el texto dice "No puede tener
two caracteres iguales seguidos". Volvé a "dos".
```

**Qué intentaba lograr:** cerrar el cuarto patrón y arreglar de paso la regresión del prompt anterior, en vez de gastar un prompt en una palabra.

**Qué devolvió:** los tokens de la lista aplicados y el "two" corregido. Auditando el CSS quedaron afuera tres `rgba()` de sombras y seis espaciados (40px, 48px, 12px, 10px, 4px): son los valores que no encajaban en `space-sm/md/lg`, y en vez de crear tokens nuevos los dejó crudos. Cumplió la lista al pie de la letra e ignoró el "no debe quedar ninguno".

Efecto lateral: el gap de los dropdowns pasó de 12px a 8px al tokenizarlo.
