P = range(500)
S = range(6)
Q = range(15)
V = range(20)

# capacidad de puntos seguros (c_s)
c_s = {
    s: max(250, 300 - abs(s - 5) * 4) for s in S
}

# rutas disponibles desde cada cuadricula a puntos seguros (con rutas por defecto)
R_qs = {}
for q in Q:
    for s in S:
        route_main = f'r_{q}_{s}_0'
        route_alt = f'r_{q}_{s}_1'
        R_qs[(q,s)] = [route_main, route_alt]

# capacidad de rutas (g_r) reducida
g_r = {}
f_r = {}
for q in Q:
    for s in S:
        for r in R_qs[(q,s)]:
            if r.endswith('_0'):
                g_r[r] = 20
                f_r[r] = 60
            else:
                g_r[r] = 10
                f_r[r] = 50

# distribución inicial de personas en cuadriculas
h_q = {q: 100 for q in Q}

# matriz de personas en cuadriculas
p_i_q = {(i, q): 0 for i in P for q in Q}
current_person = 0
for q in Q:
    for i in range(current_person, current_person + h_q[q]):
        p_i_q[(i, q)] = 1
    current_person += h_q[q]

# tiempos de desplazamiento
t_c = {}
t_a = {}
c_r = {}
for q in Q:
    for s in S:
        for r in R_qs[(q,s)]:
            if r.endswith('_0'):
                t_c[r] = 15 + (q + s) % 5
                t_a[r] = int(t_c[r] * 0.4)
            else:
                t_c[r] = 18 + (q + s) % 5
                t_a[r] = int(t_c[r] * 0.4)
            
            c_r[r] = 3

# umbral de congestión
l_r = {ruta: int(cap * 0.75) for ruta, cap in g_r.items()}

# indicador de cuadricula rural
u_q = {q: 1 if q in [3, 8, 13] else 0 for q in Q}

# asignación inicial de personas a vehiculos
a_i_v = {(i, v): 0 for i in P for v in V}
vehicles_assigned = 0
for i in P:
    if vehicles_assigned >= len(V):
        break
    for q in [3, 8, 10, 12, 13]: # aca tenemos que cambia a mano las cuadriculas que son rurales
        if p_i_q[i,q] == 1:
            a_i_v[(i, vehicles_assigned)] = 1
            vehicles_assigned += 1
            if vehicles_assigned >= len(V):
                break

# tiempo máximo para llegar a un lugar seguro
O = 40 #esto esta en minutos