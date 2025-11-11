import time

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
    ejes = ['R', 'U', 'F']
    modificadores = ['', "'", '2']
    
    # El sistema caótico ahora solo necesita 3 estados iniciales.
    # El LCG se usa para inicializarlos de forma determinista.
    estados_caoticos = {}
    for eje in ejes:
        estados_caoticos[eje] = 0.1 + (generador_lcg.get_random_float() * 0.8)
    
    print(f"--- Generador Caótico 3-Ejes con r={r} ---")
    print("Estados caóticos iniciales (x_0):")
    for e, x in estados_caoticos.items():
        print(f"  {e}: {x:.4f}")
    
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
            
    return ' '.join(scramble)

seed = 42

# 2. Crear la instancia de nuestro generador LCG
mi_generador_lcg = LCG(seed)

# 3. Generar el scramble (longitud 11 es estándar para 2x2)
mi_scramble = generar_scramble_caotico_3ejes(mi_generador_lcg, longitud=11, r=3.99)

print("\nScramble Caótico Final (3 ejes):")
print(mi_scramble)