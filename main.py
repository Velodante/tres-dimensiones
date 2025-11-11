# visualizacion_pygame.py
# Ejemplo base de visualización para el modelo de Boids utilizando la librería Pygame.

# Este script provee una visualización sencilla en 2D para un conjunto de agentes 
# (boids) que se mueven y actualizan su estado según las reglas del modelo implementado 
# en otro módulo. Permite observar de forma animada el comportamiento emergente 
# de sistemas dinámicos simples, conectando el modelado por agentes con una interfaz 
# gráfica interactiva.
# ---------------------------------------------------------
# PARÁMETROS DE VISUALIZACIÓN (metros → píxeles)
# ---------------------------------------------------------
# - WIDTH_PX, HEIGHT_PX : dimensiones de la ventana en píxeles.
# - SCALE               : factor de conversión entre unidades del modelo (m) y píxeles.
# - WORLD_X, WORLD_Y    : dimensiones del mundo simulado (en metros).
# - BG_COLOR            : color de fondo.
# - BOID_COLOR          : color de los boids.
# - FPS                 : cuadros por segundo (frecuencia de actualización).
# - STEPS_PER_FRAME     : número de actualizaciones del modelo por cada fotograma.

import pygame
import numpy as np
pygame.init()

# ---------------- Visualization params (meters -> pixels) ----------------
WIDTH_PX, HEIGHT_PX = 900, 600
SCALE = 60  # pixels per meter (900/15m)

WORLD_X = (0.0, WIDTH_PX / SCALE)
WORLD_Y = (0.0, HEIGHT_PX / SCALE)

BORDER_PARAM = 1
BORDER_X = (WORLD_X[0] + BORDER_PARAM, WORLD_X[1] - BORDER_PARAM)
BORDER_Y = (WORLD_Y[0] + BORDER_PARAM, WORLD_Y[1] - BORDER_PARAM)

if BORDER_X[0] > WORLD_X[1] or BORDER_X[1] < 0:
    raise ValueError("Parámetro de borde excesivo en comparación al tamaño del mundo.")
if BORDER_Y[0] > WORLD_Y[1] or BORDER_Y[1] < 0:
    raise ValueError("Parámetro de borde excesivo en comparación al tamaño del mundo.")


BG_COLOR = (10, 10, 20)
BOID_COLOR = (230, 230, 240)
FPS = 60
STEPS_PER_FRAME = 2   # cuantas actualizaciones del modelo por frame

# ---------------- Drawing ----------------
def draw_boid(screen, boid):
    """
    Dibuja un boid como un pequeño triángulo orientado en la pantalla.
    Las coordenadas del boid se expresan en metros y se convierten a píxeles 
    multiplicando por SCALE. El eje Y se invierte para ajustarse al sistema de 
    coordenadas de Pygame (origen en la esquina superior izquierda).

    - La orientación del triángulo se calcula según el vector de velocidad boid.v.
    - Los vértices del triángulo (p1, p2, p3) se definen en función del ángulo θ 
      y las dimensiones del triángulo (L largo, W semiancho).
    - Se utiliza pygame.draw.polygon para renderizar el boid.
    """
    x, y = boid.x * SCALE
    y = HEIGHT_PX - y  

    # orientación a partir de la velocidad
    if np.linalg.norm(boid.v) > 1e-9:
        theta = np.arctan2(boid.v[1], boid.v[0])
    else:
        theta = 0.0

    L = 15   # largo del triángulo en píxeles
    W = 6    # medio ancho del triángulo en píxeles

    p1 = (x + L * np.cos(theta),          y - L * np.sin(theta))
    p2 = (x - W * np.cos(theta + np.pi/2), y + W * np.sin(theta + np.pi/2))
    p3 = (x - W * np.cos(theta - np.pi/2), y + W * np.sin(theta - np.pi/2))
    pygame.draw.polygon(screen, BOID_COLOR, [p1, p2, p3])

# ---------------- Main animation loop ----------------
def run_pygame(boids, steps=5000):
    """
    Ejecuta la animación principal del modelo de boids. 
    Esta función:
    1. Inicializa la ventana de Pygame y un reloj para controlar el FPS.
    2. Actualiza los boids llamando a b.actualizar(boids) según las reglas del modelo.
    3. Aplica una posible corrección de retorno en los límites del mundo (boundary return).
    4. Dibuja los boids orientados en cada fotograma con draw_boid().
    5. Actualiza la pantalla con pygame.display.flip() y mantiene el ritmo con clock.tick(FPS).
    6. Finaliza la simulación al alcanzar el número máximo de pasos o cerrar la ventana.
    """
    screen = pygame.display.set_mode((WIDTH_PX, HEIGHT_PX))
    pygame.display.set_caption("Boids (with boundary return)")
    clock = pygame.time.Clock()

    running = True
    t = 0
    while running and t < steps:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # model updates
        for _ in range(STEPS_PER_FRAME):
            idx = np.random.permutation(len(boids))
            for i in idx:
                boids[i].actualizar(boids)
            t += 1

        # render
        screen.fill(BG_COLOR)
        for b in boids:
            draw_boid(screen, b)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

# ---------------- Quick runner (keeps your console menu idea) ----------------
if __name__ == "__main__":
    print("1. Un boid se encuentra con otro boid")
    print("2. Varios boids se encuentran")
    print("3. Un boid se encuentra con un grupo de boids")
    print("4. Dos grupos del mismo tamaño se encuentran")
    print("5. Dos grupos de distinto tamaño se encuentran")
    try:
        opcion = int(input("Seleccione un caso: ").strip())
    except ValueError:
        opcion = 1
    boids = crear_caso(opcion, np.array([BORDER_X, BORDER_Y]), np.array([WORLD_X, WORLD_Y]))
    run_pygame(boids, steps=10000)