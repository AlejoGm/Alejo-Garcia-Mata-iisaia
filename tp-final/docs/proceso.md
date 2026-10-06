# Bitácora del proceso

Cómo se fue armando la app, en orden. Cada entrada dice qué se hizo, con qué herramienta del flujo y qué se decidió en el camino. El detalle de cada decisión está en [grill.md](grill.md); acá queda el recorrido.

## 1. Idea y pitch

Antes de elegir Gym-bro descarté varias ideas: una herramienta para la bancada de ESP32, un juego tipo Killer, juegos absurdos. La que quedó tiene usuarios reales (nosotros y nuestros amigos del gimnasio) y una regla central que el agente no iba a resolver solo: cómo comparar a gente de distinto peso.

Salida: [pitch.md](../pitch.md) y [pitch.html](../pitch.html).

## 2. PRD y primer grill

Con la skill `grilling` en modo auto, el agente se hizo las preguntas de diseño y propuso respuestas. Con eso salió el PRD, con la skill `to-prd`, publicado también como issue. El primer PRD cubría solo el MVP. Lo corregí para que describa el producto entero, con releases, y que el MVP sea la primera versión de ese producto.

## 3. Corte para la exposición

Para la exposición de la idea construimos un corte vertical: crear un grupo, unirse, cargar una sesión y un ranking de fuerza. El módulo de estadísticas se escribió con TDD: el commit del test en rojo va antes que el de la implementación.

Probándolo en el navegador apareció un bug: después de "Salir" seguía visible el link "Volver al grupo", porque un `display: block` del CSS le ganaba al atributo `hidden`.

## 4. Repaso del grill

Repasé el auto-grill pregunta por pregunta y cambié las decisiones de fondo:
- **Fuerza:** DOTS en lugar del ratio con el peso.
- **Peso corporal:** viaja con cada sesión.
- **Progreso:** mes contra mes.
- **Constancia:** contra un objetivo semanal propio.
- **Ranking de la semana:** reemplaza al "cartel de la vergüenza".
- **Rutinas:** son del grupo, con carga guiada.
- **Duelos:** con nivel de desbalance.
- **Campañas:** tienen ganador.

El grill tiene una sección con lo que cambió y por qué.

## 5. Login con Google y spec

Para la app completa sumé login con Google por Auth0. Eso adelantó las cuentas, que estaban en la v3, y cambió la raíz del modelo: las sesiones pasan a ser del usuario, no del grupo. Lo cerré con un tercer auto-grill y después escribí el [spec](spec.md): modelo de datos, contrato completo, fórmulas y vistas. El spec es la referencia de implementación; si el código se aparta, se corrige uno de los dos en el mismo PR.

## 6. Issues

El spec se partió en 12 issues de cortes verticales: cada uno atraviesa backend, frontend y tests, y deja algo que se puede usar. Van del [#2](https://github.com/AlejoGm/Alejo-Garcia-Mata-iisaia/issues/2) (configurar el agente) al [#13](https://github.com/AlejoGm/Alejo-Garcia-Mata-iisaia/issues/13) (la prueba con el agente gym-bro), y cada PR cierra el suyo.

## 7. Implementación por issues

Cada issue se trabajó en su branch y entró por un PR que lo cierra:
- [#2](https://github.com/AlejoGm/Alejo-Garcia-Mata-iisaia/issues/2): configurar el harness.
- [#3](https://github.com/AlejoGm/Alejo-Garcia-Mata-iisaia/issues/3): login y perfil.
- [#4](https://github.com/AlejoGm/Alejo-Garcia-Mata-iisaia/issues/4): grupos.
- [#5](https://github.com/AlejoGm/Alejo-Garcia-Mata-iisaia/issues/5): carga libre.
- [#6](https://github.com/AlejoGm/Alejo-Garcia-Mata-iisaia/issues/6), [#7](https://github.com/AlejoGm/Alejo-Garcia-Mata-iisaia/issues/7) y [#9](https://github.com/AlejoGm/Alejo-Garcia-Mata-iisaia/issues/9): rankings, feed y reacciones, en un mismo PR.
- [#8](https://github.com/AlejoGm/Alejo-Garcia-Mata-iisaia/issues/8): rutinas.
- [#11](https://github.com/AlejoGm/Alejo-Garcia-Mata-iisaia/issues/11) y [#12](https://github.com/AlejoGm/Alejo-Garcia-Mata-iisaia/issues/12): duelos y campañas.
- [#10](https://github.com/AlejoGm/Alejo-Garcia-Mata-iisaia/issues/10): mis stats.

El módulo de estadísticas se escribió siempre con el test en rojo primero, en su propio commit. Cada corte se probó en el navegador a 375×812 antes del PR.

Lo que apareció en el camino:
- **Módulos viejos en el navegador.** Sin build, el navegador seguía sirviendo los módulos anteriores. Se resolvió con `Cache-Control: no-cache`.
- **`stats.py` pasó las 300 líneas.** Se partió en un paquete por tema, y las reglas del harness, la skill y el spec se actualizaron en el mismo PR.
- **Un campo de dataclass llamado `date`** pisaba el tipo `date` dentro de la clase.
- **Un test podía fallar el día 1 de cada mes**, porque usaba "ayer" con el período del mes en curso.

## 8. Prueba con el agente gym-bro

Con `scripts/seed_demo.py` se armó un grupo con 8 semanas de historia. El sub-agente `gym-bro` usó la app como un usuario real: en el gimnasio, con una mano y apurado, y después en casa. Midió toques por serie, se equivocó a propósito y recargó a mitad de carga.

Encontró 22 fricciones y 9 bugs. Tres de los bugs estaban en el spec, no en el código: constancia vacía, progreso vacío en períodos largos y demasiados PRs. Las reglas se corrigieron con test primero, y la barra de carga se rehízo para que "Guardar serie" quede en la zona del pulgar. El detalle está en [devolucion-gym-bro.md](devolucion-gym-bro.md).

## 9. Segunda pasada del gym-bro

Después de los arreglos, el gym-bro volvió a probar como un usuario nuevo. Sobre 14 puntos: 11 quedaron arreglados y 3 a medias. Los tres se resolvieron en un último PR:
- **Corregir una serie:** la serie queda en su lugar con un aviso "Editando serie N", y guardar el cambio no reinicia el timer.
- **El campo de peso:** ahora selecciona todo también con tecleo rápido.
- **"0 kg" en ejercicios con tu peso:** ahora dice "peso corporal + lastre".

También marcó que el progreso del mes en curso sale negativo, porque el mes todavía no terminó. Quedó marcado como parcial en rankings y en el gráfico, sin cambiar la regla de meses de calendario que había elegido.

Lo que no entró quedó en issues.
