"""


    GRAPH FINAL

"""


import requests
import networkx as nx
from bokeh.plotting import figure, show, output_file
from bokeh.models import GraphRenderer, StaticLayoutProvider, Circle, LabelSet, ColumnDataSource
from bokeh.palettes import Spectral4
from bokeh.io import save

# ✅ API Base URL
BASE_URL = "http://10.190.226.42:1248/api/workspaces/BankingDemoWS"

def get_bms_details(file_name):
    """Fetch details of the given BMS file."""
    url = f"{BASE_URL}/SearchObjects?name={file_name}&types=%2A"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json():
        return response.json()[0]  # ✅ Return first match
    return None

def get_bms_dependencies(bms_id):
    """Fetch dependencies of the given BMS ID."""
    url = f"{BASE_URL}/ObjectRelationships?id={bms_id}"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # ✅ Return full dependency details
    return None

def get_programs_using_map(map_id):
    """Fetch programs using the given map ID."""
    url = f"{BASE_URL}/ObjectRelationships?id={map_id}"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # ✅ Return full details
    return None

# ✅ User Input: File Name
bms_file_name = input("Enter the file name: ").strip()

# ✅ Step 1: Get BMS File Details
bms_details = get_bms_details(bms_file_name)
if not bms_details:
    print("❌ BMS file not found.")
    exit()

# ✅ Extract Parent Info
parent_id = bms_details["id"]
parent_name = bms_details["name"]

# ✅ Step 2: Get Dependencies
dependencies_data = get_bms_dependencies(parent_id)
if not dependencies_data:
    print("❌ No dependencies found.")
    exit()

# ✅ Step 3: Extract Related Maps
map_data = {}  # Store MAPs with their IDs
for relation in dependencies_data.get("relations", []):
    if relation["groupRelation"] == "Direct Relationships":
        for item in relation["data"]:
            if item["type"] == "MAP":
                map_data[item["id"]] = item["name"]  # Store MAP ID → Name

# ✅ Step 4: Generate Multiple Graphs Dynamically
for map_id, map_name in map_data.items():
    program_data = get_programs_using_map(map_id)
    if not program_data:
        continue

    # ✅ Step 4.1: Build Graph Data (Handling Duplicates)
    graph_data = {"nodes": [map_name], "edges": []}
    node_counts = {}  # Track duplicates

    for relation in program_data.get("relations", []):
        group_name = relation["groupRelation"]
        if not relation["data"]:
            continue

        # Add Group Relation Node
        graph_data["nodes"].append(group_name)
        graph_data["edges"].append((map_name, group_name))

        for item in relation["data"]:
            file_name = item["name"]

            # ✅ Handle Duplicate Nodes
            if file_name in node_counts:
                node_counts[file_name] += 1
                file_name_unique = f"{file_name} ({node_counts[file_name]})"
            else:
                node_counts[file_name] = 1
                file_name_unique = file_name

            graph_data["nodes"].append(file_name_unique)
            graph_data["edges"].append((group_name, file_name_unique))

    # ✅ Step 4.2: Create Bokeh Graph with Better Layout
    G = nx.DiGraph()
    for node in graph_data["nodes"]:
        G.add_node(node)
    for edge in graph_data["edges"]:
        G.add_edge(edge[0], edge[1])

    # ✅ Improved Layout to Avoid Overlapping
    pos = nx.fruchterman_reingold_layout(G)  # Uses a force-directed algorithm

    plot = figure(title=f"Dependency Graph for {map_name}", x_range=(-1.5, 1.5), y_range=(-1.5, 1.5), tools="", toolbar_location=None)

    graph_renderer = GraphRenderer()
    graph_renderer.node_renderer.data_source.data = dict(index=list(G.nodes()))
    graph_renderer.node_renderer.glyph = Circle(radius=0.1, fill_color="steelblue", line_color="black")

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

    

    # ✅ Save Each Graph Separately
    output_file(f"dependency_graph_{map_name}.html")
    save(plot)

    print(f"✅ Graph saved: dependency_graph_{map_name}.html")
