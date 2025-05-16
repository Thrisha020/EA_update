"""

FINAL UPDATED EA 

DATE : FEB 14


"""



import requests

# ✅ API Base URL
BASE_URL = "http://10.190.226.42:1248/api/workspaces/BankingDemoWS"

def get_bms_details(file_name):
    """Fetches details of the given BMS file."""
    url = f"{BASE_URL}/SearchObjects?name={file_name}&types=%2A"
    headers = {"accept": "application/json"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json():
        return response.json()[0]  # ✅ Return first match
    return None

def get_bms_dependencies(bms_id):
    """Fetches dependencies of the given BMS ID."""
    url = f"{BASE_URL}/ObjectRelationships?id={bms_id}"
    headers = {"accept": "application/json"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # ✅ Return full dependency details
    return None

def get_programs_using_map(map_id):
    """Fetches the list of programs using the given map ID."""
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
print(f"\n📌 Parent ID: {parent_id}\n📌 Parent Name: {parent_name}")

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

# ✅ Step 4: Fetch "Screen Used By" and "Direct Relationships"
for map_id, map_name in map_data.items():
    program_data = get_programs_using_map(map_id)
    if not program_data:
        continue

    print(f"\n🗂 **Responsible Node: {map_name}**")  # 🔥 Display MAP Name

    relations_found = False  # Track if we found any relations

    for relation in program_data.get("relations", []):
        group_name = relation["groupRelation"]
        if not relation["data"]:
            continue  # Skip empty relations

        relations_found = True
        print(f"\n📎 Group Relation: {group_name}")
        for item in relation["data"]:
            print(f"  - 📄 Child Name: {item['name']}")

    if not relations_found:
        print("\n❌ No additional relationships found.")
