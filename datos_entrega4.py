# Conjuntos principales (reducidos)
P = range(500)  # Personas (reducido de 5000)
S = range(6)    # Puntos seguros (reducido de 20)
Q = range(15)    # Cuadrículas (reducido de 25)
V = range(80)   # Vehículos (reducido de 200)

# Capacidad de puntos seguros (c_s)
c_s = {
    s: max(250, 300 - abs(s - 5) * 4) for s in S
}

# Rutas disponibles desde cada cuadricula a puntos seguros (con rutas por defecto)
R_qs = {}
for q in Q:
    for s in S:
        # Generar rutas predeterminadas para cada combinación de cuadrícula y punto seguro
        route_main = f'r_{q}_{s}_0'
        route_alt = f'r_{q}_{s}_1'
        R_qs[(q,s)] = [route_main, route_alt]

# Capacidad de rutas (g_r) reducida
g_r = {}
f_r = {}  # Capacidad para peatones
for q in Q:
    for s in S:
        for r in R_qs[(q,s)]:
            if r.endswith('_0'):  # Ruta principal
                g_r[r] = 20  # Capacidad para autos
                f_r[r] = 60   # Capacidad para peatones
            else:  # Ruta alternativa
                g_r[r] = 10  # Capacidad para autos
                f_r[r] = 50   # Capacidad para peatones

# Distribución inicial de personas en cuadriculas
h_q = {q: 100 for q in Q}  # Reducido de 200

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
        for r in R_qs[(q,s)]:
            if r.endswith('_0'):  # Ruta principal
                t_c[r] = 15 + (q + s) % 5  # Reducido rango de variación
                t_a[r] = int(t_c[r] * 0.4)
            else:  # Ruta alternativa
                t_c[r] = 18 + (q + s) % 5
                t_a[r] = int(t_c[r] * 0.4)
            
            c_r[r] = 3  # Reducido tiempo de congestión

# Umbral de congestión
l_r = {ruta: int(cap * 0.75) for ruta, cap in g_r.items()}

# Indicador de cuadricula rural
u_q = {q: 1 if q in [3, 8, 13] else 0 for q in Q}  # Reducido número de cuadrículas rurales

# Asignación inicial de personas a vehiculos
a_i_v = {(i, v): 0 for i in P for v in V}
vehicles_assigned = 0
for i in P:
    if vehicles_assigned >= len(V):
        break
    for q in [3, 8, 13]:  # Cuadriculas rurales reducidas
        if p_i_q[i,q] == 1:
            a_i_v[(i, vehicles_assigned)] = 1
            vehicles_assigned += 1
            if vehicles_assigned >= len(V):
                break

# Tiempo máximo para llegar a un lugar seguro
O = 40  # Ligeramente reducido