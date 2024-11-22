import gurobipy as gp
from gurobipy import GRB
from datos_entrega4 import *

model = gp.Model("tsunami_evacuation")

# añadimos las variables del latex
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


max_x = model.addVar(name=f"max_x", vtype=GRB.CONTINUOUS)

# f.o
model.setObjective(max_x , GRB.MINIMIZE)

# restricciones
# max_x tiene que ser mayor que le tiempo maximo de cada persona
for i in P:
    for q in Q:
        for s in S:
            if (q, s) in R_qs:
                for r in R_qs[(q, s)]:
                    model.addConstr(max_x >= x[i, r], name=f"max_constr_{i}_{q}_{s}_{r}")

# tiempo de evacuación por ruta
for i in P:
    for q in Q:
        for s in S:
            if (q,s) in R_qs:
                for r in R_qs[(q,s)]:
                    if p_i_q[i,q] == 1:
                        model.addConstr(
                            x[i,r] == (t_c[r] * (1 - sum(a_i_v[i,v] * u_q[q] for v in V)) +
                                       t_a[r] * sum(a_i_v[i,v] * u_q[q] for v in V)) +
                            c_r[r] * zg[r] * sum(a_i_v[i,v] * u_q[q] for v in V) +
                            c_r[r] * zf[r] * (1 - sum(a_i_v[i,v] * u_q[q] for v in V))
                        )

# capacidad de rutas hablando de autos 
for q in Q:
    for s in S:
        if (q,s) in R_qs:
            for r in R_qs[(q,s)]:
                model.addConstr(
                    gp.quicksum(pr[i,r] * sum(a_i_v[i,v] * y[v] for v in V) for i in P) <= g_r[r]
                )

# capacidad de rutas hablando de peatones
for q in Q:
    for s in S:
        if (q,s) in R_qs:
            for r in R_qs[(q,s)]:
                model.addConstr(
                    gp.quicksum(pr[i,r] * (1 - sum(a_i_v[i,v] for v in V)) for i in P) <= f_r[r]
                )

# capacidad de puntos seguros
for s in S:
    model.addConstr(
        gp.quicksum(pr[i,r] for q in Q for r in R_qs[(q,s)] for i in P) <= c_s[s]
    )

# cada persona debe ir a exactamente un punto seguro
for i in P:
    model.addConstr(
        gp.quicksum(ps[i,s] for s in S) == 1
    )

# tiempo máximo de evacuación
for i in P:
    for q in Q:
        for s in S:
            if (q,s) in R_qs:
                for r in R_qs[(q,s)]:
                    model.addConstr(x[i,r] <= O)

# activación de taco de auto 
for q in Q:
    for s in S:
        if (q,s) in R_qs:
            for r in R_qs[(q,s)]:
                model.addConstr(
                    gp.quicksum(pr[i,r] for i in P) - l_r[r] <= 1000 * zg[r]
                )

# activacion de taco de veredas
for q in Q:
    for s in S:
        if (q,s) in R_qs:
            for r in R_qs[(q,s)]:
                model.addConstr(
                    gp.quicksum(pr[i,r] for i in P) - l_r[r] <= 1000 * zg[r]
                )

# persona asignada a un punto seguro
for i in P:
    for s in S:
        model.addConstr(
            ps[i,s] == gp.quicksum(pr[i,r] for q in Q if (q,s) in R_qs for r in R_qs[(q,s)])
        )

# una persona solo puede estar en una cuadrícula
for i in P:
    model.addConstr(
        gp.quicksum(p_i_q[i,q] for q in Q) == 1
    )

# solo se usan autos en las cuadriculas urbanas
for v in V:
    model.addConstr(
        y[v] <= gp.quicksum(a_i_v[i,v] * p_i_q[i,q] * u_q[q] for i in P for q in Q)
    )

# restricciones de capacidad de los autos
for v in V:
    # minimo una persona por auto en uso
    model.addConstr(
        gp.quicksum(a_i_v[i,v] for i in P) >= y[v]
    )
    # maximo 5 personas por auto
    model.addConstr(
        gp.quicksum(a_i_v[i,v] for i in P) <= 5 * y[v]
    )

# optimizar modelo
model.optimize()

# imprimir resultados
if model.status == GRB.OPTIMAL:
    print("\nResultados de la optimización:")
    a = model.objVal
    print(f"Tiempo total de evacuación: {model.objVal} minutos")
    print(f"Tiempo promedio de evacuación: {a/len(P)} minutos")
    evacuados_por_punto = {s: sum(ps[i,s].x for i in P) for s in S}
    print("\nDistribución de evacuados por punto seguro:")
    for s in S:
        if evacuados_por_punto[s] > 0:
            print(f"Punto seguro {s}: {evacuados_por_punto[s]:.0f} personas")
    rutas_congestionadas = sum(1 for r in zg if zg[r].x > 0.5)
    print(f"\nCalles congestionadas: {rutas_congestionadas}")
    rutas_congestionadas = sum(1 for r in zf if zf[r].x > 0.5)
    print(f"\nVereddas congestionadas: {rutas_congestionadas}")
    vehiculos_usados = sum(1 for v in V if y[v].x > 0.5)
    print(f"Vehículos utilizados: {vehiculos_usados}")

else:
    print("No se encontró una solución óptima")