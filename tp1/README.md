# TP 1 — Nimbus, el registro que no te deja registrarte

Una página de registro de un servicio SaaS. Se ve profesional, no esconde nada,
y completar los tres pasos lleva varios minutos.

## Cómo se ejecuta

Doble click en `index.html`. Un solo archivo, sin dependencias.

## Qué me propuse construir

Una bad UI donde la hostilidad esté a la vista y aun así duela. Tres pasos, tres
mecánicas distintas.

**Usuario.** Seis caracteres, cada uno elegido desde su propio dropdown con los
95 caracteres ASCII imprimibles. Cada dropdown tiene su propio orden barajado,
así que aprender dónde está la "a" en el primero no sirve para el segundo. La
tabla completa está a la vista, ordenada de la única forma que no ayuda.

**Contraseña.** Las reglas aparecen de a una: cumplís la que ves y recién ahí te
enterás de que hay otra. Cada una nueva suele romper lo que ya habías armado, y
la última es auto-referencial — depende del largo de la contraseña, así que
agregar un carácter para cumplirla la vuelve a romper.

**Plan.** Una grilla de 25 addons con nombres que no dejan adivinar qué vende
Nimbus: Blockchain, Exorcismo, Veterinaria, Fax. Tocar uno lo prende o apaga
junto con sus cuatro vecinos, como el juego *Lights Out*. El saldo disponible es
$0 y arriba está el total mensual, así que la única forma de seguir es dejar
todo apagado. Nunca cargaste un peso, pero la página te preseleccionó diez
addons y desactivarlos es tu problema.

Lo que me interesaba de ese último paso es la inversión: en cualquier página
normal sumás lo que querés, acá tenés que restar todo, y restar prende cosas.

## Decisiones que tomé yo

**Verificar la solubilidad antes de mandar el prompt.** Escribí las reglas de la
contraseña en Python y busqué soluciones antes de pedirle nada al modelo. Una
versión anterior era imposible: pedía que el largo apareciera dentro de la
contraseña mientras otra regla prohibía las corridas de dos dígitos, y todo
largo entre 15 y 99 tiene dos dígitos. Una bad UI sin solución no es bad UI, es
un bug.

**Generar el Lights Out con clicks, no al azar.** En una grilla de 5x5 solo una
de cada cuatro configuraciones tiene solución. La grilla arranca apagada y se le
aplican diez clicks aleatorios con la misma función que usa el usuario: así el
camino de vuelta siempre existe, porque es el mismo camino.

**Nombrar la transición de cancelar.** En los dropdowns hay tres clicks, no dos:
abrir, elegir y salir sin elegir. Si no nombrás el tercero, el modelo decide por
su cuenta y lo normal es que no haya forma de cerrar sin quedarte con un
carácter que no querías. Quiero que cueste, no que sea irreversible.

**Prompts chicos en vez de uno grande.** Tres mecánicas independientes pedidas
juntas me dejaban sin forma de saber cuál rompió qué.

**Medir de dónde venía la dificultad antes de tocarla.** La grilla de 5x5 quedó
injugable y lo primero que se me ocurrió fue achicarla. Antes de hacerlo medí:
la dificultad no estaba en el tamaño sino en los diez clicks con los que se
generaba. Con cuatro clicks, una grilla de 25 celdas y una de 15 cuestan lo
mismo. Achiqué igual, pero por otro motivo — escanear 25 celdas abruma y así la
grilla entra en pantalla junto al botón.

## Qué salió mal y cómo lo corregí

**El código que no pedí fue el que trajo los bugs.** Pedí un esqueleto y llegó
además una función "para más adelante" que duplicaba un texto que ya estaba en
el HTML. Según por qué camino cambiaras el estado, la pantalla acompañaba o se
quedaba quieta. No lo vi leyendo el código: lo vi corriéndolo.

**Las instrucciones generales no se cumplen; las listas, sí.** Pasó tres veces.
Pedí centralizar el render y lo centralizó, pero dejó un valor de estado sin
cubrir que mostraba `undefined`. Un prompt de puro CSS decía "nada más cambia,
ni las reglas" y aun así cambió el texto de una regla a medio inglés. El de
tematizado decía "no debe quedar ningún valor escrito a mano" y tokenizó
exactamente los diez de mi lista, dejando crudos los que no encajaban.

Con tres casos deja de ser anécdota: el modelo cumple al pie de la letra lo que
enumerás e ignora la instrucción general que lo acompaña. Las líneas defensivas
sirven, pero solo para lo que nombran.

**Una regla mía tenía un agujero.** Aclaré en el prompt que la "y" cuenta como
consonante y me olvidé de la "ñ". El modelo hizo lo que pedí, así que quedaba
una escapatoria para saltear esa regla.

**Y una decisión mía que salió mal.** Para que la grilla de addons no se
desbordara en pantallas angostas pedí `grid-template-columns: auto-fit`. Anda,
pero reacomoda la grilla a dos columnas mientras la lógica de vecinos sigue
calculando sobre cinco: el puzzle deja de coincidir con lo que se ve. Lo dejé
porque la entrega se abre en una compu, donde siguen siendo cinco.

Ninguno de estos apareció leyendo el código. Salieron corriéndolo y midiendo el
DOM.

## Prompts

El registro completo está en [prompts.md](prompts.md).
