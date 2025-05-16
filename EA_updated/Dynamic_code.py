import requests
import json
import networkx as nx
from bokeh.plotting import figure, show, from_networkx
from bokeh.models import HoverTool, Circle, MultiLine, LabelSet, ColumnDataSource
from bokeh.models.graphs import StaticLayoutProvider
from bokeh.io import output_file

# API Base URL
BASE_URL = "http://10.190.226.42:1248/api/workspaces/BankingDemoWS"

def get_bms_details(file_name):
    """Fetches the details of the given BMS file."""
    url = f"{BASE_URL}/SearchObjects?name={file_name}&types=%2A"
    headers = {"accept": "application/json"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data[0] if data else None  # Return the first match
    return None

def get_bms_dependencies(bms_id):
    """Fetches dependencies of the given BMS ID."""
    url = f"{BASE_URL}/ObjectRelationships?id={bms_id}"
    headers = {"accept": "application/json"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Return full dependency details
    return None

def get_programs_using_map(map_id):
    """Fetches the list of programs using the given map ID."""
    url = f"{BASE_URL}/ObjectRelationships?id={map_id}"
    headers = {"accept": "application/json"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Return full details
    return None

# User Input for BMS File Name
bms_file_name = input("Enter the BMS file name: ")

# Step 1: Get BMS File Details
bms_details = get_bms_details(bms_file_name)
if not bms_details:
    print("BMS file not found.")
    exit()

print("\nBMS File Details:")
print(json.dumps(bms_details, indent=2))

# Extract BMS ID
bms_id = bms_details["id"]
if not bms_id:
    print("BMS ID not found.")
    exit()

# Step 2: Get Dependencies
dependencies_data = get_bms_dependencies(bms_id)
if not dependencies_data:
    print("No dependencies found.")
    exit()

print("\nDependencies:")
print(json.dumps(dependencies_data, indent=2))

# Step 3: Construct Graph using NetworkX
G = nx.DiGraph()
parent_name = bms_details.get("name", "Unknown BMS File")
G.add_node(parent_name, label="BMS File")

# Step 4: Process Dependencies & Add Nodes
screen_used_by_node = "Screen Used By"  # Intermediate Node
G.add_node(screen_used_by_node, label="Group")
G.add_edge(parent_name, screen_used_by_node)  # Link BMS → Screen Used By

for relation in dependencies_data.get("relations", []):
    group_relation = relation.get("groupRelation", "Unknown Relation")
    
    if group_relation == "Direct Relationships":
        # Create an intermediate node for direct relationships
        G.add_node(group_relation, label="Group")
        G.add_edge(parent_name, group_relation)
    
    for child in relation.get("data", []):
        child_name = child.get("name", "Unknown")
        G.add_node(child_name, label="Child")

        # Link children under "Direct Relationships" or "Screen Used By"
        if group_relation == "Screen Used By":
            G.add_edge(screen_used_by_node, child_name)  # Connect to "Screen Used By"
        else:
            G.add_edge(group_relation, child_name)  # Connect to other groups

# Step 5: Generate Bokeh Visualization
plot = figure(title="BMS Dependency Graph", width=1000, height=700)

# Use spring layout for a more evenly spaced graph
layout = nx.spring_layout(G, scale=2, seed=42)

# Convert NetworkX graph to Bokeh
graph_renderer = from_networkx(G, layout)
graph_renderer.node_renderer.glyph = Circle(radius=0.1, fill_color="lightblue")
graph_renderer.edge_renderer.glyph = MultiLine(line_color="black", line_width=1.5)

# Add labels to nodes
node_labels = list(G.nodes)
x_coords = [layout[node][0] for node in G.nodes]
y_coords = [layout[node][1] for node in G.nodes]
source = ColumnDataSource(data=dict(x=x_coords, y=y_coords, labels=node_labels))
labels = LabelSet(x="x", y="y", text="labels", level="glyph",
                  x_offset=10, y_offset=10, source=source)
plot.add_layout(labels)

# Add hover tool
hover = HoverTool(tooltips=[("Node", "@index")])
plot.add_tools(hover)

# Set graph layout
graph_renderer.layout_provider = StaticLayoutProvider(graph_layout=layout)
plot.renderers.append(graph_renderer)

# Output and show
output_file("bms_dependency_graph.html")
show(plot)
