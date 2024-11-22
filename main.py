import gurobipy as gp
from gurobipy import GRB
from datos import *

# Crear modelo
model = gp.Model("tsunami_evacuation")

# Variables
x = {}
for i in P:
    for q in Q:
        for s in S:
            if (q,s) in R_qs:
                for r in R_qs[(q,s)]:
                    x[i,r] = model.addVar(vtype=GRB.CONTINUOUS, name=f'x_{i}_{r}')


zg = {}  
zf = {}  
for q in Q:
    for s in S:
        if (q,s) in R_qs:
            for r in R_qs[(q,s)]:
                zg[r] = model.addVar(vtype=GRB.BINARY, name=f'zg_{r}')
                zf[r] = model.addVar(vtype=GRB.BINARY, name=f'zf_{r}')

ps = {(i,s): model.addVar(vtype=GRB.BINARY, name=f'ps_{i}_{s}') for i in P for s in S}

pr = {}
for i in P:
    for q in Q:
        for s in S:
            if (q,s) in R_qs:
                for r in R_qs[(q,s)]:
                    pr[i,r] = model.addVar(vtype=GRB.BINARY, name=f'pr_{i}_{r}')

y = {v: model.addVar(vtype=GRB.BINARY, name=f'y_{v}') for v in V}

# Funcion Objetivo
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
                    if p_i_q[i,q] == 1:
                        model.addConstr(
                            x[i,r] >= (t_c[r] * (1 - sum(a_i_v[i,v] * u_q[q] for v in V)) +
                                    t_a[r] * sum(a_i_v[i,v] * u_q[q] for v in V)) * pr[i,r] +
                            c_r[r] * zg[r] * sum(a_i_v[i,v] * u_q[q] for v in V) * pr[i,r] +
                            c_r[r] * zf[r] * (1 - sum(a_i_v[i,v] * u_q[q] for v in V)) * pr[i,r]
                        )

# 2. Capacidad en rutas Autos
for q in Q:
    for s in S:
        if (q,s) in R_qs:
            for r in R_qs[(q,s)]:
                model.addConstr(
                    gp.quicksum(pr[i,r] * sum(a_i_v[i,v] * y[v] for v in V) for i in P) <= g_r[r]
                )

# 3. Capacidad en rutas peatones
for q in Q:
    for s in S:
        if (q,s) in R_qs:
            for r in R_qs[(q,s)]:
                model.addConstr(
                    gp.quicksum(pr[i,r] * (1 - sum(a_i_v[i,v] for v in V)) for i in P) <= f_r[r]
                )

# 4. Capacidad puntos seguros
for s in S:
    model.addConstr(
        gp.quicksum(ps[i,s] for i in P) <= c_s[s]
    )

# 5. Tiempo maximo de evacuacion
for i in P:
    for q in Q:
        for s in S:
            if (q,s) in R_qs:
                for r in R_qs[(q,s)]:
                    model.addConstr(x[i,r] <= O)

# 6. Activacion de congestion Autos
for q in Q:
    for s in S:
        if (q,s) in R_qs:
            for r in R_qs[(q,s)]:
                model.addConstr(
                    gp.quicksum(pr[i,r] * sum(a_i_v[i,v] * y[v] for v in V) for i in P) - l_r[r] <= 1000 * zg[r]
                )

# 7. Activacion de congestion Peatones
for q in Q:
    for s in S:
        if (q,s) in R_qs:
            for r in R_qs[(q,s)]:
                model.addConstr(
                    gp.quicksum(pr[i,r] * (1 - sum(a_i_v[i,v] for v in V)) for i in P) - l_r[r] <= 1000 * zf[r]
                )

# 8. Consistencia entre rutas y puntos seguros
for i in P:
    for s in S:
        model.addConstr(
            ps[i,s] == gp.quicksum(pr[i,r] for q in Q if (q,s) in R_qs for r in R_qs[(q,s)])
        )

# 9. Una persona por cuadrante
for i in P:
    model.addConstr(gp.quicksum(p_i_q[i,q] for q in Q) == 1)

# 10. Uso de autos en zonas urbanas
for v in V:
    model.addConstr(
        y[v] <= gp.quicksum(a_i_v[i,v] * p_i_q[i,q] * u_q[q] for i in P for q in Q)
    )

# 11. Capacidad de autos
for v in V:
    model.addConstr(gp.quicksum(a_i_v[i,v] for i in P) >= y[v])
    model.addConstr(gp.quicksum(a_i_v[i,v] for i in P) <= 5 * y[v])

# Optimize
model.optimize()

# Print results
if model.status == GRB.OPTIMAL:
    print("\nResultados de la optimización:")
    print(f"Tiempo total de evacuación: {model.objVal:.2f} minutos")
    
    evacuados_por_punto = {s: sum(ps[i,s].x for i in P) for s in S}
    print("\nDistribución de evacuados por punto seguro:")
    for s in S:
        if evacuados_por_punto[s] > 0:
            print(f"Punto seguro {s}: {evacuados_por_punto[s]:.0f} personas")
    
    rutas_congestionadas_autos = sum(1 for r in zg if zg[r].x > 0.5)
    rutas_congestionadas_peatones = sum(1 for r in zf if zf[r].x > 0.5)
    print(f"\nRutas congestionadas para vehículos: {rutas_congestionadas_autos}")
    print(f"Rutas congestionadas para peatones: {rutas_congestionadas_peatones}")
    
    vehiculos_usados = sum(1 for v in V if y[v].x > 0.5)
    print(f"Vehículos utilizados: {vehiculos_usados}")
else:
    print("No se encontró una solución óptima")