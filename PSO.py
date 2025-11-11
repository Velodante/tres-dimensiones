import kociemba
from scrambler import LCG, Cubo, generar_scramble_caotico_3ejes
import numpy as np
import matplotlib.pyplot as plt
import time

class Agente_Resolvedor:
    def __init__(self, CuboInicial):
        self.cubo = CuboInicial
        self.n_movimientos = 0
        self.mov_previo = []
    
    def cubo_a_string_kociemba(self):
        """
        Convierte el objeto Cubo (3x3) al formato de 54 caracteres que requiere kociemba.
        Usa los centros para mapear colores → caras (U, R, F, D, L, B).
        Orden de caras: U, R, F, D, L, B.
        """
        # 1️⃣ Determinar qué color corresponde a qué cara (según los centros)
        centros = {cara: self.cubo.disposicion[cara][1][1] for cara in 'URFDLB'}
        mapa_color_a_cara = {v: k for k, v in centros.items()}

        # 2️⃣ Construir el string
        orden_caras = ['U', 'R', 'F', 'D', 'L', 'B']
        resultado = ""
        for cara in orden_caras:
            matriz = self.cubo.disposicion[cara]
            for fila in matriz:
                for sticker in fila:
                    resultado += mapa_color_a_cara[sticker]
        return resultado

    def fitness_score(self):
        """
        Calcula el fitness del cubo:
        - Si es 3x3x3, usa kociemba para obtener la cantidad mínima de movimientos.
        - Para otros tamaños, devuelve la cantidad de stickers fuera de lugar.
        Menor fitness = mejor estado.
        """
        if self.cubo.tamanio == 3:
            try:
                estado = self.cubo_a_string_kociemba()
                solucion = kociemba.solve(estado)
                return len(solucion.split())  # cantidad de movimientos
            except Exception:
                # algunos estados pueden ser inválidos por errores de rotación o caras mal alineadas
                return float('inf')
        else:
            # Fitness simple para cualquier otro tamaño: contar stickers fuera de lugar
            cubo_resuelto = Cubo(self.cubo.tamanio)
            errores = 0
            for cara in 'URFDLB':
                errores += np.sum(np.array(self.cubo.disposicion[cara]) != np.array(cubo_resuelto.disposicion[cara]))
            return errores

        
    def proximo_estado(self, P_A, G_A, S_G):
        V = 0
        if P_A <= 0 and G_A < 0:
            V = np.random.randint(1, max(2, np.abs(G_A)))
            self.cubo.disposicion = S_G
        
        elif P_A > 0 and G_A <= 0:
            V = np.random.randint(1, max(2, P_A))
        
        elif P_A > 0 and G_A >= 0:
            if G_A == 0:
                V = np.random.randint(1, max(2, P_A))
            else:
                V = np.random.randint(1, max(2, G_A))
        
        elif P_A == 0 and G_A == 0:
            V = 1

        seed = np.random.randint(10000)
        R = 25.57 + 9 * np.random.randn()

        lcg = LCG(seed)
        random_scramble = generar_scramble_caotico_3ejes(lcg, longitud=V, r=R)
        self.cubo.rotar_cubo(random_scramble)
        self.n_movimientos += len(random_scramble)
        self.mov_previo = random_scramble
        return self.fitness_score()
    
    def resuelto(self):
        cubo_resuelto = Cubo(self.cubo.tamanio)
        if cubo_resuelto.disposicion == self.cubo.disposicion:
            return True
        return False

class PSO:
    def __init__(self, n_agentes, cubo_inicial):
        self.agentes = [Agente_Resolvedor(cubo_inicial) for _ in range(n_agentes)]
        self.FS = [agente.fitness_score() for agente in self.agentes]
        self.FSP = self.FS.copy()
        self.FSG = np.min(self.FSP)  
        self.SG = cubo_inicial.disposicion
        
        # Estadísticas acumuladas
        self.NFE = 0
        self.Average = 0
        self.First = 0
        self.Last = 0
        self.Actual = self.FS[0]
        self.Obtained = 0

        # 🔹 Nuevos: históricos para graficar
        self.hist_fsg = []
        self.hist_promedio = []
        self.hist_mejor_local = []

    def iterar(self, max_iters=5000):
        RESUELTO = False
        iters = 0
        previa_solucion = 0
        while not RESUELTO and iters < max_iters: 
            RESUELTO = True
            for i in range(len(self.agentes)):
                agente_actual = self.agentes[i]
                if agente_actual.resuelto():
                    continue

                PA = self.FSP[i] - self.FS[i]
                GA = self.FSG - self.FS[i]
                
                self.FS[i] = agente_actual.proximo_estado(P_A=PA, G_A=GA, S_G=self.SG)
                self.NFE += 1
                if self.FS[i] < self.FSP[i]: 
                    self.FSP[i] = self.FS[i]

                if self.FS[i] < self.FSG: 
                    self.FSG = self.FS[i] 

                if agente_actual.resuelto():
                    if self.First == 0:
                        self.First = agente_actual.n_movimientos
                    self.Last = agente_actual.n_movimientos
                    self.Obtained += agente_actual.n_movimientos
                    self.Average += iters - previa_solucion
                    previa_solucion = iters
                else:
                    RESUELTO = False

            # 🔹 Guardar estadísticas por iteración
            self.hist_fsg.append(self.FSG)
            self.hist_promedio.append(np.mean(self.FS))
            self.hist_mejor_local.append(np.mean(self.FSP))

            iters += 1

        self.Obtained /= len(self.agentes)
        self.Average /= len(self.agentes)
    
    # 🔹 Nuevo método para graficar
    def graficar_estadisticas(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.hist_fsg, label="Mejor global (FSG)", linewidth=2)
        plt.plot(self.hist_promedio, label="Promedio (FS)", linestyle='--')
        plt.plot(self.hist_mejor_local, label="Promedio mejor personal (FSP)", linestyle=':')
        plt.xlabel("Iteraciones")
        plt.ylabel("Fitness (menor es mejor)")
        plt.title("Evolución del PSO en la resolución del cubo")
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.show()

    def mostrar_estadisticas(self):
        """
        Muestra las estadísticas principales del proceso PSO en consola, 
        con formato legible y valores redondeados.
        """
        print("\n" + "="*60)
        print("📊  ESTADÍSTICAS FINALES DEL PSO".center(60))
        print("="*60)

        # Datos principales
        print(f"{'Número de agentes:':30} {len(self.agentes)}")
        print(f"{'Evaluaciones de fitness (NFE):':30} {self.NFE}")
        print(f"{'Iteraciones realizadas:':30} {len(self.hist_fsg)}")

        # Métricas numéricas
        print("-"*60)
        print(f"{'Mejor fitness global (FSG):':30} {self.FSG:.4f}")
        print(f"{'Promedio de fitness (FS):':30} {np.mean(self.FS):.4f}")
        print(f"{'Promedio mejores personales (FSP):':30} {np.mean(self.FSP):.4f}")

        # Métricas temporales / movimiento
        print("-"*60)
        print(f"{'Primera solución en movimientos:':30} {self.First}")
        print(f"{'Última solución en movimientos:':30} {self.Last}")
        print(f"{'Promedio de movimientos obtenidos:':30} {self.Obtained:.2f}")
        print(f"{'Promedio de iteraciones entre soluciones:':30} {self.Average:.2f}")

        # Conclusión
        print("="*60)
        if self.FSG == float('inf'):
            print("⚠️  No se encontró una solución válida.")
        elif self.FSG == 0:
            print("✅  ¡Cubo completamente resuelto!")
        else:
            print("ℹ️  PSO finalizado, solución parcial alcanzada.")
        print("="*60 + "\n")


                



if __name__ == "__main__":
    longitud_scramble = [5]
    generaciones = 1
    max_its = 500
    tamanio_cubo = 3
    num_agentes = 1
    seeds = [42]
    
    for i in range(len(longitud_scramble)):
        for j in range(generaciones):
            seed = seeds[i]
            lcg = LCG(seed)
            random_scramble = generar_scramble_caotico_3ejes(lcg, longitud=longitud_scramble[i], r=3.99)
            
            c = Cubo(tamanio_cubo)
            print(random_scramble)
            c.rotar_cubo(random_scramble)  # Cubo scrambleado
            c.mostrar()

            pso = PSO(num_agentes, c)
            pso.iterar(max_iters=max_its)
            
            pso.mostrar_estadisticas()

