import kociemba
from scrambler import LCG, Cubo, generar_scramble_caotico_6ejes_adyacente
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
import copy

class Agente_Resolvedor:
    def __init__(self, CuboInicial):
        self.cubo = copy.deepcopy(CuboInicial)
        self.n_movimientos = 0
        self.mov_previo = []
        self.historial_movimientos = []
    
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

        
    def proximo_estado(self, P_A, G_A, S_G,S_G_path):
        V = 0
        if P_A <= 0 and G_A < 0:
            V = np.random.randint(1, max(2, np.abs(G_A)))
            self.cubo.disposicion = copy.deepcopy(S_G)
        
            self.historial_movimientos = copy.deepcopy(S_G_path)
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
        random_scramble = generar_scramble_caotico_6ejes_adyacente(lcg, longitud=V, r=R)
        self.cubo.rotar_cubo(random_scramble)
        self.n_movimientos += len(random_scramble)
        self.mov_previo = random_scramble
        self.historial_movimientos.extend(random_scramble)
        return self.fitness_score()
    
    def resuelto(self):
        cubo_resuelto = Cubo(self.cubo.tamanio)
        if cubo_resuelto.disposicion == self.cubo.disposicion:
            return True
        return False

class PSO:
    def __init__(self, n_agentes, cubo_inicial):
        self.agentes = [Agente_Resolvedor(copy.deepcopy(cubo_inicial)) for _ in range(n_agentes)]
        self.mejor_agente = self.agentes[0]
        self.FS = [agente.fitness_score() for agente in self.agentes]
        self.FSP = self.FS.copy()
        self.FSG = np.min(self.FSP)  
        self.SG = copy.deepcopy(cubo_inicial.disposicion)
        self.SG_path = []
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
                
                self.FS[i] = agente_actual.proximo_estado(P_A=PA, G_A=GA, S_G=self.SG, S_G_path=self.SG_path)
                self.NFE += 1
                if self.FS[i] < self.FSP[i]: 
                    self.FSP[i] = self.FS[i]

                if self.FS[i] < self.FSG: 
                    # 🔹 Actualizar el mejor cubo global
                    self.SG = copy.deepcopy(agente_actual.cubo.disposicion)
                    self.FSG = self.FS[i]
                    
                    # 🔹 Guardar la concatenación de scrambles que mejoraron el global
                    self.SG_path= copy.deepcopy(agente_actual.historial_movimientos)
                    
                    # 🔹 NUEVO: guardar también el historial completo del agente que logró el mejor global
                    self.mejor_agente = copy.deepcopy(agente_actual)

                #if i==0:
                #    print("ITERACION ", iters, ' AGENTE ', i)
                #    print(agente_actual.mov_previo)
                #    print('FITNESS SCORE: ', agente_actual.fitness_score())
                #    agente_actual.cubo.mostrar()


                if agente_actual.resuelto():
                    if previa_solucion == 0:
                        self.SG_path.extend(agente_actual.mov_previo)

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
        
    
if __name__ == "__main__":
    # ===================== PARÁMETROS EXPERIMENTALES =====================
    LONGITUDES_SCRAMBLE = [25, 30]  # Column "Length"
    N_INTENTOS = 5                                  # 5/5 en la tabla
    N_AGENTES = 50                                  # 50 partículas
    MAX_ITERS = 7500                              # 10,000 iteraciones
    TAM_CUBO = 3                                    # 3x3x3 Rubik cube
    R_PARAM = 3.99                                  # Valor base de r
    SEED_BASE = 42                                  # Semilla reproducible

    # ===================== LOOP PRINCIPAL =====================
    resultados = []

    for longitud in LONGITUDES_SCRAMBLE:
        print(f"\n🧩 Iniciando experimentos para scramble de longitud {longitud}...")
        exitos = 0
        datos_longitud = []

        for intento in range(N_INTENTOS):
            print(f"  ▶ Intento {intento+1}/{N_INTENTOS}")
            # Generar scramble reproducible
            lcg = LCG(SEED_BASE + intento)
            scramble = generar_scramble_caotico_6ejes_adyacente(lcg, longitud=longitud, r=R_PARAM)
            cubo_inicial = Cubo(TAM_CUBO)
            cubo_inicial.rotar_cubo(scramble)

            # Obtener solución óptima por Kociemba
            solver = Agente_Resolvedor(cubo_inicial)
            actual_kociemba = len(kociemba.solve(solver.cubo_a_string_kociemba()))

            # Ejecutar PSO
            pso = PSO(n_agentes=N_AGENTES, cubo_inicial=cubo_inicial)
            pso.iterar(max_iters=MAX_ITERS)

            # SOLUTION LENGTH (importante guardarlo)
            longitud_solucion = len(pso.SG_path)

            print("============================================================")
            print("🏁 SECUENCIA ÓPTIMA GLOBAL (concatenación de scrambles que mejoraron el global):")
            print("Scramble inicial: ", scramble)
            print(pso.SG_path)
            print(f"Total movimientos concatenados: {longitud_solucion}")
            print("============================================================")


            # Calcular métricas
            obtained = pso.Obtained
            first = pso.First
            last = pso.Last
            avg = pso.Average
            nfe = pso.NFE
            total = sum(ag.resuelto() for ag in pso.agentes)

            if total > 0:
                exitos += 1
                
            datos_longitud.append({
                "Length": longitud,
                "%": f"{exitos}/{N_INTENTOS}",
                "Actual": actual_kociemba,
                "Obtained": round(obtained, 2),
                "First": first,
                "Last": last,
                "Average": round(avg, 2),
                "NFE": nfe,
                "Total": total,
                "SolutionLen": longitud_solucion
            })

        # ===== al terminar los N_INTENTOS de esta longitud, calcular mínimo local =====
        # Si hubo intentos y se guardaron SolutionLen:
        sol_lengths = [d["SolutionLen"] for d in datos_longitud if "SolutionLen" in d]
        if sol_lengths:
            minimo_local = int(min(sol_lengths))
            maximo_local = int(max(sol_lengths))  
        else:
            minimo_local = None
            maximo_local = None

        # Agregar promedio de los N_INTENTOS
        promedio = {
            "Length": longitud,
            "%": f"{exitos}/{N_INTENTOS}",
            "Actual": np.nanmean([d["Actual"] for d in datos_longitud]),
            "Obtained": np.nanmean([d["Obtained"] for d in datos_longitud]),
            "First": np.nanmean([d["First"] for d in datos_longitud]),
            "Last": np.nanmean([d["Last"] for d in datos_longitud]),
            "Average": np.nanmean([d["Average"] for d in datos_longitud]),
            "NFE": np.nanmean([d["NFE"] for d in datos_longitud]),
            "Total": np.nanmean([d["Total"] for d in datos_longitud]),
            "MinSolutionLen": minimo_local,
            "MaxSolutionLen": maximo_local
        }

        resultados.append(promedio)

        # Guardar el mínimo LOCAL para esta longitud en un dict global
        # (usa un dict fuera del for para acumular)
        if minimo_local is not None:
            if 'minimos_por_scramble' not in locals():
                minimos_por_scramble = {}
            minimos_por_scramble[longitud] = minimo_local


    # ===================== CALCULAR COTAS DEL NÚMERO DE DIOS =====================
    if 'minimos_por_scramble' in locals() and minimos_por_scramble:
        # Cota inferior experimental = mejor (mínimo) entre los mínimos locales
        cota_inferior = min(minimos_por_scramble.values())
        # Cota superior experimental = peor (máximo) entre los mínimos locales
        cota_superior = max(minimos_por_scramble.values())

        print("\n============================================================")
        print("🧠 ESTIMACIÓN EXPERIMENTAL DEL NÚMERO DE DIOS (PSO)")
        print("============================================================")
        print("Minimos por scramble (por longitud):", minimos_por_scramble)
        print("Cota inferior (mejor solución hallada entre todos los scrambles):", cota_inferior)
        print("Cota superior (peor de las mejores soluciones por scramble):", cota_superior)
        print(f"→ Intervalo estimado para el Número de Dios: [{cota_inferior}, {cota_superior}] movimientos")
        print("============================================================")
    else:
        print("\n⚠️ No se pudieron calcular cotas: no se registraron soluciones válidas.")
