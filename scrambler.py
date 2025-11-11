import numpy as np
import matplotlib.pyplot as plt
import time

class Cubo:
    def __init__(self, tamanio=3):
        self.tamanio = tamanio
        colores = {
            'U': 'W',  # Blanco
            'D': 'Y',  # Amarillo
            'L': 'O',  # Naranja
            'R': 'R',  # Rojo
            'F': 'G',  # Verde
            'B': 'B'   # Azul
        }
        self.disposicion = {
            c: [[colores[c] for _ in range(tamanio)] for _ in range(tamanio)]
            for c in colores
        }

    # -----------------------------
    # Mostrar el cubo en formato net
    # -----------------------------
    def mostrar(self):
        U, D, L, F, R, B = [self.disposicion[c] for c in "UDLFRB"]
        n = self.tamanio

        def fila_texto(fila):
            return " ".join(fila)

        # cara superior (U)
        for i in range(n):
            print(" " * (n * 2) + fila_texto(U[i]))

        # L, F, R, B
        for i in range(n):
            print(f"{fila_texto(L[i])}   {fila_texto(F[i])}   {fila_texto(R[i])}   {fila_texto(B[i])}")

        # cara inferior (D)
        for i in range(n):
            print(" " * (n * 2) + fila_texto(D[i]))
        print()

    # -----------------------------
    # Rotación de una cara NxN (en sentido horario)
    # -----------------------------
    def _rotar_matriz_horario(self, cara):
        n = self.tamanio
        return [[cara[n - j - 1][i] for j in range(n)] for i in range(n)]

    def _rotar_matriz_antihorario(self, cara):
        n = self.tamanio
        return [[cara[j][n - i - 1] for j in range(n)] for i in range(n)]

    def _rotar_matriz_180(self, cara):
        n = self.tamanio
        return [[cara[n - i - 1][n - j - 1] for j in range(n)] for i in range(n)]

    # -----------------------------
    # Ejecutar movimiento
    # -----------------------------
    def rotar_cubo(self, mov):
        # mover puede ser U, U', U2, etc.
        for m in mov:
            base = m[0]
            sentido = 1  # horario
            if len(m) > 1:
                if m[1] == "'":
                    sentido = -1
                elif m[1] == "2":
                    sentido = 2

            self._rotar_cara(base, sentido)

    # -----------------------------
    # Movimiento de una cara
    # -----------------------------
    def _rotar_cara(self, cara, sentido):
        n = self.tamanio
        D = self.disposicion

        # --- Manejar rotación doble primero y salir ---
        if sentido == 2:
            # aplicar dos veces la rotación normal (horaria) y terminar
            self._rotar_cara(cara, 1)
            self._rotar_cara(cara, 1)
            return

        # Rotar la propia cara (solo 1 o -1 llegan acá)
        if sentido == 1:
            D[cara] = self._rotar_matriz_horario(D[cara])
        elif sentido == -1:
            D[cara] = self._rotar_matriz_antihorario(D[cara])

        # Bordes afectados según la cara
        def filaU(): return D['U'][-1]
        def filaD(): return D['D'][0]
        def colL(): return [r[-1] for r in D['L']]
        def colR(): return [r[0] for r in D['R']]

        if cara == 'U':
            caras = ['B', 'R', 'F', 'L']
            filas = [D[x][0][:] for x in caras]
            if sentido == 1:
                filas = [filas[-1]] + filas[:-1]
            elif sentido == -1:
                filas = filas[1:] + [filas[0]]
            for c, f in zip(caras, filas):
                D[c][0] = f

        elif cara == 'D':
            caras = ['F', 'R', 'B', 'L']
            filas = [D[x][-1][:] for x in caras]
            if sentido == 1:
                filas = [filas[-1]] + filas[:-1]
            elif sentido == -1:
                filas = filas[1:] + [filas[0]]
            for c, f in zip(caras, filas):
                D[c][-1] = f

        elif cara == 'F':
            top = D['U'][-1][:]
            bottom = D['D'][0][:]
            left = [r[-1] for r in D['L']]
            right = [r[0] for r in D['R']]

            if sentido == 1:  # F horario
                for i in range(n):
                    D['U'][-1][i] = left[n - 1 - i]
                    D['R'][i][0] = top[i]
                    D['D'][0][i] = right[n - 1 - i]
                    D['L'][i][-1] = bottom[i]

            elif sentido == -1:  # F antihorario
                for i in range(n):
                    D['U'][-1][i] = right[i]
                    D['R'][i][0] = bottom[n - 1 - i]
                    D['D'][0][i] = left[i]
                    D['L'][i][-1] = top[n - 1 - i]


        elif cara == 'B':
            top = D['U'][0][:]
            bottom = D['D'][-1][:]
            left = [r[0] for r in D['L']]
            right = [r[-1] for r in D['R']]

            if sentido == 1:  # B horario - CORREGIDO
                for i in range(n):
                    D['U'][0][i] = right[i]
                    D['R'][i][-1] = bottom[n - 1 - i]
                    D['D'][-1][i] = left[i]
                    D['L'][i][0] = top[n - 1 - i]

            elif sentido == -1:  # B antihorario - CORREGIDO
                for i in range(n):
                    D['U'][0][i] = left[n - 1 - i]
                    D['R'][i][-1] = top[i]
                    D['D'][-1][i] = right[n - 1 - i]
                    D['L'][i][0] = bottom[i]


        elif cara == 'L':
            top = [r[0] for r in D['U']]
            front = [r[0] for r in D['F']]
            bottom = [r[0] for r in D['D']]
            back = [r[-1] for r in D['B']]  # columna derecha de B

            if sentido == 1:  # L horario
                for i in range(n):
                    D['U'][i][0] = back[n - 1 - i]
                    D['F'][i][0] = top[i]
                    D['D'][i][0] = front[i]
                    D['B'][i][-1] = bottom[n - 1 - i]
            elif sentido == -1:  # L antihorario
                for i in range(n):
                    D['U'][i][0] = front[i]
                    D['F'][i][0] = bottom[i]
                    D['D'][i][0] = back[n - 1 - i]
                    D['B'][i][-1] = top[n - 1 - i]

        elif cara == 'R':
            top = [r[-1] for r in D['U']]
            front = [r[-1] for r in D['F']]
            bottom = [r[-1] for r in D['D']]
            back = [r[0] for r in D['B']]  # columna izquierda de B

            if sentido == 1:  # R horario
                for i in range(n):
                    D['U'][i][-1] = front[i]
                    D['F'][i][-1] = bottom[i]
                    D['D'][i][-1] = back[n - 1 - i]
                    D['B'][i][0] = top[n - 1 - i]
            elif sentido == -1:  # R antihorario
                for i in range(n):
                    D['U'][i][-1] = back[n - 1 - i]
                    D['F'][i][-1] = top[i]
                    D['D'][i][-1] = front[i]
                    D['B'][i][0] = bottom[n - 1 - i]


# -------------------------------------------------------------------
# PARTE 1: El "Motor" (Generador Congruencial Lineal - LCG)
# (Esta parte es idéntica)
# -------------------------------------------------------------------
class LCG:
    def __init__(self, seed):
        self.m = 2**31 - 1
        self.a = 1103515245
        self.c = 12345
        self._state = seed % self.m
        if self._state == 0: self._state = 1

    def next_int(self):
        self._state = (self.a * self._state + self.c) % self.m
        return self._state

    def get_random_float(self):
        return self.next_int() / self.m

# -------------------------------------------------------------------
# PARTE 2: Funciones "Puente" (Usan nuestro LCG)
# (Esta parte es idéntica)
# -------------------------------------------------------------------

def nuestro_choice_con_pesos(generador_lcg, opciones, pesos):
    total_peso = sum(pesos)
    if total_peso <= 0:
        return choicer(generador_lcg, opciones)
    pick = generador_lcg.get_random_float() * total_peso
    acumulado = 0
    for i, opcion in enumerate(opciones):
        acumulado += pesos[i]
        if pick < acumulado:
            return opcion
    return opciones[-1]

def choicer(generador_lcg, opciones):
    idx = int(generador_lcg.get_random_float() * len(opciones))
    return opciones[idx]

# -------------------------------------------------------------------
# PARTE 3: El "Sistema" (Cadena de Markov Caótica de 3 ejes)
# (Aquí están los cambios)
# -------------------------------------------------------------------

def logistic_map_iterate(x, r):
    """Aplica una iteración del mapa logístico."""
    return r * x * (1.0 - x)

def generar_scramble_caotico_3ejes(generador_lcg, longitud=20, r=3.99):
    """
    Generador de Scramble Caótico usando solo R, U, F.
    """
    
    # --- CAMBIO 1 ---
    ejes = ["R", "U", "F"]
    modificadores = ["", "'", "2"]
    
    # El sistema caótico ahora solo necesita 3 estados iniciales.
    # El LCG se usa para inicializarlos de forma determinista.
    estados_caoticos = {}
    for eje in ejes:
        estados_caoticos[eje] = 0.1 + (generador_lcg.get_random_float() * 0.8)
    
    #print(f"--- Generador Caótico 3-Ejes con r={r} ---")
    #print("Estados caóticos iniciales (x_0):")
    #for e, x in estados_caoticos.items():
    #    print(f"  {e}: {x:.4f}")
    
    ultimo_eje_movido = None
    scramble = []

    for i in range(longitud):
        
        # 1. Obtener ejes y pesos posibles
        #    (Ahora la lista será de 2 ejes)
        ejes_posibles = [eje for eje in ejes if eje != ultimo_eje_movido]
        pesos_posibles = [estados_caoticos[eje] for eje in ejes_posibles]

        # 2. Elegir Eje (usando LCG + pesos caóticos)
        eje_actual = nuestro_choice_con_pesos(generador_lcg, ejes_posibles, pesos_posibles)
        
        # 3. Elegir Modificador (usando LCG)
        modificador_actual = choicer(generador_lcg, modificadores)

        # 4. Guardar y actualizar memoria
        scramble.append(eje_actual + modificador_actual)
        ultimo_eje_movido = eje_actual
        
        # 5. Iterar el sistema caótico (ahora solo itera 3 estados)
        for eje in estados_caoticos:
            estados_caoticos[eje] = logistic_map_iterate(estados_caoticos[eje], r)
            
    return scramble

if __name__ == "__main__":
    secuencia = ['U', "D", 'F', 'R', "B", 'L'] 
    #secuencia_prima = ["U'", "D'", "F'", "R'", "B'", "L'"]
    #secuencia_dos = ['U2', "D2", 'F2', 'R2', "B2", 'L2']