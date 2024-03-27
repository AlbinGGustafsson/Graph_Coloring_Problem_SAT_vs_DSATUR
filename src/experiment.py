import os
import time
import datetime
import random
import string
import csv
import networkx as nx
from pysat.solvers import Cadical153

UPPER_BOUND_STRATEGY = "largest_first"
TIME_LIMIT = 999999999
CONFLICT_BUDGET = 50000

def read_graph_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    num_vertices = 0
    edges = []
    for line in lines:
        if line.startswith('p edge'):
            num_vertices = int(line.split()[2])
        elif line.startswith('e'):
            parts = line.split()
            edges.append((int(parts[1]), int(parts[2])))

    return num_vertices, edges

def create_graph(edges):
    graph = nx.Graph()
    graph.add_edges_from(edges)
    return graph


def color_graph_dsatur(graph):
    start_time = time.perf_counter()
    coloring = nx.coloring.greedy_color(graph, strategy="DSATUR")
    end_time = time.perf_counter()
    return coloring, end_time - start_time


def relabel_graph(graph):
    vertex_mapping = {old_label: new_label for new_label, old_label in enumerate(graph.nodes())}
    return nx.relabel_nodes(graph, vertex_mapping)


def sat_helper(graph, output_file, dsatur_coloring):
    matched_time_dsatur = 999

    start_time = time.perf_counter()
    max_colors = len(set(nx.coloring.greedy_color(graph, strategy=UPPER_BOUND_STRATEGY).values()))
    upper_bound_calc_time = time.perf_counter() - start_time
    write_and_print(output_file, f"Upper bound {max_colors} calculated using {UPPER_BOUND_STRATEGY} in: {upper_bound_calc_time}")

    acc_time = upper_bound_calc_time
    best_coloring = None
    best_iteration_time = None

    while True:
        start_time_iteration = time.perf_counter()
        coloring = color_graph_sat(graph, max_colors)
        iteration_time = time.perf_counter() - start_time_iteration

        if acc_time > TIME_LIMIT:
            write_and_print(output_file, f"Time limit: {TIME_LIMIT} reached")
            break

        if coloring is not None:
            colors_used = len(set(coloring.values()))
            best_coloring = coloring
            acc_time = time.perf_counter() - start_time
            write_and_print(output_file, f"Colors used: {colors_used}, Colors considered: {max_colors}, Acc time: {acc_time}, Iteration time: {iteration_time}")
            if colors_used == dsatur_coloring:
                matched_time_dsatur = acc_time
            best_iteration_time = iteration_time

        else:
            write_and_print(output_file, f"No valid coloring found with current conflicts budget, acc time: {time.perf_counter() - start_time}")
            break

        max_colors = colors_used - 1

    if matched_time_dsatur == 999:
        matched_time_dsatur = acc_time

    return best_coloring, acc_time, matched_time_dsatur, best_iteration_time


def color_graph_sat(graph, max_colors):
    num_vertices = graph.number_of_nodes()
    solver = Cadical153()
    solver.conf_budget(CONFLICT_BUDGET)

    # Generate variables
    # variables[i][c] is the variable for vertex i having color c
    #variables = [[(i * max_colors + c + 1) for c in range(max_colors)] for i in range(num_vertices)]
    variables = []
    for i in range(num_vertices):
        inner_list = []
        for c in range(max_colors):
            inner_list.append(i * max_colors + c + 1)
        variables.append(inner_list)

    # At least one color per vertex
    for i in range(num_vertices):
        solver.add_clause(variables[i])

    # No two colors per vertex
    for i in range(num_vertices):
        for c1 in range(max_colors):
            for c2 in range(c1 + 1, max_colors):
                solver.add_clause([-variables[i][c1], -variables[i][c2]])

    # Adjacent vertices must have different colors
    for v1, v2 in graph.edges():
        for c in range(max_colors):
            solver.add_clause([-variables[v1][c], -variables[v2][c]])

    if solver.solve_limited():
        solution = solver.get_model()
        vertex_color_mapping = {}

        for i in range(num_vertices):
            for c in range(max_colors):
                if solution[variables[i][c] - 1] > 0:
                    vertex_color_mapping[i] = c
                    break

        return vertex_color_mapping
    else:
        return None

def write_and_print(output_file, message):
    print(message)
    output_file.write(message + "\n")


def process_graph_files(instances_folder, output_folder):

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Generate output filenames based on the current date and time, plus a random sequence
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    random_seq = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
    output_filename = os.path.join(output_folder, f"output_{current_time}_{random_seq}.txt")
    csv_filename = os.path.join(output_folder, f"results_{current_time}_{random_seq}.csv")

    # Initialize list to store data for CSV
    all_files_data = []

    # Process each file in the folder
    with open(output_filename, 'w') as output_file:
        for filename in os.listdir(instances_folder):
            file_path = os.path.join(instances_folder, filename)
            if os.path.isfile(file_path):
                # Initial print and write for filename
                write_and_print(output_file, f"Filename: {filename}")

                # Graph processing (placeholders for your actual implementations)
                num_vertices, edges = read_graph_from_file(file_path)
                num_edges = len(edges)
                graph = relabel_graph(create_graph(edges))

                graph_density = nx.density(graph)

                write_and_print(output_file, f"Vertices: {num_vertices}, Edges: {num_edges}\n")
                write_and_print(output_file, f"Density: {graph_density}")

                # DSATUR coloring
                dsatur_coloring, dsatur_time = color_graph_dsatur(graph)
                num_colors_used_dsatur = len(set(dsatur_coloring.values()))
                write_and_print(output_file,f"DSATUR completed, SAT Starting")

                # SAT coloring
                sat_coloring, sat_time, sat_time_matched_with_dsatur, best_iteration_time = sat_helper(graph, output_file, num_colors_used_dsatur)
                num_colors_used_sat = len(set(sat_coloring.values())) if sat_coloring is not None else "999"

                # Add the processed file's data to the list for CSV output
                all_files_data.append({
                    'filename': filename,
                    'num_edges': num_edges,
                    'num_vertices': num_vertices,
                    'graph_density': graph_density,
                    'num_colors_used_dsatur': num_colors_used_dsatur,
                    'dsatur_time': dsatur_time,
                    'num_colors_used_sat': num_colors_used_sat,
                    'sat_time_matched_with_dsatur': sat_time_matched_with_dsatur if sat_coloring is not None else "999",
                    'sat_time': sat_time if sat_coloring is not None else "999",
                    'sat_best_solution_iteration_time': best_iteration_time if sat_coloring is not None else "999"
                })

                write_and_print(output_file, "Number of colors used (DSATUR): " + str(num_colors_used_dsatur))
                write_and_print(output_file, "DSATUR Coloring Time: " + str(dsatur_time))
                if sat_coloring is not None:
                    write_and_print(output_file, "Number of colors used (SAT): " + str(num_colors_used_sat))
                    write_and_print(output_file, "SAT Coloring Time (Best solution): " + str(sat_time))
                    write_and_print(output_file,
                                    "SAT Coloring Time (Matched with DSATUR): " + str(sat_time_matched_with_dsatur))
                else:
                    write_and_print(output_file,
                                    "SAT solver could not find a solution with the given number of colors.")
                write_and_print(output_file, "\n")

    # Writing to CSV
    fieldnames = ['filename', 'num_edges', 'num_vertices', 'graph_density', 'num_colors_used_dsatur', 'dsatur_time',
                  'num_colors_used_sat', 'sat_time_matched_with_dsatur', 'sat_time', 'sat_best_solution_iteration_time']
    with open(csv_filename, mode='w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for data in all_files_data:
            writer.writerow(data)

    print(f"CSV data successfully written to {csv_filename}.")

#Usage
instances_folder = 'instances'
output_folder = 'output'

for i in range(5):
    print(f"Iteration {i+1} started")
    process_graph_files(instances_folder, output_folder)

