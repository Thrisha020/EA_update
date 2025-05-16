import requests
import json

BASE_URL = "http://10.190.226.42:1248/api/workspaces/BankingDemoWS"

def get_bms_id(file_name):
    """Fetches the ID of the given BMS file."""
    url = f"{BASE_URL}/SearchObjects?name={file_name}&types=%2A"
    headers = {"accept": "application/json"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]  # Returns full BMS details
    return None

def get_bms_dependencies(bms_id):
    """Fetches dependencies of the given BMS ID."""
    url = f"{BASE_URL}/ObjectRelationships?id={bms_id}"
    headers = {"accept": "application/json"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Returns full dependency details
    return None

# Main execution
#bms_file_name = "MBANK70.bms"
bms_file_name = "MBANK70.bms"
# Step 1: Get BMS File Details
bms_details = get_bms_id(bms_file_name)
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

# Extract program using the BMS file
programs_using_bms = []
if "relations" in dependencies_data:
    for relation_group in dependencies_data["relations"]:
        for item in relation_group["data"]:
            programs_using_bms.append(item["name"])  # Extract dependency names

print("\nPrograms Using This BMS File:")
print(json.dumps(programs_using_bms, indent=2))
