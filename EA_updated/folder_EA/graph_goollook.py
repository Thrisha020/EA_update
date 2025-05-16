
"""

GOOD FORMATED GRAPH 

UPDATED : 15TH FEB

AUTHOR : TRISHA 

full structured output , bokeh graph , html link


"""


import requests
import networkx as nx
import webbrowser
import os
import time
from bokeh.plotting import figure, output_file, save
from bokeh.models import GraphRenderer, StaticLayoutProvider, Circle, LabelSet, ColumnDataSource

BASE_URL = "http://10.190.226.42:1248/api/workspaces/BankingDemoWS"

def get_bms_details(file_name):
    url = f"{BASE_URL}/SearchObjects?name={file_name}&types=%2A"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json():
        return response.json()[0]
    return None

def get_bms_dependencies(bms_id):
    url = f"{BASE_URL}/ObjectRelationships?id={bms_id}"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def get_programs_using_map(map_id):
    url = f"{BASE_URL}/ObjectRelationships?id={map_id}"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

bms_file_name = input("Enter the file name: ").strip()
bms_details = get_bms_details(bms_file_name)
if not bms_details:
    print(" BMS file not found.")
    exit()

parent_id = bms_details["id"]
parent_name = bms_details["name"]
print("\n Parent ID:", parent_id)
print(" Parent Name:", parent_name, "\n")

dependencies_data = get_bms_dependencies(parent_id)
if not dependencies_data:
    print(" No dependencies found.")
    exit()

map_data = {}
for relation in dependencies_data.get("relations", []):
    if relation["groupRelation"] == "Direct Relationships":
        for item in relation["data"]:
            if item["type"] == "MAP":
                map_data[item["id"]] = item["name"]

generated_files = []
timestamp = time.strftime("%Y%m%d_%H%M%S")

for map_id, map_name in map_data.items():
    program_data = get_programs_using_map(map_id)
    if not program_data:
        continue

    print(f"\n **Responsible Node: {map_name}**\n")
    graph_data = {"nodes": [map_name], "edges": []}
    node_counts = {}

    for relation in program_data.get("relations", []):
        group_name = relation["groupRelation"]
        if not relation["data"]:
            continue

        print(f"📎 Group Relation: {group_name}")
        graph_data["nodes"].append(group_name)
        graph_data["edges"].append((map_name, group_name))

        for item in relation["data"]:
            file_name = item["name"]

            if file_name in node_counts:
                node_counts[file_name] += 1
                file_name_unique = f"{file_name} ({node_counts[file_name]})"
            else:
                node_counts[file_name] = 1
                file_name_unique = file_name

            graph_data["nodes"].append(file_name_unique)
            graph_data["edges"].append((group_name, file_name_unique))
            print(f"  -  Child Name: {file_name_unique}")
        print()

    G = nx.DiGraph()
    for node in graph_data["nodes"]:
        G.add_node(node)
    for edge in graph_data["edges"]:
        G.add_edge(edge[0], edge[1])

    pos = nx.spring_layout(G)

    plot = figure(title=f"Dependency Graph for {map_name}", tools="", toolbar_location=None, 
                  background_fill_color="lightgray", outline_line_color=None, border_fill_color="lightgray", 
                  x_axis_type=None, y_axis_type=None, x_axis_label=None, y_axis_label=None)
    
    graph_renderer = GraphRenderer()
    graph_renderer.node_renderer.data_source.data = dict(index=list(G.nodes()))
    graph_renderer.node_renderer.glyph = Circle(radius=0.1, fill_color="lightblue", line_color="black")

    edge_start = [edge[0] for edge in G.edges()]
    edge_end = [edge[1] for edge in G.edges()]
    graph_renderer.edge_renderer.data_source.data = dict(start=edge_start, end=edge_end)
    
    graph_renderer.layout_provider = StaticLayoutProvider(graph_layout=pos)
    
    node_labels = ColumnDataSource(data=dict(
        x=[pos[node][0] for node in G.nodes()],
        y=[pos[node][1] for node in G.nodes()],
        names=[node for node in G.nodes()]
    ))

    labels = LabelSet(x='x', y='y', text='names', source=node_labels, text_font_size="10px", text_align='center')
    
    plot.renderers.append(graph_renderer)
    plot.add_layout(labels)
    
    file_counter = 1
    file_name = f"dependency_graph_{map_name}_{timestamp}.html"
    
    while os.path.exists(file_name):
        file_name = f"dependency_graph_{map_name}_{timestamp}_{file_counter}.html"
        file_counter += 1

    output_file(file_name)
    save(plot)
    
    generated_files.append(file_name)

if generated_files:
    print("\n Generated Graph Files:")
    for file in generated_files:
        abs_path = os.path.abspath(file)
        file_url = f"file://{abs_path}"
        print(f"{file} → Open in browser: {file_url}")
        webbrowser.open(file_url)
else:
    print(" No graphs were generated.")



html_link_1 = "file:///Users/thrisham/Desktop/MBANK70.BANK70A.htm"
html_link_2 = "file:///Users/thrisham/Desktop/MBANK70.HELP70A.htm"

print("MBANK70.BANK70A.htm :",html_link_1,"\n","MBANK70.HELP70A.htm :",html_link_2)