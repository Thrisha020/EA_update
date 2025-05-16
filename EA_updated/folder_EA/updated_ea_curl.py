"""

FINAL WORKING CODE

4 curl command , correct structure o/p , bokeh graph , html link to open in browser and table format


updated : 14th feb

"""

import requests
import networkx as nx
import webbrowser
import os
import time
from bokeh.plotting import figure, output_file, save
from bokeh.models import GraphRenderer, StaticLayoutProvider, Circle, LabelSet, ColumnDataSource
import json
import pandas as pd
import requests
import matplotlib.pyplot as plt


# API Base URL
BASE_URL = "http://10.190.226.42:1248/api/workspaces/BankingDemoWS"

def get_bms_details(file_name):
    """Fetch details of the given BMS file."""
    url = f"{BASE_URL}/SearchObjects?name={file_name}&types=%2A"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json():
        return response.json()[0]
    return None

def get_bms_dependencies(bms_id):
    """Fetch dependencies of the given BMS ID."""
    url = f"{BASE_URL}/ObjectRelationships?id={bms_id}"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def get_programs_using_map(map_id):
    """Fetch programs using the given map ID."""
    url = f"{BASE_URL}/ObjectRelationships?id={map_id}"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

# User Input: File Name
bms_file_name = input("Enter the file name: ").strip()

# Step 1: Get BMS File Details
bms_details = get_bms_details(bms_file_name)
if not bms_details:
    print("BMS file not found.")
    exit()

# Extract Parent Info
parent_id = bms_details["id"]
parent_name = bms_details["name"]

print("\nParent ID:", parent_id)
print("Parent Name:", parent_name, "\n")

# Step 2: Get Dependencies
dependencies_data = get_bms_dependencies(parent_id)
if not dependencies_data:
    print("No dependencies found.")
    exit()

# Step 3: Extract Related Maps
map_data = {}
for relation in dependencies_data.get("relations", []):
    if relation["groupRelation"] == "Direct Relationships":
        for item in relation["data"]:
            if item["type"] == "MAP":
                map_data[item["id"]] = item["name"]

# Step 4: Print and Generate Multiple Graphs Dynamically
generated_files = []  # Store generated file names for printing
timestamp = time.strftime("%Y%m%d_%H%M%S")  # Generate timestamp to avoid overwriting

for map_id, map_name in map_data.items():
    program_data = get_programs_using_map(map_id)
    if not program_data:
        continue

    # Print Responsible Node
    print(f"\n**Responsible Node: {map_name}**\n")

    graph_data = {"nodes": [map_name], "edges": []}
    node_counts = {}

    for relation in program_data.get("relations", []):
        group_name = relation["groupRelation"]
        if not relation["data"]:
            continue

        # Print Group Relation
        print(f"Group Relation: {group_name}")

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

            # Print Child Nodes
            print(f"  - Child Name: {file_name_unique}")
        print()  # Add spacing for readability

    # Generate Graph
    G = nx.DiGraph()
    for node in graph_data["nodes"]:
        G.add_node(node)
    for edge in graph_data["edges"]:
        G.add_edge(edge[0], edge[1])

    # Improved Layout to Avoid Overlapping
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

    # Ensure Unique File Name (Avoid Overwriting)
    file_counter = 1
    file_name = f"dependency_graph_{map_name}_{timestamp}.html"

    while os.path.exists(file_name):  # If file exists, append a counter
        file_name = f"dependency_graph_{map_name}_{timestamp}_{file_counter}.html"
        file_counter += 1

    output_file(file_name)
    save(plot)
    
    generated_files.append(file_name)

# Print Output & Open in Browser
if generated_files:
    print("\nGenerated Graph Files:")
    for file in generated_files:
        abs_path = os.path.abspath(file)  # Get absolute path
        file_url = f"file://{abs_path}"
        print(f"{file} → Open in browser: {file_url}")
        webbrowser.open(file_url)  # Open automatically
else:
    print("No graphs were generated.")


html_link_1 = "file:///Users/thrisham/Desktop/MBANK70.BANK70A.htm"
html_link_2 = "file:///Users/thrisham/Desktop/MBANK70.HELP70A.htm"

print("MBANK70.BANK70A.htm :",html_link_1,"\n","MBANK70.HELP70A.htm :",html_link_2)



def save_table_as_image(df, output_filename="affected_data_table.png"):
    """Saves the affected data items table as an image using Matplotlib."""
    fig, ax = plt.subplots(figsize=(10, len(df) * 0.3 + 1))  # Auto-scale based on rows
    ax.axis("tight")
    ax.axis("off")

    # Create a table inside the figure
    table = ax.table(cellText=df.values,
                     colLabels=df.columns,
                     cellLoc="center",
                     loc="center")

    table.auto_set_font_size(False)
    table.set_fontsize(9)  # Adjust font size for readability
    table.auto_set_column_width([0, 1, 2, 3])  # Adjust width

    plt.savefig(output_filename, bbox_inches="tight", dpi=300)  # Save as PNG with high resolution
    print(f"\nTable saved as image: {output_filename}")

def display_affected_data_table(affected_data):
    """Extracts and displays a formatted table of affected data items, and saves it as an image."""
    table_data = []
    
    for item in affected_data:
        for field in item.get("affectedFields", []):
            table_data.append([
                field.get("dataName", "N/A"),
                str(field.get("length", "N/A")),
                field.get("file", "N/A").split("\\")[-1],  # Extract filename only
                field.get("program", "N/A")
            ])

    if table_data:
        df = pd.DataFrame(table_data, columns=["Data Name", "Length", "Defined In", "For Program"])
        print("\n **Formatted Affected Data Items Table:**\n")
        print(df.to_string(index=False))  # Pretty-print the table
        save_table_as_image(df)  # ✅ Save table as an image
    else:
        print("No valid affected data items to display.")

def get_variable_id(variable_name):
    url = "http://10.190.226.42:1248/api/workspaces/BankingDemoWS/SourceObjects/Search"
    params = {
        "name": variable_name,
        "objectTypes": "COBOL,NATURAL,PLI,RPG,JCL",
        "sourceObjectTypes": "DECL,SECTION,PAR,VAR,DATASTORE",
        "limit": 10000
    }
    headers = {"accept": "application/json"}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data:
            id_list = []
            print("\nAvailable IDs:")
            for item in data:
                print(f"Variable: {item['name']}, ID: {item['id']}")
                id_list.append(item['id'])
            return id_list  # Return list of IDs found
        else:
            print("No data found for the given variable.")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

def get_affected_data_items(variable_id):
    url = "http://10.190.226.42:1248/api/workspaces/BankingDemoWS/SourceObjects/ChangeAnalyzer/AffectedDataItems"
    encoded_id = variable_id.replace("| |", "%7C%7C")
    params = {
        "Ids": encoded_id,
        "includeTrace": "false",
        "crossProgramAnalysis": "false",
        "defaultDepth": "10"
    }
    headers = {"accept": "application/json"}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data:
            formatted_output = []
            for item in data:
                change_candidate = {
                    "changeCandidate": item.get("changeCandidate", ""),
                    "program": item.get("program", ""),
                    "file": item.get("file", ""),
                    "line": item.get("line", 0),
                    "column": item.get("column", 0),
                    "affectedFields": []
                }
                
                for field in item.get("affectedFields", []):
                    affected_field = {
                        "id": field.get("id", ""),
                        "dataName": field.get("dataName", ""),
                        "length": field.get("length", ""),
                        "value": field.get("value", ""),
                        "picture": field.get("picture", ""),
                        "normalizedPicture": field.get("normalizedPicture", ""),
                        "comment": field.get("comment", ""),
                        "program": field.get("program", ""),
                        "file": field.get("file", ""),
                        "usage": field.get("usage", ""),
                        "normalizedUsage": field.get("normalizedUsage", ""),
                        "line": field.get("line", 0),
                        "column": field.get("column", 0),
                        "changeCandidate": field.get("changeCandidate", False),
                        "traceItems": field.get("traceItems", [])
                    }
                    change_candidate["affectedFields"].append(affected_field)

                formatted_output.append(change_candidate)

            print(json.dumps(formatted_output, indent=4))
            return formatted_output
        else:
            print("No affected data items found.")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching affected data items: {e}")
        return []

# Example usage
variable_name = input("Enter variable name: ")
variable_ids = get_variable_id(variable_name)

if variable_ids:
    while True:
        selected_id = input("\nCopy and paste the ID you want to analyze from the list above: ")
        if selected_id in variable_ids:
            break
        print("Invalid ID. Please select a valid ID from the list.")
    
    affected_data = get_affected_data_items(selected_id)
    display_affected_data_table(affected_data)  # Call function to display & save table



"""

file name : MBANK70.bms


variable name : BANK-SCR70-RATE


 ID : 53||STU


"""