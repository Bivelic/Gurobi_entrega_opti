import gurobipy as gp
from gurobipy import GRB
from datos_entrega4 import *

# Crear modelo
model = gp.Model("tsunami_evacuation")

# Variables de decisión
# x_irqsn: tiempo que toma la persona i en la ruta r
x = {}
for i in P:
    for q in Q:
        for s in S:
            if (q,s) in R_qs:  # Solo para rutas que existen
                for r in R_qs[(q,s)]:
                    x[i,r] = model.addVar(vtype=GRB.CONTINUOUS, name=f'x_{i}_{r}')

# zg_r: indica si hay congestión en la ruta r para autos
zg = {}
for q in Q:
    for s in S:
        if (q,s) in R_qs:
            for r in R_qs[(q,s)]:
                zg[r] = model.addVar(vtype=GRB.BINARY, name=f'zg_{r}')

# zf_r: indica si hay congestión en la ruta r para peatones
zf = {}
for q in Q:
    for s in S:
        if (q,s) in R_qs:
            for r in R_qs[(q,s)]:
                zf[r] = model.addVar(vtype=GRB.BINARY, name=f'zf_{r}')

# ps_i_s: indica si la persona i irá al punto seguro s
ps = {}
for i in P:
    for s in S:
        ps[i,s] = model.addVar(vtype=GRB.BINARY, name=f'ps_{i}_{s}')

# pr_i_r: indica si la persona i usa la ruta r
pr = {}
for i in P:
    for q in Q:
        for s in S:
            if (q,s) in R_qs:
                for r in R_qs[(q,s)]:
                    pr[i,r] = model.addVar(vtype=GRB.BINARY, name=f'pr_{i}_{r}')

# y_v: indica si el vehículo v está en uso
y = {}
for v in V:
    y[v] = model.addVar(vtype=GRB.BINARY, name=f'y_{v}')

# Función objetivo: minimizar tiempo total de evacuación
model.setObjective(
    gp.quicksum(x[i,r] for i in P for q in Q for s in S if (q,s) in R_qs for r in R_qs[(q,s)]),
    GRB.MINIMIZE
)

# Restricciones

# 1. Tiempo de evacuación por ruta
for i in P:
    for q in Q:
        for s in S:
            if (q,s) in R_qs:
                for r in R_qs[(q,s)]:
                    if p_i_q[i,q] == 1:  # Only if the person is in that grid
                        model.addConstr(
                            x[i,r] == (t_c[r] * (1 - sum(a_i_v[i,v] * u_q[q] for v in V)) +
                                       t_a[r] * sum(a_i_v[i,v] * u_q[q] for v in V)) +
                            c_r[r] * zg[r] * sum(a_i_v[i,v] * u_q[q] for v in V) +
                            c_r[r] * zf[r] * (1 - sum(a_i_v[i,v] * u_q[q] for v in V))
                        )

# 2. Capacidad de rutas apartir de autos 
for q in Q:
    for s in S:
        if (q,s) in R_qs:
            for r in R_qs[(q,s)]:
                model.addConstr(
                    gp.quicksum(pr[i,r] * sum(a_i_v[i,v] * y[v] for v in V) for i in P) <= g_r[r]
                )

# 2. Capacidad de rutas apartir de peatones tenemos que añadir el f_r en los datos que es la capacidad de las vredas
for q in Q:
    for s in S:
        if (q,s) in R_qs:
            for r in R_qs[(q,s)]:
                model.addConstr(
                    gp.quicksum(pr[i,r] * (1 - sum(a_i_v[i,v] for v in V)) for i in P) <= f_r[r]
                )

# 3. Capacidad de puntos seguros
for s in S:
    model.addConstr(
        gp.quicksum(pr[i,r] for q in Q for r in R_qs[(q,s)] for i in P) <= c_s[s]
    )

# 4. Cada persona debe ir a exactamente un punto seguro
for i in P:
    model.addConstr(
        gp.quicksum(ps[i,s] for s in S) == 1
    )

# 5. Tiempo máximo de evacuación
for i in P:
    for q in Q:
        for s in S:
            if (q,s) in R_qs:
                for r in R_qs[(q,s)]:
                    model.addConstr(x[i,r] <= O)

# 6. Activación de congestión de auto 
for q in Q:
    for s in S:
        if (q,s) in R_qs:
            for r in R_qs[(q,s)]:
                model.addConstr(
                    gp.quicksum(pr[i,r] for i in P) - l_r[r] <= 1000 * zg[r]
                )

#6.1 activacion de congestion de veredas
for q in Q:
    for s in S:
        if (q,s) in R_qs:
            for r in R_qs[(q,s)]:
                model.addConstr(
                    gp.quicksum(pr[i,r] for i in P) - l_r[r] <= 1000 * zg[r]
                )

#7 Consistencia entre rutas y puntos seguros
for i in P:
    for s in S:
        model.addConstr(
            ps[i,s] == gp.quicksum(pr[i,r] for q in Q if (q,s) in R_qs for r in R_qs[(q,s)])
        )

# 8. Una persona solo puede estar en una cuadrícula
for i in P:
    model.addConstr(
        gp.quicksum(p_i_q[i,q] for q in Q) == 1
    )

# 9. Restricción de uso de vehículos en zonas urbanas
for v in V:
    model.addConstr(
        y[v] <= gp.quicksum(a_i_v[i,v] * p_i_q[i,q] * u_q[q] for i in P for q in Q)
    )

# 10. Restricciones de capacidad de vehículos
for v in V:
    # Mínimo una persona por vehículo en uso
    model.addConstr(
        gp.quicksum(a_i_v[i,v] for i in P) >= y[v]
    )
    # Máximo 5 personas por vehículo
    model.addConstr(
        gp.quicksum(a_i_v[i,v] for i in P) <= 5 * y[v]
    )

# Optimizar modelo
model.optimize()

# Imprimir resultados
if model.status == GRB.OPTIMAL:
    print("\nResultados de la optimización:")
    print(f"Tiempo total de evacuación: {model.objVal:.2f} minutos")
    
    # Contar personas evacuadas por punto seguro
    evacuados_por_punto = {s: sum(ps[i,s].x for i in P) for s in S}
    print("\nDistribución de evacuados por punto seguro:")
    for s in S:
        if evacuados_por_punto[s] > 0:
            print(f"Punto seguro {s}: {evacuados_por_punto[s]:.0f} personas")
    
    # Contar rutas congestionadas
    rutas_congestionadas = sum(1 for r in zg if zg[r].x > 0.5)
    print(f"\nCalles congestionadas: {rutas_congestionadas}")
    
    rutas_congestionadas = sum(1 for r in zf if zf[r].x > 0.5)
    print(f"\nVereddas congestionadas: {rutas_congestionadas}")

    # Vehículos utilizados
    vehiculos_usados = sum(1 for v in V if y[v].x > 0.5)
    print(f"Vehículos utilizados: {vehiculos_usados}")

else:
    print("No se encontró una solución óptima")