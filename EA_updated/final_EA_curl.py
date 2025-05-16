import requests
import json
import pandas as pd
import matplotlib.pyplot as plt

BASE_URL = "http://10.190.226.42:1248/api/workspaces/BankingDemoWS"

def get_bms_details(file_name):
    url = f"{BASE_URL}/SearchObjects?name={file_name}&types=%2A"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data[0] if data else None
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

def save_table_as_image(df, output_filename="affected_data_table.png"):
    fig, ax = plt.subplots(figsize=(10, len(df) * 0.3 + 1))
    ax.axis("tight")
    ax.axis("off")
    table = ax.table(cellText=df.values,
                     colLabels=df.columns,
                     cellLoc="center",
                     loc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.auto_set_column_width([0, 1, 2, 3])
    plt.savefig(output_filename, bbox_inches="tight", dpi=300)
    print(f"\n Table saved as image: {output_filename}")

def display_affected_data_table(affected_data):
    table_data = []
    for item in affected_data:
        for field in item.get("affectedFields", []):
            table_data.append([
                field.get("dataName", "N/A"),
                str(field.get("length", "N/A")),
                field.get("file", "N/A").split("\\")[-1],
                field.get("program", "N/A")
            ])
    if table_data:
        df = pd.DataFrame(table_data, columns=["Data Name", "Length", "Defined In", "For Program"])
        print("\n**Formatted Affected Data Items Table:**\n")
        print(df.to_string(index=False))
        save_table_as_image(df)
    else:
        print("No valid affected data items to display.")

def get_variable_id(variable_name):
    url = f"{BASE_URL}/SourceObjects/Search"
    params = {
        "name": variable_name,
        "objectTypes": "COBOL,NATURAL,PLI,RPG,JCL",
        "sourceObjectTypes": "DECL,SECTION,PAR,VAR,DATASTORE",
        "limit": 10000
    }
    headers = {"accept": "application/json"}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        id_list = [item['id'] for item in data]
        for item in data:
            print(f"Variable: {item['name']}, ID: {item['id']}")
        return id_list
    return []

def get_affected_data_items(variable_id):
    url = f"{BASE_URL}/SourceObjects/ChangeAnalyzer/AffectedDataItems"
    params = {
        "Ids": variable_id.replace("| |", "%7C%7C"),
        "includeTrace": "false",
        "crossProgramAnalysis": "false",
        "defaultDepth": "10"
    }
    headers = {"accept": "application/json"}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data if data else []
    return []

if __name__ == "__main__":
    # BMS Analysis
    bms_file_name = input("Enter the BMS file name: ")
    bms_details = get_bms_details(bms_file_name)
    if not bms_details:
        print("BMS file not found.")
        exit()
    print("BMS File Details:")
    print(json.dumps(bms_details, indent=2))
    
    bms_id = bms_details.get("id")
    if not bms_id:
        print("BMS ID not found.")
        exit()
    
    dependencies_data = get_bms_dependencies(bms_id)
    if not dependencies_data:
        print("No dependencies found.")
        exit()
    print("\nDependencies:")
    print(json.dumps(dependencies_data, indent=2))
    
    map_ids = [item["id"] for relation in dependencies_data.get("relations", []) for item in relation["data"] if item["type"] == "MAP"]
    
    for map_id in map_ids:
        program_data = get_programs_using_map(map_id)
        if program_data:
            print("\nPrograms Using This Screen:")
            print(json.dumps(program_data, indent=2))
    
    # Variable Analysis
    variable_name = input("Enter variable name: ")
    variable_ids = get_variable_id(variable_name)
    if variable_ids:
        while True:
            selected_id = input("\nCopy and paste the ID you want to analyze from the list above: ")
            if selected_id in variable_ids:
                break
            print("Invalid ID. Please select a valid ID from the list.")
        affected_data = get_affected_data_items(selected_id)
        display_affected_data_table(affected_data)
