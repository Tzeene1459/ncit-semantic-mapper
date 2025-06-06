import sys
import os
import sqlite3
from dotenv import load_dotenv
from neo4j import GraphDatabase, Auth
from tqdm import tqdm


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


load_dotenv()
chunk_size = 250
dbfile = "../cdexml/vms.db"
conn = sqlite3.connect(dbfile)
conn.row_factory = dict_factory
cur = conn.cursor()

drv = GraphDatabase.driver(os.environ['NEO4J_URI'],
                           auth=Auth('basic',os.environ['NEO4J_USERNAME'],
                                     os.environ['NEO4J_PASSWORD']))
allowed_tbls = ('oc', 'pr', 'vdm', 'cde', 'dec')

tbls = sys.argv[1:]

for tbl in tbls:
    print(tbl)
    if tbl not in allowed_tbls:
        print(f"unknown table '{tbl}'; skipped")
        continue
    cur.execute(f"select code,type,version,term,shortName,context from {tbl}")
    rows = cur.fetchall()
    chunks = [rows[slice(y, y+chunk_size)] for y in range(0, len(rows), chunk_size)]
    for chunk in tqdm(chunks):
        drv.execute_query(f"""
        unwind $chunk as dta
        create (n:{tbl.upper()}:Term) set n = dta
        """, chunk=chunk)
        pass
    
