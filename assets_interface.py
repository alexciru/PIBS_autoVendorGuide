import base64
import requests
import json
import os
from dotenv import load_dotenv

class AtlassianAssetsAPI:
    def __init__(self, email: str, api_token: str, domain: str):
        """Initialize API client with authentication."""
        self.email = email
        self.api_token = api_token
        self.domain = domain
        self.headers = {
            "Authorization": f"Basic {base64.b64encode(f'{email}:{api_token}'.encode()).decode()}",
            "Content-Type": "application/json"
        }
        self.base_url = None

    # -----------------------------
    # Workspace
    # -----------------------------
    def get_workspace_id(self):
        """Retrieve the first workspace ID."""
        url = f"https://{self.domain}/rest/servicedeskapi/assets/workspace"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        workspace_data = resp.json()
        workspace_id = workspace_data["values"][0]["workspaceId"]
        self.base_url = f"https://api.atlassian.com/jsm/assets/workspace/{workspace_id}"
        return workspace_id

    # -----------------------------
    # Object Queries
    # -----------------------------
    def get_object_ids(self, aql_query: str, start: int = 0, max_results: int = 1000):
        """Retrieve object IDs matching an AQL query."""
        if not self.base_url:
            raise ValueError("Workspace not initialized. Call get_workspace_id() first.")
        body = {"qlQuery": aql_query}
        url = f"{self.base_url}/v1/object/aql?startAt={start}&maxResults={max_results}"
        resp = requests.post(url, headers=self.headers, data=json.dumps(body))
        resp.raise_for_status()
        data = resp.json()
        return [obj["id"] for obj in data.get("values", [])]

    # -----------------------------
    # Object Details
    # -----------------------------
    def get_object(self, object_id: str):
        """Retrieve full object details."""
        url = f"{self.base_url}/v1/object/{object_id}"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        
        return resp.json()

    # -----------------------------
    # Object Attributes
    # -----------------------------
    def get_object_attributes(self, object_id: str):
        """Retrieve the attributes of a specific object."""
        url = f"{self.base_url}/v1/object/{object_id}/attributes"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        data_list = resp.json()

        attributes = []
        for val in data_list:
            name = val.get("objectTypeAttribute", {}).get("name")

            # objectAttributeValues is a list, take the first element if present
            values = val.get("objectAttributeValues", [])
            display_val = values[0].get("displayValue") if values else None

            # If multiple values exist, join them with |
            if len(values) > 1:
                display_val = "|".join(v.get("displayValue", "") for v in values)

            attributes.append({
                "name": name,
                "display_value": display_val
            })

        # Create a dictionary for easy access
        attributes = {attr["name"]: attr["display_value"] for attr in attributes}

        return attributes

    # -----------------------------
    # Object Type Attributes
    # -----------------------------
    def get_object_type_attributes(self, object_type_id: int):
        """Retrieve all attributes defined for an object type."""
        url = f"{self.base_url}/v1/objecttype/{object_type_id}/attributes"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()
    


if __name__ == "__main__":

    load_dotenv(".env")  # Load environment variables from .env file

    # Example usage
    email = os.getenv("ATLANTSIA_EMAIL")
    api_token = os.getenv("ATLANTSIA_API_TOKEN")
    domain = os.getenv("ATLANTSIA_DOMAIN")
    pib_number = "135"  # Example PiB number to search for

    api = AtlassianAssetsAPI(email, api_token, domain)
    # Get workspace ID
    workspace_id = api.get_workspace_id()
    print(f"Workspace ID: {workspace_id}")
    # Get all object IDs of type 40 (PiB)
    object_ids = api.get_object_ids("objectTypeId = 40")
    print(f"Found {len(object_ids)} objects of type 40.")
    # get the pib number from the object id
    print("Object ID:", object_ids[0])
    for id in object_ids:
        attributes = api.get_object_attributes(id)
        if(attributes["PiB"].endswith(pib_number)):
            object_id = id
            break
        
    # Retrieve a specific object
    obj_data = api.get_object(object_id)
    print(f"Object ID: {obj_data['id']}, Name: {obj_data['name']}")
    # Retrieve its attributes
    attributes = api.get_object_attributes(object_id)
    print(f"Attributes for object {object_id}: {attributes}")
    # Retrieve all attributes of object type 40
    all_attrs = api.get_object_type_attributes(40)
    print(f"Attributes for object type 40: {all_attrs}")