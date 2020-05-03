import db
import physics as phys 
from networkx import line_graph as dual

def update_physics(conn):
    G = db.graph(conn, center = None)

    # NODES
    mass, energy = phys.mass(G), phys.energy(G)
    values = zip(G.nodes(),mass,energy)
    for node, mass, energy in values:
        _ = db.run_sql(conn,\
            "UPDATE nodes SET mass = ? WHERE name = ? LIMIT 1", mass, node).lastrowid
        _ = db.run_sql(conn,\
            "UPDATE nodes SET energy = ? WHERE name = ? LIMIT 1", energy, node).lastrowid

    # EDGES
    H = dual(G); del G
    mass, energy = phys.mass(H), phys.energy(H)
    values = [(u,v,m,p) for (u,v),m, p in zip(H.edges(),mass,energy)]
    for u, v,  mass, energy in values:
        _ = db.run_sql(conn,\
            "UPDATE nodes SET mass = ? WHERE left  = ? and right = ?", mass, u, v).lastrowid
        _ = db.run_sql(conn,\
            "UPDATE nodes SET mass = ? WHERE left  = ? and right = ?", mass, v, u).lastrowid
        _ = db.run_sql(conn,\
            "UPDATE nodes SET energy = ? WHERE left  = ? and right = ?", energy, u, v).lastrowid
        _ = db.run_sql(conn,\
            "UPDATE nodes SET energy = ? WHERE left  = ? and right = ?", energy, v, u).lastrowid


def read_node_prop(conn,subgraph,prop="energy"):
    nodes = list(subgraph.nodes())
    res = [db.run_sql(conn,\
        f"SELECT {prop} FROM nodes WHERE name = ?", n).fetchall()[0][0] for n in nodes]
    return array([get_node_energy(conn,n) for n in nodes])

def read_edge_prop(conn,subgraph,prop="energy"):
    edges = list(subgraph.edges())
    res = [db.run_sql(conn,\
        "SELECT energy FROM edges WHERE left = ? AND right = ?", u,v).fetchall()[0][0] for u,v in edges]
    return array([get_edge_energy(conn,u,v) for u,v in edges])