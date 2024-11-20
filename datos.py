import random

def generate_test_data(num_people=10900, num_safe_points=18, num_grids=66, num_vehicles=529):
    """
    Genera datos de prueba realistas con correcciones
    """
    data = {
        # Conjuntos base
        'P': range(num_people),
        'S': range(num_safe_points),
        'Q': range(num_grids),
        'V': range(num_vehicles),
        'O': 25,  
    }
    
    # Capacidad de puntos seguros
    min_capacity = num_people // num_safe_points + 1
    data['cs'] = [random.randint(min_capacity, min_capacity * 2) 
                  for _ in range(num_safe_points)]
    
    # Generar rutas
    data['Rqs'] = {(q, s): [f"r_{q}_{s}_0"] 
                   for q in range(num_grids) 
                   for s in range(num_safe_points)}
    
    # Parámetros por ruta con tiempos ajustados
    data['gr'] = {}
    data['tc'] = {}
    data['ta'] = {}
    data['cr'] = {}
    data['lr'] = {}
    
    for q in range(num_grids):
        for s in range(num_safe_points):
            for r in data['Rqs'][(q, s)]:
                data['gr'][r] = random.randint(max(20, num_people // (num_grids * num_safe_points)), 
                                             max(40, num_people // (num_grids * num_safe_points) * 2))
                data['tc'][r] = random.randint(5, min(15, data['O'] - 5))
                data['ta'][r] = random.randint(2, min(8, data['O'] - 5))
                data['cr'][r] = random.randint(1, min(4, data['O'] - max(data['tc'][r], data['ta'][r])))
                data['lr'][r] = data['gr'][r] * 0.8
    
    # Asignar personas a cuadrículas de manera controlada
    data['uq'] = {q: random.choice([0]) for q in range(num_grids)}
    data['hq'] = {}
    data['piq'] = {}
    
    data['piq'] = {(i, q): 1 if q == random.choice(range(num_grids)) else 0 
               for i in range(num_people) for q in range(num_grids)}
    
    # Asignación de vehículos controlada
    data['aiv'] = {(i, v): 0 for i in range(num_people) for v in range(num_vehicles)}
    vehicles_assigned = 0
    for i in range(num_people):
        if vehicles_assigned >= num_vehicles:
            break
        if random.random() < 0.3:  
            data['aiv'][(i, vehicles_assigned)] = 1
            vehicles_assigned += 1
    
    return data