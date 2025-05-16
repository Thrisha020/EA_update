# give child and parent node alone

import requests
import networkx as nx
from bokeh.plotting import figure, show, from_networkx
from bokeh.models import HoverTool, Circle, MultiLine, LabelSet, ColumnDataSource
from bokeh.models.graphs import StaticLayoutProvider
from bokeh.io import output_file
import time
# API Call to Fetch Data with Retry Logic
url = "http://10.190.226.42:1248/api/workspaces/BankingDemoWS/ObjectRelationships"
params = {"id": "MAP|23"}
headers = {"accept": "application/json"}
def fetch_data():
    retries = 3
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(3)  # Wait before retrying
    return None
data = fetch_data()
if data:
    parent_name = data.get("name", "Unknown Parent")
    # Print Parent Name
    print("\n Parent ID:", data.get("id", "Unknown ID"))
    print(" Parent Name:", parent_name)
    # Create Graph
    G = nx.DiGraph()
    G.add_node(parent_name, label="Parent")
    for relation in data.get("relations", []):
        group_relation = relation.get("groupRelation", "Unknown Relation")
        if group_relation in ["Screen Used By", "Direct Relationships"]:
            G.add_node(group_relation, label="Group")
            G.add_edge(parent_name, group_relation)
            print(f"\n:paperclip: Group Relation: {group_relation}")
            for child in relation.get("data", []):
                child_name = child.get("name", "Unknown")
                G.add_node(child_name, label="Child")
                G.add_edge(group_relation, child_name)
                # Print child file names in the terminal
                print(f"  - :page_facing_up: Child Name: {child_name}")
    # Create Bokeh Figure
    plot = figure(title="Dependency Graph", width=800, height=600)
    layout = nx.spring_layout(G, scale=2, seed=42)
    graph_renderer = from_networkx(G, layout)
    # Node Styling
    graph_renderer.node_renderer.glyph = Circle(radius=0.1, fill_color="lightblue")
    # Edge Styling
    graph_renderer.edge_renderer.glyph = MultiLine(line_color="black", line_width=1)
    # Add Labels
    node_labels = list(G.nodes)
    x_coords = [layout[node][0] for node in G.nodes]
    y_coords = [layout[node][1] for node in G.nodes]
    source = ColumnDataSource(data=dict(x=x_coords, y=y_coords, labels=node_labels))
    labels = LabelSet(x="x", y="y", text="labels", level="glyph",
                      x_offset=10, y_offset=10, source=source)
    plot.add_layout(labels)
    # Hover Tool to Show Names
    hover = HoverTool(tooltips=[("Name", "@index")])
    plot.add_tools(hover)
    # Set Custom Layout Provider
    graph_renderer.layout_provider = StaticLayoutProvider(graph_layout=layout)
    plot.renderers.append(graph_renderer)
    # Output and Show
    output_file("dependency_graph.html")
    show(plot)
else:
    print("Error: Could not fetch data after retries. Check API connection.")