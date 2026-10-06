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
