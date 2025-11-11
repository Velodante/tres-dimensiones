import numpy as np
import matplotlib.pyplot as plt

class Cubo:
    def __init__(self, tamanio=3, 
        colores = {
            'U': 'W',  # Blanco
            'D': 'Y',  # Amarillo
            'L': 'O',  # Naranja
            'R': 'R',  # Rojo
            'F': 'G',  # Verde
            'B': 'B'   # Azul
        }):
        self.tamanio = tamanio
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
        base = mov[0]
        sentido = 1  # horario
        if len(mov) > 1:
            if mov[1] == "'":
                sentido = -1 # antihorario
            elif mov[1] == "2":
                sentido = 2 # doble

        self._rotar_cara(base, sentido)

    # -----------------------------
    # Movimiento de una cara
    # -----------------------------
    def _rotar_cara(self, cara, sentido):
        n = self.tamanio
        D = self.disposicion

        # Rotar la propia cara
        if sentido == 1:
            D[cara] = self._rotar_matriz_horario(D[cara])
        elif sentido == -1:
            D[cara] = self._rotar_matriz_antihorario(D[cara])
        elif sentido == 2:
            D[cara] = self._rotar_matriz_180(D[cara])

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
            elif sentido == 2:
                filas = filas[2:] + filas[:2]
            for c, f in zip(caras, filas):
                D[c][0] = f

        elif cara == 'D':
            caras = ['F', 'R', 'B', 'L']
            filas = [D[x][-1][:] for x in caras]
            if sentido == 1:
                filas = [filas[-1]] + filas[:-1]
            elif sentido == -1:
                filas = filas[1:] + [filas[0]]
            elif sentido == 2:
                filas = filas[2:] + filas[:2]
            for c, f in zip(caras, filas):
                D[c][-1] = f

        elif cara == 'F':
            top = D['U'][-1][:]
            right = [r[0] for r in D['R']]
            bottom = D['D'][0][:]
            left = [r[-1] for r in D['L']]
            if sentido == 1:
                D['U'][-1] = left[::-1]
                for i in range(n):
                    D['R'][i][0] = top[i]
                D['D'][0] = right[::-1]
                for i in range(n):
                    D['L'][i][-1] = bottom[i]
            elif sentido == -1:
                D['U'][-1] = [r[0] for r in D['R']][::-1]
                for i in range(n):
                    D['R'][i][0] = D['D'][0][::-1][i]
                D['D'][0] = [r[-1] for r in D['L']][::-1]
                for i in range(n):
                    D['L'][i][-1] = top[i]
            elif sentido == 2:
                self._rotar_cara(cara, 1)
                self._rotar_cara(cara, 1)

        elif cara == 'B':
            top = D['U'][0][:]
            right = [r[-1] for r in D['R']]
            bottom = D['D'][-1][:]
            left = [r[0] for r in D['L']]
            if sentido == 1:
                D['U'][0] = [r[-1] for r in D['R']]
                for i in range(n):
                    D['R'][i][-1] = bottom[::-1][i]
                D['D'][-1] = [r[0] for r in D['L']]
                for i in range(n):
                    D['L'][i][0] = top[::-1][i]
            elif sentido == -1:
                D['U'][0] = [r[0] for r in D['L']][::-1]
                for i in range(n):
                    D['L'][i][0] = bottom[i]
                D['D'][-1] = [r[-1] for r in D['R']][::-1]
                for i in range(n):
                    D['R'][i][-1] = top[i]
            elif sentido == 2:
                self._rotar_cara(cara, 1)
                self._rotar_cara(cara, 1)

        elif cara == 'L':
            top = [r[0] for r in D['U']]
            front = [r[0] for r in D['F']]
            bottom = [r[0] for r in D['D']]
            back = [r[-1] for r in D['B']][::-1]
            if sentido == 1:
                for i in range(n):
                    D['U'][i][0] = back[i]
                    D['F'][i][0] = top[i]
                    D['D'][i][0] = front[i]
                    D['B'][n - 1 - i][-1] = bottom[i]
            elif sentido == -1:
                for i in range(n):
                    D['U'][i][0] = front[i]
                    D['F'][i][0] = bottom[i]
                    D['D'][i][0] = back[i]
                    D['B'][n - 1 - i][-1] = top[i]
            elif sentido == 2:
                self._rotar_cara(cara, 1)
                self._rotar_cara(cara, 1)

        elif cara == 'R':
            top = [r[-1] for r in D['U']]
            front = [r[-1] for r in D['F']]
            bottom = [r[-1] for r in D['D']]
            back = [r[0] for r in D['B']][::-1]
            if sentido == 1:
                for i in range(n):
                    D['U'][i][-1] = front[i]
                    D['F'][i][-1] = bottom[i]
                    D['D'][i][-1] = back[i]
                    D['B'][n - 1 - i][0] = top[i]
            elif sentido == -1:
                for i in range(n):
                    D['U'][i][-1] = back[i]
                    D['F'][i][-1] = top[i]
                    D['D'][i][-1] = front[i]
                    D['B'][n - 1 - i][0] = bottom[i]
            elif sentido == 2:
                self._rotar_cara(cara, 1)
                self._rotar_cara(cara, 1)

if __name__ == "__main__":
    c = Cubo(3)
    print("Estado inicial:")
    c.mostrar()
    
    print("\nSecuencia: R, U, R', U'")
    movimientos = ['R', 'U', "R'", "U'"]
    for m in movimientos:
        print(f"\nDespués de {m}:")
        c.rotar_cubo(m)
        c.mostrar()