
P = range(5000)  # Personas
S = range(20)    # Puntos seguros
Q = range(25)    # Cuadrículas
V = range(200)   # Vehículos

# Capacidad de puntos seguros (c_s)
c_s = {
    s: max(300, 325 - abs(s - 10) * 5) for s in S
}

# Rutas disponibles desde cada cuadricula a puntos seguros
R_qs = {
    # Cuadrículas 0-4
    (0, 0): ['r_0_0_0', 'r_0_0_1'], (0, 1): ['r_0_1_0'], (0, 2): ['r_0_2_0', 'r_0_2_1'],
    (1, 1): ['r_1_1_0', 'r_1_1_1'], (1, 2): ['r_1_2_0'], (1, 3): ['r_1_3_0', 'r_1_3_1'],
    (2, 2): ['r_2_2_0'], (2, 3): ['r_2_3_0', 'r_2_3_1'], (2, 4): ['r_2_4_0'],
    (3, 3): ['r_3_3_0', 'r_3_3_1'], (3, 4): ['r_3_4_0'], (3, 5): ['r_3_5_0', 'r_3_5_1'],
    (4, 4): ['r_4_4_0'], (4, 5): ['r_4_5_0', 'r_4_5_1'], (4, 6): ['r_4_6_0'],

    # Cuadrículas 5-9
    (5, 5): ['r_5_5_0', 'r_5_5_1'], (5, 6): ['r_5_6_0'], (5, 7): ['r_5_7_0', 'r_5_7_1'],
    (6, 6): ['r_6_6_0'], (6, 7): ['r_6_7_0', 'r_6_7_1'], (6, 8): ['r_6_8_0'],
    (7, 7): ['r_7_7_0', 'r_7_7_1'], (7, 8): ['r_7_8_0'], (7, 9): ['r_7_9_0', 'r_7_9_1'],
    (8, 8): ['r_8_8_0'], (8, 9): ['r_8_9_0', 'r_8_9_1'], (8, 10): ['r_8_10_0'],
    (9, 9): ['r_9_9_0', 'r_9_9_1'], (9, 10): ['r_9_10_0'], (9, 11): ['r_9_11_0', 'r_9_11_1'],

    # Cuadrículas 10-14
    (10, 10): ['r_10_10_0'], (10, 11): ['r_10_11_0', 'r_10_11_1'], (10, 12): ['r_10_12_0'],
    (11, 11): ['r_11_11_0', 'r_11_11_1'], (11, 12): ['r_11_12_0'], (11, 13): ['r_11_13_0', 'r_11_13_1'],
    (12, 12): ['r_12_12_0'], (12, 13): ['r_12_13_0', 'r_12_13_1'], (12, 14): ['r_12_14_0'],
    (13, 13): ['r_13_13_0', 'r_13_13_1'], (13, 14): ['r_13_14_0'], (13, 15): ['r_13_15_0', 'r_13_15_1'],
    (14, 14): ['r_14_14_0'], (14, 15): ['r_14_15_0', 'r_14_15_1'], (14, 16): ['r_14_16_0'],

    # Cuadrículas 15-19
    (15, 15): ['r_15_15_0', 'r_15_15_1'], (15, 16): ['r_15_16_0'], (15, 17): ['r_15_17_0', 'r_15_17_1'],
    (16, 16): ['r_16_16_0'], (16, 17): ['r_16_17_0', 'r_16_17_1'], (16, 18): ['r_16_18_0'],
    (17, 17): ['r_17_17_0', 'r_17_17_1'], (17, 18): ['r_17_18_0'], (17, 19): ['r_17_19_0', 'r_17_19_1'],
    (18, 18): ['r_18_18_0'], (18, 19): ['r_18_19_0', 'r_18_19_1'], (18, 0): ['r_18_0_0'],
    (19, 19): ['r_19_19_0', 'r_19_19_1'], (19, 0): ['r_19_0_0'], (19, 1): ['r_19_1_0', 'r_19_1_1'],

    # Cuadrículas 20-24
    (20, 0): ['r_20_0_0', 'r_20_0_1'], (20, 1): ['r_20_1_0'], (20, 2): ['r_20_2_0', 'r_20_2_1'],
    (21, 1): ['r_21_1_0'], (21, 2): ['r_21_2_0', 'r_21_2_1'], (21, 3): ['r_21_3_0'],
    (22, 2): ['r_22_2_0', 'r_22_2_1'], (22, 3): ['r_22_3_0'], (22, 4): ['r_22_4_0', 'r_22_4_1'],
    (23, 3): ['r_23_3_0'], (23, 4): ['r_23_4_0', 'r_23_4_1'], (23, 5): ['r_23_5_0'],
    (24, 4): ['r_24_4_0', 'r_24_4_1'], (24, 5): ['r_24_5_0'], (24, 6): ['r_24_6_0', 'r_24_6_1']
} 
# Keeping the original R_qs from the previous data file

# Capacidad de rutas (g_r) considerando capacidad para autos
g_r = {}
f_r = {}  # Capacidad para peatones
for q in Q:
    for s in S:
        if (q,s) in R_qs:
            for r in R_qs[(q,s)]:
                if r.endswith('_0'):  # Ruta principal
                    g_r[r] = 150  # Capacidad para autos
                    f_r[r] = 80   # Capacidad para peatones
                else:  # Ruta alternativa
                    g_r[r] = 100  # Capacidad para autos
                    f_r[r] = 50   # Capacidad para peatones

# Distribución inicial de personas en cuadriculas
h_q = {q: 200 for q in Q}

# Matriz de personas en cuadriculas
p_i_q = {(i, q): 0 for i in P for q in Q}
current_person = 0
for q in Q:
    for i in range(current_person, current_person + h_q[q]):
        p_i_q[(i, q)] = 1
    current_person += h_q[q]

# Tiempos de desplazamiento
t_c = {}  # Tiempo caminando
t_a = {}  # Tiempo en auto
c_r = {}  # Tiempo adicional por congestión
for q in Q:
    for s in S:
        if (q,s) in R_qs:
            for r in R_qs[(q,s)]:
                if r.endswith('_0'):  # Ruta principal
                    t_c[r] = 15 + (q + s) % 6  # 15-20 minutos
                    t_a[r] = int(t_c[r] * 0.4)  # Reducción de tiempo en auto
                else:  # Ruta alternativa
                    t_c[r] = 18 + (q + s) % 8  # 18-25 minutos
                    t_a[r] = int(t_c[r] * 0.4)
                
                c_r[r] = 4  # Tiempo adicional por congestión

# Umbral de congestión
l_r = {ruta: int(cap * 0.8) for ruta, cap in g_r.items()}

# Indicador de cuadricula rural
u_q = {q: 1 if q in [3, 8, 13, 18, 23] else 0 for q in Q}

# Asignación inicial de personas a vehiculos
a_i_v = {(i, v): 0 for i in P for v in V}
vehicles_assigned = 0
for i in P:
    if vehicles_assigned >= len(V):
        break
    for q in [3, 8, 13, 18, 23]:  # Cuadriculas rurales
        if p_i_q[i,q] == 1:
            a_i_v[(i, vehicles_assigned)] = 1
            vehicles_assigned += 1
            if vehicles_assigned >= len(V):
                break

# Tiempo máximo para llegar a un lugar seguro
O = 45