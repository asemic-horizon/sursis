import logging
logging.basicConfig(filename="app.log")

import os, json, sqlite3
#
from numpy import unique, array
from time import ctime
import networkx as nx 
#
import backend.physics as phys


def is_numericstring(s : str) -> bool:
    return all([v in "0123456789." for v in s])

def surefloat(s):
    if isinstance(s,float) or isinstance(s,int):
        return s
    if isinstance(s,str) and is_numericstring(s):
        return float(s)
    else:
        return 0

def stringfloat(s):
    if isinstance(s,str) and is_numericstring(s):
        return float(s)
    else:
        return 0

def dt(s):
    if len(s)==0:
        return None
    elif len(s)==1:
        return stringfloat(s[0])
    else:
        return [stringfloat(u) for u in s]



def nc(file="data.sqlite"):
    try:
        conn = sqlite3.connect(file)
        return conn
    except sqlite3.Error as e:
        logging.error(e)

def run_sql(conn, sql, *args):
    cur = conn.cursor()
    cur.execute(sql,(*args,))
    return cur

def push(conn, sql, *args):
    return run_sql(conn,sql,*args).lastrowid

def grab(conn, sql, *args):
    cur = run_sql(conn,sql,*args)
    res = cur.fetchone()
    return dt(res)

def pull(conn, sql, *args):
    cur = run_sql(conn,sql,*args)
    res = cur.fetchall()
    return [dt(r) for r in res]


# insert and delete functions do db work
def insert_node(conn,node):
    push(conn,
        "INSERT INTO nodes (name) VALUES (?)",node)

def node_exists(conn, node):
    res = pull(conn,
        "SELECT id FROM nodes WHERE name = ? LIMIT 1",node)
    return len(res)>0

def count_nodes(conn):
    return grab(conn,
        "select (count (name)) from nodes;")


# edges are written in one direction, but are assumed to be undirected
# therefore must check both ways

def edge_exists(conn, node_1, node_2):
    query = "SELECT id FROM named_edges WHERE node_1 = ? and node_2 = ? "
    res1 = run_sql(conn,query, node_1, node_2).fetchall()
    res2 = run_sql(conn,query, node_2, node_1).fetchall()
    return len(res1)>0 and len(res2)>0

# This helper is necessary for inserts given as node names
def get_node_id(conn,node):
    try:
        return run_sql(conn,"SELECT id FROM nodes WHERE name = ? LIMIT 1",node).fetchall()[0][0]
    except:    
        logging.error("Error fetching id for node " + node)

# edges are written in one direction, but are assumed to be undirected
def insert_edge(conn, node_1, node_2):
    try:
        # ensure pattern for edges where n1 dominates alphabetically
        n1, n2 = min(node_1, node_2), max(node_1,node_2)
        id_1, id_2 = get_node_id(conn,n1),get_node_id(conn,n2)
        return run_sql(conn,"INSERT INTO edges (left,right) VALUES (?,?)",id_1,id_2).lastrowid
    except:
        logging.error(f"Couldn't create edge {node_1}-{node_2}")

# edges are written in one direction, but are assumed to be undirected
# therefore must check both ways

def delete_edge(conn, node_1, node_2):
    query = "DELETE FROM edges WHERE left = ? and right = ?"
    try:
        id_1, id_2 = get_node_id(conn,node_1),get_node_id(conn,node_2)
        run_sql(conn,query,id_1,id_2)
        run_sql(conn,query,id_2,id_1)
    except:
        logging.error(f"Couldn't get nodes {node_1}-{node_2}")

def delete_node(conn, node):
    try:
        id_1 = get_node_id(conn,node)
        # first delete connected edges.
        run_sql(conn,"DELETE FROM edges WHERE left = ? ",id_1)
        run_sql(conn,"DELETE FROM edges WHERE right = ?",id_1)
        run_sql(conn,"DELETE FROM nodes WHERE id = ?", id_1)
    except:
        logging.error(f"Couldn't {node}.")

# write and del functions are called by the app an return a boolean
def write_node(conn,node):
    node = node.lower()
    if node_exists(conn,node):
        return True
    else:
        insert_node(conn,node)
def write_edge(conn,node_1,node_2):
    if edge_exists(conn,node_1,node_2):
        return True
    else:
        insert_edge(conn,node_1,node_2)
        return False
def del_node(conn,node):
    if not node_exists(conn,node):
        return False
    else:
        delete_node(conn,node)
        return True
def del_edge(conn,node_1,node_2):
    if edge_exists(conn,node_1,node_2):
        return True
    else:
        delete_edge(conn,node_1,node_2)
        return False

# meant to be called directly from the app too.
def list_nodes(conn, where=None):
    query = "SELECT name FROM nodes"
    if where: query += " WHERE " + where
    return [n[0] for n in run_sql(conn,query).fetchall()]

# not currently used,  just for completeness
def list_edges(conn):
    query = """SELECT * FROM named_edges"""
    return run_sql(conn,query).fetchall()

def query_connections(conn,node):
    connected = run_sql(conn,"SELECT node_1, node_2 FROM named_edges WHERE node_1 = ?").fetchall()
    connected += run_sql(conn,"SELECT node_1, node_2 FROM named_edges WHERE node_2 = ?").fetchall()
    return connected

def merge_nodes(conn,node1,node2,new_name = None):
    if new_name == None:
        new_name = f"{node1}/{node2}"
    write_node(conn,new_name)
    new_edges = query_connections(conn,node1)\
              + query_connections(conn,node2)
    for u,v in new_edges:
        write_edge(conn,u,v)
    del_node(conn,node1); del_node(conn,node2)


## convertion from OOOLD json format. 
def convert_json(conn, json_file):
    with open(json_file,"r") as f: d = json.load(f)
    for node in d["nodes"]:
        insert_node(conn,node)
    for edge in d["edges"]:
        u, v = edge.split(";")
        try:
            insert_edge(conn,u,v)
        except:
            logging.error(f"Conversion error in edge {node_1}-{node_2}")




