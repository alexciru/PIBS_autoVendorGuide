# PIBS_autoVendorGuide
A Python-based tool that connects to Jira Assets, retrieves asset data, and automatically generates a formatted Word document report, streamlining documentation and inventory management.



# How to interface with Atlassian Assets API
The Atlassian Assets API is used to retrieve asset data from Jira.
The database is a combination of Object Types and Object Attributes, which are defined in the Jira database.

## Object Types
Object Types are used to categorize assets, such as "PiB" or "Machine".
Each Object Type has a unique ID, which is used to retrieve its attributes.

## Object Attributes
Object Attributes are used to store additional information about assets, such as the serial number or the vendor name.
Each Object Attribute has a unique ID, which is used to retrieve its value.


## Relevant TypesIds
| Object Type | Object Type ID |
| --- | --- |
| PiB | 40 |
| Server | 70 |
| Vendor | 38 |
| Teltonika | 39 |


## Structure of the data
Each of the objects, ex: PIB, has this structure:
```json
{
  "workspaceId": "string",
  "globalId": "string", 
  "id": "string",
  "label": "string",
  "objectKey": "string",
  "objectType": { ... }, /
  "created": "datetime",
  "updated": "datetime",
  "attributes": [ ... ], // <--------------- Here is the multiple components 
  "extendedInfo": { ... },
  "_links": { ... },
  "name": "string"
}
```


The attributes is a **list** of objects each of them wtih the following structure:

```json
{
  "id": "string",
  "objectTypeAttribute": {
    "name": "string",           // Attribute name (e.g., "Status", "Model")
    "type": "number"            // Data type (0=Text, 1=Reference, 4=Date, etc.)
  },
  "objectAttributeValues": [    // The actual values
    {
      "displayValue": "string", // Human-readable value
      "searchValue": "string",  // Search/filter value
      "value": "string",        // Raw value
      "referencedType": 3,
      "referencedObject": {     // If this references another object
        "id": "string",         // ID of referenced object
        "name": "string",       // Name of referenced object
        "objectKey": "string"   // Key of referenced object
      }
    }
  ]
}

```
Example Object: PiB138
This server object contains:

Basic Info: PiB138, Service Tag C9KCT64
References:

Model → Dell PowerEdge T560 (ID: 1295)
Location → DKKA (ID: 1301)
Vendor → Unimec A/S (ID: 4749)
Teltonika → 6002020850 (ID: 3856)


Multiple References:

Virtual Machines → 4 VMs (IDs: 140, 4729, 4730, 4731)