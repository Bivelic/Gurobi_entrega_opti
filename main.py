import gurobipy as gp
from gurobipy import GRB
from datos import generate_test_data
import pandas as pd
import random
import time



def create_optimization_model(data):
    """
    Crea el modelo de optimización con restricciones corregidas
    """
    model = gp.Model("tsunami_evacuation")
    
    # Variables
    x = model.addVars([(i, r) for i in data['P'] 
                       for q in data['Q'] 
                       for s in data['S'] 
                       for r in data['Rqs'][(q, s)]],
                      vtype=GRB.CONTINUOUS, lb=0, name="x")
    
    z = model.addVars([(r) for q in data['Q'] 
                       for s in data['S'] 
                       for r in data['Rqs'][(q, s)]],
                      vtype=GRB.BINARY, name="z")
    
    ps = model.addVars([(s, i) for s in data['S'] for i in data['P']],
                       vtype=GRB.BINARY, name="ps")
    
    pr = model.addVars([(r, i) for q in data['Q'] 
                        for s in data['S'] 
                        for r in data['Rqs'][(q, s)]
                        for i in data['P']],
                       vtype=GRB.BINARY, name="pr")
    
    ms = model.addVar(vtype=GRB.BINARY, name="ms")
    
    y = model.addVars(data['V'], vtype=GRB.BINARY, name="y")
    
    # Función objetivo
    model.setObjective(gp.quicksum(x[i,r] for i in data['P'] 
                                 for q in data['Q'] 
                                 for s in data['S'] 
                                 for r in data['Rqs'][(q, s)]), 
                      GRB.MINIMIZE)
    
    # Activar evacuación
    model.addConstr(ms == 1)
    
    # Tiempo de evacuación
    for i in data['P']:
        for q in data['Q']:
            for s in data['S']:
                for r in data['Rqs'][(q, s)]:
                    if any(data['piq'][(i, q_)] == 1 for q_ in data['Q']):
                        model.addConstr(
                            x[i,r] >= 
                            (data['tc'][r] * (1 - gp.quicksum(data['aiv'][i,v] * data['uq'][q] 
                                                            for v in data['V'])) +
                            data['ta'][r] * gp.quicksum(data['aiv'][i,v] * data['uq'][q] 
                                                    for v in data['V'])) +
                            data['cr'][r] * z[r]
                        )
    
    # Tiempo máximo
    for i in data['P']:
        for q in data['Q']:
            for s in data['S']:
                for r in data['Rqs'][(q, s)]:
                    model.addConstr(x[i,r] <= data['O'])
    
    # Capacidad de rutas
    for q in data['Q']:
        for s in data['S']:
            for r in data['Rqs'][(q, s)]:
                model.addConstr(
                    gp.quicksum(pr[r,i] * y[v] * 8 for i in data['P'] for v in data['V']) +
                    gp.quicksum(pr[r,i] * (1 - gp.quicksum(data['aiv'][i,v] 
                                                        for v in data['V'])) 
                            for i in data['P']) <= data['gr'][r]
                )

    # Activación de congestión
    M = 1000  
    for (q, s) in data['Rqs'].keys():
        for r in data['Rqs'][(q, s)]:
            # Si el flujo supera el umbral, se activa la congestión
            model.addConstr(
                gp.quicksum(pr[r,i] for i in data['P']) - data['lr'][r] <= 
                M * z[r]
            )
            # Si hay congestión, el flujo debe superar el umbral
            model.addConstr(
                gp.quicksum(pr[r,i] for i in data['P']) >= 
                data['lr'][r] - M * (1 - z[r])
            )

    # Capacidad de puntos seguros
    for s in data['S']:
        model.addConstr(
            gp.quicksum(pr[r,i] for (q, s_check) in data['Rqs'].keys() 
                       if s_check == s
                       for r in data['Rqs'][(q, s)]
                       for i in data['P']) <= data['cs'][s]
        )

    # Restricciones de vehículos
    for v in data['V']:
        # Un vehículo solo puede ser usado si está asignado a alguien
        model.addConstr(
            y[v] <= gp.quicksum(data['aiv'][i,v] for i in data['P'])
        )
        
        # Si un vehículo está en uso, debe tener al menos una persona
        assigned_people = gp.quicksum(data['aiv'][i,v] for i in data['P'])
        model.addConstr(assigned_people >= y[v])
        
        # No más de 5 personas por vehículo
        model.addConstr(assigned_people <= 5)
    
    # Cada persona debe ser evacuada
    for i in data['P']:
        if any(data['piq'][(i, q)] == 1 for q in data['Q']):
            model.addConstr(
                gp.quicksum(ps[s,i] for s in data['S']) == 1
            )
    
    # Relación entre pr y ps
    for i in data['P']:
        for s in data['S']:
            accessible_routes = []
            for (q, s_check) in data['Rqs'].keys():
                if s_check == s and any(data['piq'][(i, q_)] == 1 for q_ in data['Q']):
                    accessible_routes.extend(data['Rqs'][(q, s)])
            
            if accessible_routes:
                model.addConstr(
                    gp.quicksum(pr[r,i] for r in accessible_routes) == ps[s,i]
                )
            else:
                model.addConstr(ps[s,i] == 0)
    
    return model

def analyze_infeasibility(model):
    print("\nAnalizando infactibilidad del modelo...")
    
    try:
        # Computar IIS
        model.computeIIS()
        
        # Obtener y mostrar restricciones infactibles
        print("\nRestricciones infactibles encontradas:")
        
        infeasible_constraints = []
        for c in model.getConstrs():
            if c.IISConstr:
                infeasible_constraints.append({
                    'nombre': c.ConstrName,
                    'expresion': str(model.getRow(c)),
                    'sentido': c.Sense,
                    'rhs': c.RHS
                })
        
        if infeasible_constraints:
            print(f"\nNúmero de restricciones infactibles: {len(infeasible_constraints)}")
            print("\nDetalles de las restricciones infactibles:")
            for i, constr in enumerate(infeasible_constraints, 1):
                print(f"\n{i}. Restricción: {constr['nombre']}")
                print(f"   Expresión: {constr['expresion']}")
                print(f"   Sentido: {constr['sentido']}")
                print(f"   RHS: {constr['rhs']}")
        
        # Analizar variables involucradas
        print("\nVariables involucradas en restricciones infactibles:")
        infeasible_vars = set()
        for c in model.getConstrs():
            if c.IISConstr:
                row = model.getRow(c)
                for i in range(row.size()):
                    var = row.getVar(i)
                    infeasible_vars.add(var.VarName)
        
        print(f"\nNúmero de variables involucradas: {len(infeasible_vars)}")
        print("Nombres de las variables:")
        for var in sorted(infeasible_vars):
            print(f"- {var}")
            
        return infeasible_constraints, infeasible_vars
        
    except Exception as e:
        print(f"Error al analizar infactibilidad: {str(e)}")
        return None, None

def check_data_consistency(data):
    issues = []
    
    # Verificar capacidades
    total_people = len(data['P'])
    total_capacity_safe_points = sum(data['cs'])
    if total_capacity_safe_points < total_people:
        issues.append(f"Capacidad total de puntos seguros ({total_capacity_safe_points}) es menor que el número de personas ({total_people})")
    
    # Verificar distribución de personas en cuadrículas
    total_assigned = sum(data['piq'].values())
    if total_assigned != total_people:
        issues.append(f"Número de personas asignadas a cuadrículas ({total_assigned}) no coincide con total de personas ({total_people})")
    
    # Verificar asignación de vehículos
    vehicles_per_person = {i: sum(data['aiv'].get((i,v), 0) for v in data['V']) for i in data['P']}
    multiple_vehicles = [i for i, count in vehicles_per_person.items() if count > 1]
    if multiple_vehicles:
        issues.append(f"Personas con múltiples vehículos asignados: {multiple_vehicles}")
    
    # Verificar tiempos de evacuación
    max_walking_time = max(data['tc'].values())
    if max_walking_time >= data['O']:
        issues.append(f"Tiempo máximo de caminata ({max_walking_time}) es mayor o igual al tiempo disponible ({data['O']})")
    
    return issues

def solve_and_analyze_with_diagnostics(model, data):
    """
    Resuelve el modelo e incluye diagnósticos detallados
    """
    # Verificar datos antes de resolver
    print("\nVerificando consistencia de datos...")
    issues = check_data_consistency(data)
    if issues:
        print("\nProblemas encontrados en los datos:")
        for issue in issues:
            print(f"- {issue}")
    else:
        print("Datos consistentes")
    
    # Configurar parámetros de Gurobi
    model.setParam('TimeLimit', 300)
    model.setParam('MIPGap', 0.1)
    model.setParam('NonConvex', 2)
    
    # Intentar resolver
    start_time = time.time()
    model.optimize()
    solve_time = time.time() - start_time
    
    results = {
        'status': model.status,
        'solve_time': solve_time,
        'num_variables': model.NumVars,
        'num_constraints': model.NumConstrs
    }
    
    # Analizar resultado
    if model.status == GRB.OPTIMAL:
        results.update({
            'objective_value': model.objVal,
            'gap': model.MIPGap
        })
    elif model.status == GRB.INFEASIBLE:
        print("\nModelo infactible. Analizando causas...")
        infeasible_constraints, infeasible_vars = analyze_infeasibility(model)
        results.update({
            'infeasible_constraints': infeasible_constraints,
            'infeasible_variables': infeasible_vars
        })
    
    return results

def analyze_optimal_solution(model, data, results):
    """
    Analiza la solución óptima y extrae información detallada
    """
    solution_stats = {}
    
    # 1. Tiempo máximo de evacuación y detalles
    max_time = 0
    slowest_person = None
    slowest_route = None
    for i in data['P']:
        for (q, s) in data['Rqs'].keys():
            for r in data['Rqs'][(q, s)]:
                var_name = f'x[{i},{r}]'
                var = model.getVarByName(var_name)
                if var is not None and var.X > max_time:
                    max_time = var.X
                    slowest_person = i
                    slowest_route = r
    
    solution_stats['max_evacuation_time'] = max_time
    solution_stats['slowest_person'] = slowest_person
    solution_stats['slowest_route'] = slowest_route
    
    # 2. Estadísticas de puntos seguros
    safe_points_stats = {}
    for s in data['S']:
        people_count = sum(1 for i in data['P'] 
                         if model.getVarByName(f'ps[{s},{i}]').X > 0.5)
        safe_points_stats[s] = {
            'total_people': people_count,
            'capacity': data['cs'][s],
            'utilization': (people_count / data['cs'][s]) * 100
        }
    solution_stats['safe_points'] = safe_points_stats
    
    # 3. Estadísticas de rutas
    route_stats = {}
    for (q, s) in data['Rqs'].keys():
        for r in data['Rqs'][(q, s)]:
            people_count = sum(1 for i in data['P'] 
                             if model.getVarByName(f'pr[{r},{i}]').X > 0.5)
            is_congested = model.getVarByName(f'z[{r}]').X > 0.5
            route_stats[r] = {
                'total_people': people_count,
                'capacity': data['gr'][r],
                'utilization': (people_count / data['gr'][r]) * 100,
                'is_congested': is_congested,
                'congestion_time': data['cr'][r] if is_congested else 0
            }
    solution_stats['routes'] = route_stats
    
    # 4. Estadísticas de vehículos
    vehicle_stats = {}
    for v in data['V']:
        if model.getVarByName(f'y[{v}]').X > 0.5:
            people_assigned = [i for i in data['P'] if data['aiv'][(i,v)] > 0.5]
            vehicle_stats[v] = {
                'total_people': len(people_assigned),
                'people_ids': people_assigned
            }
    solution_stats['vehicles'] = vehicle_stats
    
    # 5. Estadísticas generales
    solution_stats['general'] = {
        'total_people_evacuated': len(data['P']),
        'total_vehicles_used': len(vehicle_stats),
        'congested_routes': sum(1 for r_stat in route_stats.values() if r_stat['is_congested']),
        'average_evacuation_time': sum(model.getVarByName(f'x[{i},{r}]').X 
                                     for i in data['P'] 
                                     for (q, s) in data['Rqs'].keys() 
                                     for r in data['Rqs'][(q, s)] 
                                     if model.getVarByName(f'pr[{r},{i}]').X > 0.5) / len(data['P'])
    }
    
    return solution_stats

def print_solution_analysis(solution_stats):
    """
    Imprime el análisis detallado de la solución
    """
    print("\n" + "="*80)
    print("ANÁLISIS DETALLADO DE LA SOLUCIÓN")
    print("="*80)
    
    # 1. Información general
    print("\nESTADÍSTICAS GENERALES:")
    print(f"Total de personas evacuadas: {solution_stats['general']['total_people_evacuated']}")
    print(f"Vehículos utilizados: {solution_stats['general']['total_vehicles_used']}")
    print(f"Rutas congestionadas: {solution_stats['general']['congested_routes']}")
    print(f"Tiempo promedio de evacuación: {solution_stats['general']['average_evacuation_time']:.2f} minutos")
    
    # 2. Tiempo máximo de evacuación
    print("\nTIEMPO MÁXIMO DE EVACUACIÓN:")
    print(f"Tiempo: {solution_stats['max_evacuation_time']:.2f} minutos")
    print(f"Persona: {solution_stats['slowest_person']}")
    print(f"Ruta: {solution_stats['slowest_route']}")
    
    # 3. Puntos seguros
    print("\nESTADÍSTICAS DE PUNTOS SEGUROS:")
    for s, stats in solution_stats['safe_points'].items():
        print(f"\nPunto seguro {s}:")
        print(f"  Personas asignadas: {stats['total_people']}")
        print(f"  Capacidad total: {stats['capacity']}")
        print(f"  Utilización: {stats['utilization']:.2f}%")
    
    # 4. Rutas congestionadas
    print("\nRUTAS CONGESTIONADAS:")
    congested_routes = {r: stats for r, stats in solution_stats['routes'].items() 
                       if stats['is_congested']}
    if congested_routes:
        for r, stats in congested_routes.items():
            print(f"\nRuta {r}:")
            print(f"  Personas: {stats['total_people']}")
            print(f"  Capacidad: {stats['capacity']}")
            print(f"  Utilización: {stats['utilization']:.2f}%")
            print(f"  Tiempo adicional por congestión: {stats['congestion_time']} minutos")
    else:
        print("No hay rutas congestionadas")
    
    # 5. Vehículos
    print("\nUSO DE VEHÍCULOS:")
    for v, stats in solution_stats['vehicles'].items():
        print(f"\nVehículo {v}:")
        print(f"  Personas transportadas: {stats['total_people']}")
        print(f"  IDs de personas: {stats['people_ids']}")


def main():
    """
    Función principal con diagnósticos mejorados
    """
    print("Generando datos de prueba...")
    data = generate_test_data()
    
    print("\nCreando modelo de optimización...")
    model = create_optimization_model(data)
    
    print("\nResolviendo y analizando modelo...")
    results = solve_and_analyze_with_diagnostics(model, data)
    
    # Mostrar resultados detallados
    print("\nResultados del análisis:")
    print(f"Estado de la solución: {results['status']}")
    if results['status'] == GRB.OPTIMAL:
        print(f"Valor objetivo: {results['objective_value']:.2f}")
        print(f"GAP: {results['gap']*100:.2f}%")
        solution_stats = analyze_optimal_solution(model, data, results)
        print_solution_analysis(solution_stats)
    print(f"Tiempo de resolución: {results['solve_time']:.2f} segundos")
    print(f"Número total de variables: {results['num_variables']}")
    print(f"Número de restricciones: {results['num_constraints']}")

if __name__ == "__main__":
    main()