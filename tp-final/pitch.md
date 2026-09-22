# Gym-bro — pitch

Alejo García Mata y Gustavo Campero.

## Problema (1 min)

Entreno con amigos, pero cada uno anota en su app o en una nota del celular. No hay forma de compararse, y comparar kilos no sirve: el que pesa 95 siempre levanta más que el que pesa 70. La competencia, que es lo que motiva, queda en el chat del grupo y a ojo.

## Usuarios (30 s)

Grupos chicos de amigos que van al gimnasio, cada uno con su rutina. No es para entrenadores ni para gimnasios.

## MVP (2 min 30 s)

- Crear un grupo y sumar amigos con un código.
- Cada uno carga sus sesiones: ejercicio, series, peso y repeticiones. El 1RM estimado se calcula solo.
- La rutina es libre. El grupo elige 3 o 4 ejercicios de desafío que hacen todos.
- Tres rankings:
  - **Fuerza relativa** en los ejercicios de desafío (1RM / peso corporal).
  - **Progreso** contra uno mismo en el último mes.
  - **Constancia**: sesiones por semana y racha.
- Un feed del grupo con los PRs.

Queda afuera del MVP: duelos, gráficos de progresión y reacciones.

## Stack (1 min)

Backend en FastAPI con SQLite. Frontend en HTML, CSS y JavaScript sin paso de build. Un solo proceso sirve la API y la página. Desarrollo con Claude Code y el flujo de superpowers: spec, plan, TDD y PR.

## Dudas para la devolución (1 min)

- ¿Alcanza con nickname por grupo o hace falta login, si se ven datos de otros?
- ¿Tres rankings entran en el alcance, o recorto a uno?
