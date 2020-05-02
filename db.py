import logging
logging.basicConfig(filename="app.log")

import os, json, sqlite3
from numpy import unique, array
from time import ctime
import networkx as nx 

import physical as phys




def nc(file="data.sqlite"):
    try:
        conn = sqlite3.connect(file)
        return conn
    except sqlite3.Error as e:
        logging.error(e)


def initialize(conn):
    sql_nodes_table =\
    """CREATE TABLE IF NOT EXISTS nodes (
            id integer PRIMARY KEY,
            name text NOT NULL,
            mass real,
            energy real);"""
    sql_edges_table =\
    """CREATE TABLE IF NOT EXISTS edges (
            id integer PRIMARY KEY,
            left integer NOT NULL,
            right integer NOT NULL);"""
    try:
        c = conn.cursor()
        c.execute(sql_nodes_table)
        c.execute(sql_edges_table)
    except sqlite3.Error as e:
        logging.error(e)

def run_sql(conn,sql,*args):
    cur = conn.cursor()
    cur.execute(sql,(*args,))
    return cur


def insert_node(conn,node):
    return run_sql(conn,"INSERT INTO nodes (name) VALUES (?)",node).lastrowid

def node_exists(conn, node):
    res = run_sql(conn,"SELECT id FROM nodes WHERE name = ? LIMIT 1",node).fetchall()
    return len(res)>0

def write_node(conn,node):
    if node_exists(conn,node):
        return True
    else:
        insert_node(conn,node)
        return False

def get_node_id(conn,node):
    try:
        return run_sql(conn,"SELECT id FROM nodes WHERE name = ? LIMIT 1",node).fetchall()[0][0]
    except:    
        logging.error("Error fetching id for node " + node)

def get_node_name(conn,id_1):
    try:
        return run_sql(conn,"SELECT id FROM nodes WHERE id = ? LIMIT 1",id_1).fetchall()[0][0]
    except:    
        logging.error("Error fetching id for node " + node)

def insert_edge(conn, node_1, node_2):
    try:
        id_1, id_2 = get_node_id(conn,node_1),get_node_id(conn,node_2)
        return run_sql(conn,"INSERT INTO edges (left,right) VALUES (?,?)",id_1,id_2).lastrowid
    except:
        logging.error(f"Couldn't create edge {node_1}-{node_2}")

def edge_exists(conn, node_1, node_2):
    id_1, id_2 = get_node_id(conn,node_1),get_node_id(conn,node_2)
    res1 = run_sql(conn,"SELECT id FROM edges WHERE left = ? and right = ? ", id_1, id_2).fetchall()
    res2 = run_sql(conn,"SELECT id FROM edges WHERE left = ? and right = ? ", id_2, id_1).fetchall()
    return len(res1)>0 and len(res2)>0


def write_edge(conn,node_1,node_2):
    if edge_exists(conn,node_1,node_2):
        return True
    else:
        insert_edge(conn,node_1,node_2)
        return False


def delete_edge(conn, node_1, node_2):
    try:
        id_1, id_2 = get_node_id(conn,node_1),get_node_id(conn,node_2)
        _ =  run_sql(conn,"DELETE FROM edges WHERE left = ? and right = ?",id_1,id_2)
        _ =  run_sql(conn,"DELETE FROM edges WHERE left = ? and right = ?",id_2,id_1)
    except:
        logging.error(f"Couldn't get nodes {node_1}-{node_2}")

def delete_node(conn, node):
    try:
        id_1 = get_node_id(conn,node)
        _ =  run_sql(conn,"DELETE FROM edges WHERE left = ? ",id_1)
        _ =  run_sql(conn,"DELETE FROM edges WHERE right = ?",id_1)
        _ =  run_sql(conn,"DELETE FROM nodes WHERE id = ?", id_1)
    except:
        logging.error(f"Couldn't {node}.")


def del_node(conn,node):
    if node_exists(conn,node):
        return True
    else:
        delete_node(conn,node)
        return False


def del_edge(conn,node_1,node_2):
    if edge_exists(conn,node_1,node_2):
        return True
    else:
        delete_edge(conn,node_1,node_2)
        return False


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
def update_mass(conn, node, mass):
    return run_sql(conn,"UPDATE nodes SET mass = ? WHERE name = ? LIMIT 1",mass, node)

def update_energy(conn, node, mass):
    return run_sql(conn,"UPDATE nodes SET energy = ? WHERE name = ? LIMIT 1",mass, node)

def list_nodes(conn):
    return [n[0] for n in run_sql(conn,"SELECT name FROM nodes").fetchall()]



def get_energy(conn,node):
    return run_sql(conn,"SELECT energy FROM nodes WHERE name = ?", node).fetchall()[0][0]

def list_edges(conn):
    query = """SELECT n1.name, n2.name FROM edges 
                LEFT JOIN nodes AS n1 ON n1.id = edges.left 
                LEFT JOIN nodes AS n2 ON n2.id = edges.right;"""
    return run_sql(conn,query).fetchall()


def graph(conn, center = None, radius = None):
    nodes = list_nodes(conn)
    edges = list_edges(conn)

    G = nx.Graph()
    for node in nodes:
        G.add_node(node)
    for u,v in edges:
        if u in G.nodes() and v in G.nodes():
            G.add_edge(u,v)
    if center and radius:
        G = nx.ego_graph(G,n=center, radius=radius)
    return G


def calculate_energy(conn):
    G = graph(conn, center = None)
    potential = phys.graph_potential(G)
    w = phys.rescale(potential)
    values = zip(G.nodes(),w)
    for node, energy in values:
        update_energy(conn,node,energy)

def read_energy(conn,subgraph):
    nodes = list(subgraph.nodes())
    return array([get_energy(conn,n) for n in nodes])

def query_connections(node,file="data.json"):
    edges = list_edges(file)
    connected = [(u,v) for u,v in edges if\
                    (u==node) or (v==node)]
    return connected

def merge_nodes(node1,node2,new_name = None, file="data.json"):
    if new_name == None:
        new_name = f"{node1}/{node2}"
    insert_node(new_name)
    new_edges = query_connections(node1)\
              + query_connections(node2)
    delete_node(node1); delete_node(node2)
    for u,v in new_edges:
        insert_edge(u,v)
