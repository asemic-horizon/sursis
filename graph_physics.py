import db
import physics as phys 
from networkx import line_graph as dual
from numpy import array
import logging

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


def update_physics(conn):
    G = graph(conn, center = None)

    # NODES
    mass, energy = phys.mass(G), phys.energy(G)
    values = zip(G.nodes(),mass,energy)
    for node, mass, energy in values:
        db.run_sql(conn,\
            "UPDATE nodes SET mass = ? WHERE name = ? LIMIT 1", mass, node).lastrowid
        db.run_sql(conn,\
            "UPDATE nodes SET energy = ? WHERE name = ? LIMIT 1", energy, node).lastrowid

    # EDGES
    H = dual(G); del G
    mass, energy = phys.mass(H), phys.energy(H)
    values = [(u,v,m,p) for (u,v),m, p in zip(H.nodes(),mass,energy)]

    for u, v,  mass, energy in values:
        id_1, id_2 = db.get_node_id(conn,u), db.get_node_id(conn,v)
        db.run_sql(conn,\
            "UPDATE edges SET mass = ? WHERE left  = ? and right = ?", mass, id_1, id_2).lastrowid
        db.run_sql(conn,\
            "UPDATE edges SET mass = ? WHERE left  = ? and right = ?", mass, id_2, id_1).lastrowid
        db.run_sql(conn,\
            "UPDATE edges SET energy = ? WHERE left  = ? and right = ?", energy, id_1, id_2).lastrowid
        db.run_sql(conn,\
            "UPDATE edges SET energy = ? WHERE left  = ? and right = ?", energy, id_2, id_1).lastrowid


def read_node_prop(conn,subgraph,prop="energy"):
    nodes = list(subgraph.nodes())
    res = [db.run_sql(conn,\
        f"SELECT {prop} FROM nodes WHERE name = ?", n).fetchall()[0][0] for n in nodes]
    return res

def read_edge_prop(conn,subgraph,prop="energy"):
    edges = list(subgraph.edges())
    res = [db.run_sql(conn,\
        "SELECT energy FROM edges WHERE left = ? AND right = ?", u,v).fetchall()[0][0] for u,v in edges]
    return array([get_edge_energy(conn,u,v) for u,v in edges])
