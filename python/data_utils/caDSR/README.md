# caDSR ETL

This are a pipeline of scripts to load the SITamer graph with caDSR entities. The input data are the XML dump of the caDSR found at [https://cadsr.nci.nih.gov/ftp/caDSR_Downloads/CDE/XML/](https://cadsr.nci.nih.gov/ftp/caDSR_Downloads/CDE/XML/). Download and unzip the file there into this directory.

The steps are as follows (assumes creating db from scratch):

```shell
# Create the intermediate [SQLite](https://sqlite.org) local database.
echo cadsr-dde.sql | sqlite3 vms.db
 
# Parse the XML and store the caDSR entities (CDE, DEC, OB, PR, VDM, PV) in 
# corresponding  SQLite tables (`vms.db`). This step also standardizes the names 
# of the entity attributes and creates 'linking tables' that connect the entities 
# as specified in the XML.
python parse-cde-xml-into-sqlite.py
 
* Create the nodes in Neo4j using the SQLite database.
python add-tables.py
 
* Add the relationships between nodes in Neo4j.
python add-relationships.py
 
* Compute and add the vector embeddings to relevant nodes.
python vectorize-cdes-sqlite.py
```




