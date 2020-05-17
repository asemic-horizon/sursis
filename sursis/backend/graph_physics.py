import logging
logging.basicConfig(filename="physics.log",level = logging.INFO)

from backend import db
from backend import physics as phys 
#
from networkx import line_graph as dual
import networkx as nx
import numpy as np
from scipy.stats import norm
from numpy import array

def get_physics(conn, index, table):
    query = f"SELECT {index}, energy, mass, degree FROM {table}"
    return np.array(db.run_sql(conn,query).fetchall())


def graph(conn, center = None, radius = None, prop = "energy"):
    nodes = get_physics(conn, index = "name", table =  "nodes")
    edges = get_physics(conn, index = "node_1, node_2", table = "named_edges")
    G = nx.Graph()
    for node, energy, mass, degree in nodes:
        G.add_node(node, 
                weight=db.surefloat(energy), 
                energy=db.surefloat(energy), 
                mass = db.surefloat(mass), 
                degree=int(db.surefloat(degree)))
    for u,v, energy, mass, degree in edges:
        if u in G.nodes() and v in G.nodes():
            if energy and mass:
                w = norm.cdf(0.1 - db.surefloat(energy)*db.surefloat(mass))
            else:
                w = 0.5
            G.add_edge(u,v,weight=w if w>0 else 0, 
                energy = db.surefloat(energy), 
                mass = db.surefloat(mass),
                degree = int(db.surefloat(degree)))
    if center and radius:
        G = nx.ego_graph(G,n=center, radius=radius)
    return G



def update_physics(conn, fast = True):
    G = graph(conn, center = None)
    logging.info("Calculate node physics")
    boundary = db.run_sql(conn,
        "SELECT AVG(energy) FROM nodes WHERE degree=1").fetchone()[0]
    # NODES
    mass, energy = phys.physics(graph=G, fast=fast)
    for node, mass, energy in zip(G.nodes(), mass, energy):
        db.push(conn,\
            """UPDATE nodes SET mass = ?, energy = ?, degree = ? 
               WHERE name = ? """,
               mass, energy, G.degree[node],node)

    # EDGES
    logging.info("Calculate edge physics")
    boundary = db.run_sql(conn,
        "SELECT AVG(energy) FROM edges WHERE degree=1").fetchone()[0]

    H = dual(G); del G
    mass, energy = phys.physics(graph=H,boundary_value=0.5,fast=fast)
    values = [(u,v,m,p) for (u,v),m, p in zip(H.nodes(),mass,energy)]

    for u, v,  mass, energy in values: 
        n1 = min(u,v); n2 = max(u,v)
        id_1, id_2 = db.get_node_id(conn,n1), db.get_node_id(conn,n2)
        db.push(conn,\
            """UPDATE edges SET mass = ?, energy = ?, degree = ? 
                WHERE (left  = ? and right = ?)
                   OR (right = ? and left  = ?) """, 
                   mass, energy, H.degree[(u,v)], id_1, id_2, id_1, id_2)


def read_node_prop(conn,subgraph,prop="energy"):
    nodes = list(subgraph.nodes())
    res = [db.run_sql(conn,\
        f"SELECT {prop} FROM nodes WHERE name = ?", n).fetchall()[0][0] for n in nodes]
    return array([db.surefloat(r) for r in res])

def read_edge_prop(conn,subgraph,prop="energy"):
    edges = list(subgraph.edges())
    res = [db.run_sql(conn,\
        "SELECT energy FROM edges WHERE left = ? AND right = ?", u,v).fetchall()[0][0] for u,v in edges]
    return array([get_edge_energy(conn,u,v) for u,v in edges])

def prop_bounds(conn,prop="energy",table="nodes",slices=4):
    count = db.run_sql(conn,f"SELECT (COUNT(*)) FROM {table}").fetchone()[0]
    
    min_val = db.run_sql(conn,f"select MIN({prop}) FROM {table}").fetchone()[0]

    avg_val = db.run_sql(conn,f"select AVG({prop}) FROM {table}").fetchone()[0]
    med_val = db.run_sql(conn,\
        f"""SELECT {prop} FROM {table} ORDER BY {prop} LIMIT 1
            OFFSET
                {count//2}

        """).fetchone()[0]
    max_val = db.run_sql(conn,f"select MAX({prop}) FROM {table}").fetchone()[0]


    return min_val, max_val, avg_val, med_val


def total_energy(conn, table = "nodes",where=""):
    return db.run_sql(conn,\
        f"SELECT SUM((mass * energy)) from {table} {where}").fetchone()[0]

def subgraph_energy(conn,subgraph):
    m = read_node_prop(conn,subgraph,"mass")
    e = read_node_prop(conn,subgraph,"energy")
    return np.sum(m*e)

def gravity_partition(G, conn):
    expanding = db.list_nodes(conn, "(mass * energy) >0")
    collapsing = db.list_nodes(conn, "(mass * energy) < 0")
    return G.subgraph(expanding), G.subgraph(collapsing)    
#end
