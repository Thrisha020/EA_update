import requests
import json

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

# Main executionMBANK70.bms
#bms_file_name = ""
bms_file_name = input("Enter the file name: ")


# Step 1: Get BMS File Details
bms_details = get_bms_details(bms_file_name)
if not bms_details:
    print("BMS file not found.")
    exit()

# Print BMS File Details
print("BMS File Details:")
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

# Print Dependency Details
print("\nDependencies:")
print(json.dumps(dependencies_data, indent=2))

# Extract MAP IDs (Screens defined in the BMS file)
map_ids = []
if "relations" in dependencies_data:
    for relation_group in dependencies_data["relations"]:
        for item in relation_group["data"]:
            if item["type"] == "MAP":  # Extract only MAPs
                map_ids.append(item["id"])

# Step 3: Get Programs Using Each MAP
for map_id in map_ids:
    program_data = get_programs_using_map(map_id)
    if program_data:
        print("\nPrograms Using This Screen:")
        print(json.dumps(program_data, indent=2))


#  MBANK70.bms