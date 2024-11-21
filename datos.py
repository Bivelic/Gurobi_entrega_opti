# Conjuntos principales
P = range(500)  # Personas
S = range(10)   # Puntos seguros
Q = range(5)    # Cuadrículas
V = range(20)   # Vehículos

# Capacidad de puntos seguros
c_s = {
    0: 50,
    1: 52,
    2: 51,
    3: 53,
    4: 54,
    5: 55,
    6: 50,
    7: 52,
    8: 53,
    9: 50
}

# Rutas disponibles desde cada cuadrícula a puntos seguros
# Formato: {(cuadrícula, punto_seguro): [rutas]}
R_qs = {
    # Cuadrícula 0 tiene rutas a puntos seguros 0, 2, 4
    (0, 0): ['r_0_0_0', 'r_0_0_1'],
    (0, 2): ['r_0_2_0'],
    (0, 4): ['r_0_4_0', 'r_0_4_1'],
    
    # Cuadrícula 1 (rural) tiene rutas a puntos seguros 1, 3, 5
    (1, 1): ['r_1_1_0', 'r_1_1_1'],
    (1, 3): ['r_1_3_0'],
    (1, 5): ['r_1_5_0'],
    
    # Cuadrícula 2 tiene rutas a puntos seguros 2, 4, 6
    (2, 2): ['r_2_2_0', 'r_2_2_1'],
    (2, 4): ['r_2_4_0'],
    (2, 6): ['r_2_6_0'],
    
    # Cuadrícula 3 tiene rutas a puntos seguros 3, 5, 7
    (3, 3): ['r_3_3_0'],
    (3, 5): ['r_3_5_0', 'r_3_5_1'],
    (3, 7): ['r_3_7_0'],
    
    # Cuadrícula 4 tiene rutas a puntos seguros 6, 8, 9
    (4, 6): ['r_4_6_0'],
    (4, 8): ['r_4_8_0', 'r_4_8_1'],
    (4, 9): ['r_4_9_0']
}

# Distribución inicial de personas en cuadrículas
# Se asegura que la suma sea 500
h_q = {
    0: 120,  # 120 personas en cuadrícula 0
    1: 90,   # 90 personas en cuadrícula 1
    2: 100,  # 100 personas en cuadrícula 2
    3: 95,   # 95 personas en cuadrícula 3
    4: 95    # 95 personas en cuadrícula 4
}

# Matriz de personas en cuadrículas (1 si la persona i está en la cuadrícula q, 0 en otro caso)
p_i_q = {(i, q): 0 for i in P for q in Q}
current_person = 0
for q in Q:
    for i in range(current_person, current_person + h_q[q]):
        p_i_q[(i, q)] = 1
    current_person += h_q[q]

# Capacidad de las rutas
# Se asegura que sea suficiente para evacuar a las personas de cada cuadrícula
g_r = {
    # Rutas desde cuadrícula 0
    ('r_0_0_0'): 70, ('r_0_0_1'): 60, ('r_0_2_0'): 65, ('r_0_4_0'): 70, ('r_0_4_1'): 60,
    
    # Rutas desde cuadrícula 1
    ('r_1_1_0'): 50, ('r_1_1_1'): 50, ('r_1_3_0'): 45, ('r_1_5_0'): 45,
    
    # Rutas desde cuadrícula 2
    ('r_2_2_0'): 60, ('r_2_2_1'): 50, ('r_2_4_0'): 55, ('r_2_6_0'): 55,
    
    # Rutas desde cuadrícula 3
    ('r_3_3_0'): 50, ('r_3_5_0'): 55, ('r_3_5_1'): 45, ('r_3_7_0'): 50,
    
    # Rutas desde cuadrícula 4
    ('r_4_6_0'): 50, ('r_4_8_0'): 55, ('r_4_8_1'): 45, ('r_4_9_0'): 50
}

# Tiempo caminando por cada ruta (en minutos)
t_c = {
    # Rutas desde cuadrícula 0
    ('r_0_0_0'): 12, ('r_0_0_1'): 15, ('r_0_2_0'): 10, ('r_0_4_0'): 14, ('r_0_4_1'): 16,
    
    # Rutas desde cuadrícula 1
    ('r_1_1_0'): 11, ('r_1_1_1'): 13, ('r_1_3_0'): 15, ('r_1_5_0'): 12,
    
    # Rutas desde cuadrícula 2
    ('r_2_2_0'): 10, ('r_2_2_1'): 12, ('r_2_4_0'): 14, ('r_2_6_0'): 13,
    
    # Rutas desde cuadrícula 3
    ('r_3_3_0'): 11, ('r_3_5_0'): 13, ('r_3_5_1'): 15, ('r_3_7_0'): 12,
    
    # Rutas desde cuadrícula 4
    ('r_4_6_0'): 10, ('r_4_8_0'): 12, ('r_4_8_1'): 14, ('r_4_9_0'): 11
}

# Tiempo en auto por cada ruta (en minutos)
t_a = {ruta: int(tiempo * 0.4) for ruta, tiempo in t_c.items()}  # 40% del tiempo a pie

# Tiempo adicional por congestión (en minutos)
c_r = {ruta: 3 for ruta in g_r.keys()}

# Umbral de congestión (80% de la capacidad de la ruta)
l_r = {ruta: int(cap * 0.8) for ruta, cap in g_r.items()}

# Indicador de cuadrícula rural (1) o urbana (0)
u_q = {
    0: 0,
    1: 1,  # Cuadrícula 1 es rural
    2: 0,
    3: 0,
    4: 0
}

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