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

