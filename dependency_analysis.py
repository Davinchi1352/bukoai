#!/usr/bin/env python3
"""
Análisis de dependencias circulares entre agentes
"""
import os
import re
import json
from collections import defaultdict, deque

def extract_agent_dependencies(agent_file_path):
    """Extraer dependencias de un archivo de agente"""
    dependencies = set()
    
    with open(agent_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Lista de todos los nombres de agentes posibles
    agent_names = [
        'analizador-arquitectura', 'desarrollador-frontend-ux', 'desarrollador-fullstack-backend',
        'desarrollador-editorial', 'database-optimizer', 'performance-analyzer', 
        'security-guardian', 'test-architect', 'deployment-manager', 'documentador-integral',
        'limpiador-codigo-profundo', 'reorganizador-codigo', 'experto-escalabilidad',
        'agente-inteligencia-negocio', 'agente-internacionalizacion', 'depurador',
        'api-docs-generator'
    ]
    
    # Buscar referencias a otros agentes
    for agent_name in agent_names:
        # Diferentes patrones de referencia
        patterns = [
            f"agente '{agent_name}'",
            f"agente '{agent_name.replace('-', '_')}'", 
            f"'{agent_name}'",
            f"{agent_name}",
            f"ejecutar {agent_name}",
            f"coordinar con '{agent_name}'",
            f"usar el agente {agent_name}",
        ]
        
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                dependencies.add(agent_name)
                break
    
    return dependencies

def extract_agent_name(file_path):
    """Extraer el nombre del agente del archivo"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar la línea name:
    match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    
    # Si no se encuentra, usar el nombre del archivo
    return os.path.basename(file_path).replace('.md', '')

def detect_cycles(graph):
    """Detectar ciclos en el grafo de dependencias usando DFS"""
    color = {}  # 0=blanco, 1=gris, 2=negro
    cycles = []
    
    def dfs(node, path):
        if node not in color:
            color[node] = 0
        
        if color[node] == 1:  # Ciclo detectado
            cycle_start = path.index(node)
            cycle = path[cycle_start:] + [node]
            cycles.append(cycle)
            return
        
        if color[node] == 2:  # Ya procesado
            return
        
        color[node] = 1  # Marcar como visitando
        
        for neighbor in graph.get(node, []):
            dfs(neighbor, path + [node])
        
        color[node] = 2  # Marcar como procesado
    
    for node in graph:
        if node not in color or color[node] == 0:
            dfs(node, [])
    
    return cycles

def analyze_dependencies():
    """Analizar dependencias entre agentes"""
    agents_dir = '/home/davinchi/bukoai/.claude/agents'
    
    # Mapear dependencias
    dependencies = {}
    agent_files = {}
    
    for file_name in os.listdir(agents_dir):
        if file_name.endswith('.md'):
            file_path = os.path.join(agents_dir, file_name)
            agent_name = extract_agent_name(file_path)
            agent_files[agent_name] = file_path
            deps = extract_agent_dependencies(file_path)
            dependencies[agent_name] = deps
    
    print("=== MAPA DE DEPENDENCIAS ===")
    for agent, deps in dependencies.items():
        if deps:
            print(f"{agent} -> {list(deps)}")
        else:
            print(f"{agent} -> (sin dependencias)")
    
    print("\n=== DETECCIÓN DE CICLOS ===")
    cycles = detect_cycles(dependencies)
    
    if cycles:
        print("🚨 CICLOS DETECTADOS:")
        for i, cycle in enumerate(cycles):
            print(f"Ciclo {i+1}: {' -> '.join(cycle)}")
    else:
        print("✅ No se detectaron ciclos")
    
    print("\n=== ANÁLISIS DE NIVELES ===")
    # Análisis de niveles jerárquicos
    levels = {}
    
    def calculate_level(agent, visited=None):
        if visited is None:
            visited = set()
        
        if agent in visited:
            return float('inf')  # Ciclo detectado
        
        if agent in levels:
            return levels[agent]
        
        deps = dependencies.get(agent, set())
        if not deps:
            levels[agent] = 0
            return 0
        
        visited.add(agent)
        max_dep_level = max(calculate_level(dep, visited.copy()) for dep in deps)
        visited.remove(agent)
        
        if max_dep_level == float('inf'):
            levels[agent] = float('inf')
        else:
            levels[agent] = max_dep_level + 1
        
        return levels[agent]
    
    for agent in dependencies:
        calculate_level(agent)
    
    # Organizar por niveles
    level_groups = defaultdict(list)
    for agent, level in levels.items():
        level_groups[level].append(agent)
    
    for level in sorted(level_groups.keys()):
        if level == float('inf'):
            print(f"Nivel ∞ (ciclos): {level_groups[level]}")
        else:
            print(f"Nivel {level}: {level_groups[level]}")
    
    return dependencies, cycles, levels

if __name__ == "__main__":
    analyze_dependencies()