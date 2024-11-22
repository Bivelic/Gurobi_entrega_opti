import random
# Conjuntos principales
P = range(50)  # Personas
S = range(10)   # Puntos seguros
Q = range(5)    # Cuadrículas
V = range(20)   # Vehículos
t1 = 10    #tiempos en los que varia la 
t2 = 13
# Capacidad de puntos seguros
def generar_capacidades_puntos_seguros(num_puntos_seguros, num_personas):
    variacion=0.03
    base_capacity = num_personas // num_puntos_seguros
    capacidades = []

    # Asignar capacidades con variación aleatoria en ±8%
    for _ in range(num_puntos_seguros - 1):
        capacidad_base = base_capacity
        # Variar la capacidad en un rango de ±8%
        capacidad_var = capacidad_base * random.uniform(1 - variacion, 1 + variacion)
        capacidades.append(int(capacidad_var))

    # Ajustar el último valor para que la suma total sea igual a num_personas
    restantes = num_personas - sum(capacidades)
    capacidades.append(restantes)

    # Aleatorizar el orden para que las capacidades no sigan un patrón
    random.shuffle(capacidades)

    # Crear el diccionario de capacidades
    return {i: capacidad for i, capacidad in enumerate(capacidades)}
c_s = generar_capacidades_puntos_seguros(len(S), len(P))

# Rutas disponibles desde cada cuadrícula a puntos seguros
# Formato: {(cuadrícula, punto_seguro): [rutas]}
def generar_rutas(cant_cuadriculas, cant_puntos_seguros, max_rutas_por_enlace=3):
    """
    Genera rutas aleatorias desde las cuadriculas a los puntos seguros.
    
    Args:
    - cant_cuadriculas (int): Número de cuadriculas.
    - cant_puntos_seguros (int): Número de puntos seguros.
    - max_rutas_por_enlace (int): Máximo número de rutas entre una cuadrícula y un punto seguro.

    Returns:
    - dict: Diccionario con rutas disponibles entre cuadriculas y puntos seguros.
    """
    rutas = {}

    # Recorrer todas las cuadriculas
    for cuadrícula in range(cant_cuadriculas):
        for punto_seguro in range(cant_puntos_seguros):
            # Determinar cuántas rutas habrá entre esta cuadrícula y este punto seguro
            num_rutas = random.randint(1, max_rutas_por_enlace)
            rutas_cuadrícula_punto_seguro = []

            # Generar las rutas
            for i in range(num_rutas):
                ruta_id = f"r_{cuadrícula}_{punto_seguro}_{i}"
                rutas_cuadrícula_punto_seguro.append(ruta_id)

            # Asignar rutas a la cuadrícula y punto seguro
            rutas[(cuadrícula, punto_seguro)] = rutas_cuadrícula_punto_seguro

    return rutas
R_qs = generar_rutas(len(Q), len(S))

# Distribución inicial de personas en cuadrículas
# Se asegura que la suma sea 500
def distribuir_personas_aleatoriamente(total_personas, num_cuadriculas):
    # Inicializar un diccionario para la distribución de personas
    h_q = {i: 0 for i in range(num_cuadriculas)}

    # Asignar de manera aleatoria las personas a las cuadrículas
    personas_restantes = total_personas
    while personas_restantes > 0:
        # Elegir una cuadrícula aleatoria para asignar personas
        cuadrícula = random.randint(0, num_cuadriculas - 1)

        # Definir un rango máximo para asignar personas (por ejemplo, 0 a 50 por cuadrícula)
        personas_a_asignar = random.randint(1, personas_restantes)

        # Asignar las personas seleccionadas a esa cuadrícula
        h_q[cuadrícula] += personas_a_asignar
        personas_restantes -= personas_a_asignar

    return h_q
h_q = distribuir_personas_aleatoriamente(len(P), len(Q))

# Matriz de personas en cuadrículas (1 si la persona i está en la cuadrícula q, 0 en otro caso)
p_i_q = {(i, q): 0 for i in P for q in Q}
current_person = 0
for q in Q:
    for i in range(current_person, current_person + h_q[q]):
        p_i_q[(i, q)] = 1
    current_person += h_q[q]

# Capacidad de las rutas
# Se asegura que sea suficiente para evacuar a las personas de cada cuadrícula
def generar_capacidad_maxima_rutas(R_qs, personas_por_cuadricula):
    capacidades_rutas = {}

    # Iterar sobre cada cuadrícula
    for cuadrícula, rutas in R_qs.items():
        # Obtener el número de personas a evacuar desde esta cuadrícula
        personas_a_evacuar = personas_por_cuadricula.get(cuadrícula, 0)
        
        # Calcular la capacidad necesaria para cada ruta de la cuadrícula
        if len(rutas) > 0:
            capacidad_por_ruta = personas_a_evacuar // len(rutas)  # Distribuir las personas entre las rutas

            # Si la cantidad de personas no es divisible entre las rutas, la última ruta toma el resto
            for i, ruta in enumerate(rutas):
                if i == len(rutas) - 1:
                    # Asignar el resto de las personas a la última ruta
                    capacidades_rutas[ruta] = capacidad_por_ruta + (personas_a_evacuar % len(rutas))
                else:
                    capacidades_rutas[ruta] = capacidad_por_ruta

    return capacidades_rutas
g_r = generar_capacidad_maxima_rutas(R_qs, h_q)
# Tiempo caminando por cada ruta (en minutos)
def generar_tiempos_rutas(Ruts, tiempo1, tiempo2):
    t_c = {}  # Diccionario para almacenar los tiempos de las rutas
    
    # Recorremos cada cuadrícula y sus rutas
    for cuadrícula, rutas in Ruts.items():
        for ruta in rutas:
            # Asignamos un tiempo aleatorio entre t1 y t2 a cada ruta
            tiempo = random.randint(tiempo1, tiempo2)
            t_c[ruta] = tiempo
    
    return t_c
t_c = generar_tiempos_rutas(R_qs, t1, t2)
# Tiempo en auto por cada ruta (en minutos)
t_a = {ruta: int(tiempo * 0.4) for ruta, tiempo in t_c.items()}  # 40% del tiempo a pie

# Tiempo adicional por congestión (en minutos)
c_r = {ruta: 3 for ruta in g_r.keys()}

# Umbral de congestión (80% de la capacidad de la ruta)
l_r = {ruta: int(cap * 0.8) for ruta, cap in g_r.items()}

# Indicador de cuadrícula rural (1) o urbana (0)
def asignar_tipo_cuadriculas(num_cuadriculas):
    u_q = {i: random.choice([0, 1]) for i in range(num_cuadriculas)}
    return u_q
u_q = asignar_tipo_cuadriculas(len(Q))

# Asignación inicial de personas a vehículos (solo en zona rural)
a_i_v = {(i, v): 0 for i in P for v in V}
# Asignamos algunos vehículos a personas en la cuadrícula rural (1)
vehicles_assigned = 0
for i in P:
    if vehicles_assigned >= 20:  # Límite de vehículos
        break
    if any(p_i_q[(i, 1)] == 1 for q in Q):  # Si la persona está en la cuadrícula rural
        a_i_v[(i, vehicles_assigned)] = 1
        vehicles_assigned += 1

# Tiempo máximo para llegar a un lugar seguro (en minutos)
O = 30