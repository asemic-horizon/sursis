import os, json
import networkx as nx 
import shutil
from time import ctime, sleep
from numpy import unique
import physical as phys

def read_data(file="data.json"):
    sleep(0.2)
    if os.path.exists(file):
        with open(file,"r") as f:
            d = json.load(f)
        if "nodes" not in d: d["nodes"]=list()
        if "edges" not in d: d["edges"]=list()
        #if "potential" not in d: d['potential'] = calculate_potential()
        if "state" not in d: d["state"]=dict()
    else:
        d = {"nodes":[], "edges":[],state:{}}
    return d

def write_data(d,file="data.json"):
    with open(file,"w") as f:
        json.dump(d,f)
    shutil.copyfile(file,ctime()+".json")
    sleep(0.2)
def str_pair(u,v):
    return f'{u.lower()};{v.lower()}'

def calculate_potential(file="data.json"):
    G = graph(center = None, file = file)
    potential = phys.graph_potential(G)
    w = (potential - potential.min())/(potential.max() - potential.min())

    d = read_data(file)
    d["potential"] = dict(zip(list(G.nodes()),list(w)))
    write_data(d,file)

def read_potential(file="data.json"):
    d = read_data(file)
    return np.array(list(d["potential"].values()))

def graph(center = None, radius = None, file="data.json"):
    d = read_data(file)
    d['last_query'] = center
    write_data(d,file)
    G = nx.Graph()
    for node in list_nodes(file):
        G.add_node(node)
    for u,v in list_edges(file):
        if u in G.nodes() and v in G.nodes():
            G.add_edge(u,v)
    if center and radius:
        G = nx.ego_graph(G,n=center, radius=radius)
    return G

def list_nodes(file="data.json"):
    d = read_data(file)
    return list(unique(d['nodes']))

def list_edges(file="data.json"):
    d = read_data(file)
    return [v.split(";") for v in set(d['edges'])]

def query_connections(node,file="data.json"):
    nodes = list_nodes(file)
    edges = list_edges(file)
    d = read_data(file)
    d["state"]["last_query"] = node
    write_data(d,file)
    connected = [(u,v) for u,v in edges if\
                    (u==node) or (v==node)]
    return connected

def del_node(node,file="data.json"):
    d = read_data(file)
    found = True
    while found:
        if node in d['nodes']:
            u = d['nodes']
            u.remove(node.lower())
            d['nodes'] = u
            # remove edges
            candidates = query_connections(node)
            for u,v in candidates: 
                del_edge(u,v)
            found = True
        else:
            found = False
    write_data(d,file)
    return found

def merge_nodes(node1,node2,new_name = None, file="data.json"):
    if new_name == None:
        new_name = f"{node1}/{node2}"
    write_node(new_name)
    new_edges = query_connections(node1)\
              + query_connections(node2)
    del_node(node1); del_node(node2)
    for u,v in new_edges:
        write_edge(u,v)

def del_edge(u,v,file="data.json"):
    d = read_data(file)
    found = False
    for edge in [str_pair(u,v),str_pair(v,u)]:
        if edge in d['edges']:
            edges_ = d['edges']
            edges_.remove(edge)
            d['edges'] = edges_
            found = found or True
        else:
            found = found or False
        write_data(d,file)
        return found

def write_edge(u,v,file="data.json"):
    d = read_data(file)
    if (v,u) and (u,v) not in list_edges():
        d['edges'].append(str_pair(u,v))
    write_data(d,file)

def write_node(node,file="data.json"):
    d = read_data(file)
    if node not in d['nodes']:
        d['nodes'].append(node.lower())
        calculate_potential(file)

    write_data(d,file)

def state(file="data.json"):
    d = read_data(file)
    if "state" in d and "last_add" in d["state"]:
        return d["state"]
    else:
        first_node = list_nodes()[0]
        d["state"]["last_add"] = first_node
        d["state"]["blast_add"] = first_node
        d["state"]["last_query"] = first_node
        write_data(d,file)
