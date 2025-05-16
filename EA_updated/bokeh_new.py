import requests
import networkx as nx
from bokeh.plotting import figure, show, from_networkx
from bokeh.models import HoverTool, Circle, MultiLine, LabelSet, ColumnDataSource
from bokeh.models.graphs import StaticLayoutProvider
from bokeh.io import output_file
# API Call to Fetch Data
url = "http://10.190.226.42:1248/api/workspaces/BankingDemoWS/ObjectRelationships"
params = {"id": "MAP|23"}
headers = {"accept": "application/json"}
response = requests.get(url, headers=headers, params=params)
if response.status_code == 200:
    data = response.json()
    # Extract Parent Node
    parent_name = data.get("name", "Unknown Parent")
    # Create Graph
    G = nx.DiGraph()
    # Add Parent Node (Main)
    G.add_node(parent_name, label="Parent")
    # Extract and Add Child Nodes
    for relation in data.get("relations", []):
        group_relation = relation.get("groupRelation", "Unknown Relation")
        if group_relation in ["Screen Used By", "Direct Relationships"]:
            # Add intermediate node for the group
            G.add_node(group_relation, label="Group")
            G.add_edge(parent_name, group_relation)  # Link parent → group
            for child in relation.get("data", []):
                child_name = child.get("name", "Unknown")
                # Add final child nodes under respective groups
                G.add_node(child_name, label="Child")
                G.add_edge(group_relation, child_name)  # Link group → child
    # Create Bokeh Figure
    plot = figure(title="Dependency Graph", width=800, height=600)
    # Generate Graph Layout
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
    # Add Labels to Plot
    plot.add_layout(labels)
    # Hover Tool to Show Names
    hover = HoverTool(tooltips=[("Name", "@index")])
    plot.add_tools(hover)
    # Set Custom Layout Provider
    graph_renderer.layout_provider = StaticLayoutProvider(graph_layout=layout)
    # Add Graph to Plot
    plot.renderers.append(graph_renderer)
    # Output and Show
    output_file("dependency_graph.html")
    show(plot)
else:
    print("Failed to fetch data:", response.status_code, response.text)


