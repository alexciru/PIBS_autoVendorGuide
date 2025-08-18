########################################################
# Script: Atlassian Assets Data Extraction (Python)
# Purpose: Connect to Atlassian Assets API, retrieve object data,
#          and build a structured DataFrame for export.
# Author: Converted from R to Python
# Date: 2025-08-18
########################################################

import base64
import requests
import pandas as pd
import json
import os
from dotenv import load_dotenv

# --- 1. Authentication ----

load_dotenv(".env")

email = os.getenv("ATLANTSIA_EMAIL")
api_token = os.getenv("ATLANTSIA_API_TOKEN")
domain = os.getenv("ATLANTSIA_DOMAIN")



# Encode credentials in Base64
auth_string = f"{email}:{api_token}"
auth_base64 = base64.b64encode(auth_string.encode()).decode()

headers = {
    "Authorization": f"Basic {auth_base64}",
    "Content-Type": "application/json"
}

# -----------------------------
# 2. Retrieve Workspace ID
# -----------------------------
workspace_url = f"https://{domain}/rest/servicedeskapi/assets/workspace"
resp_workspace = requests.get(workspace_url, headers=headers)
resp_workspace.raise_for_status()

workspace_data = resp_workspace.json()
workspace_id = workspace_data["values"][0]["workspaceId"]
print(f"Workspace ID: {workspace_id}")

base_url = f"https://api.atlassian.com/jsm/assets/workspace/{workspace_id}"

# -----------------------------
# 3. Retrieve Object IDs
# -----------------------------
start = 0
page_size = 1000
body = {"qlQuery": "objectTypeId = 40"}

res_objects = requests.post(
    f"{base_url}/v1/object/aql?startAt={start}&maxResults={page_size}",
    headers=headers,
    data=json.dumps(body)
)
res_objects.raise_for_status()
data_objects = res_objects.json()
object_ids = [obj["id"] for obj in data_objects.get("values", [])]
print(f"Found {len(object_ids)} objects.")

# -----------------------------
# 4. Prepare Output DataFrame
# -----------------------------
column_names = [
    "object_id","Key", "Created", "Updated", "PiB", "Model", "Location", 
    "Area", "Machine", "Vendor", "Teltonika", "Virtual Machines", "Software", 
    "Licenses", "Status", "Service Tag", "Express Service Code", "MAC Address", 
    "Requestor Initials", "Project", "Standard Support Expiry", 
    "Extended Support Expiry", "Last SSH Login", "Last VM Login", 
    "Last WebUI Login", "Vendor Guide", "ThinManager Product Key",  
    "Serial Number"
]
result_df = pd.DataFrame(columns=column_names)

# -----------------------------
# 5. Process Each Object
# -----------------------------
for one_id in object_ids:
    print(f"🔄 Processing object_id: {one_id}")

    # 5.1 Get object details
    resp_obj = requests.get(f"{base_url}/v1/object/{one_id}", headers=headers)
    resp_obj.raise_for_status()
    obj_data = resp_obj.json()

    # 5.2 Get display attributes (attr_data is a list)
    resp_attr = requests.get(f"{base_url}/v1/object/{one_id}/attributes", headers=headers)
    resp_attr.raise_for_status()
    attr_data_list = resp_attr.json()

    obj_type_att_values = []
    attr_names = []

    for val in attr_data_list:  # iterate over list of dicts
        display_val = val.get("displayValue")
        if display_val is None:
            obj_type_att_values.append(None)
        elif isinstance(display_val, list):
            obj_type_att_values.append("|".join(map(str, display_val)))
        else:
            obj_type_att_values.append(display_val)

        att_name = val.get("objectTypeAttribute", {}).get("name")
        attr_names.append(att_name)

    # 5.3 Get all attributes for object type
    obj_types_att_resp = requests.get(f"{base_url}/v1/objecttype/40/attributes", headers=headers)
    obj_types_att_resp.raise_for_status()
    object_types_attributes = obj_types_att_resp.json()

    all_attributes = pd.DataFrame({
        "name": [att["name"] for att in object_types_attributes],
        "value": [None] * len(object_types_attributes)
    })

    # Map retrieved attribute values to names
    name_to_value = dict(zip(attr_names, obj_type_att_values))
    all_attributes["value"] = all_attributes["name"].map(lambda x: name_to_value.get(x, None))

    # Append to result DataFrame, ensuring column count matches
    row_values = [one_id] + all_attributes["value"].tolist()
    expected_cols = len(result_df.columns)
    if len(row_values) < expected_cols:
        row_values += [None] * (expected_cols - len(row_values))
    elif len(row_values) > expected_cols:
        row_values = row_values[:expected_cols]

    result_df.loc[len(result_df)] = row_values

# -----------------------------
# 6. Final Output
# -----------------------------
print("Data retrieval complete")
print(result_df.head())

# Optional: save to CSV
result_df.to_csv("PiB_project_cleanup_LMS.csv", index=False)
