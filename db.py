import os, json
import networkx as nx 
import shutil
from time import ctime

def read_data(file="data.json"):
    if os.path.exists(file):
        with open(file,"r") as f:
            d = json.load(f)
        if "nodes" not in d: d["nodes"]=list()
        if "edges" not in d: d["edges"]=list()
    else:
        d = {"nodes":[], "edges":[]}
    return d
def write_data(d,file="data.json"):
    with open(file,"w") as f:
        json.dump(d,f)
    shutil.copyfile(file,f"{ctime()}.json")
def str_pair(u,v):
    return f'{u.lower()};{v.lower()}'

def graph(file="data.json"):
    G = nx.Graph()
    for node in query_nodes(file):
        G.add_node(node)
    for u,v in query_edges(file):
        G.add_edge(u,v)
    return G

def query_nodes(file="data.json"):
    d = read_data(file)
    return list(set(d['nodes']))

def query_edges(file="data.json"):
    d = read_data(file)
    return [v.split(";") for v in set(d['edges'])]

def write_node(node,file="data.json"):
    d = read_data(file)
    d['nodes'].append(node.lower())
    d['nodes']=list(set(d['nodes']))
    write_data(d,file)

def del_node(node,file="data.json"):
    d = read_data(file)
    if node in d['nodes']:
        d['nodes'].remove(node.lower())
        #edges = query_edges(file)
        #d['edges'] = [str_pair(u,v) for u,v in edges if u==node.lower() or v==node.lower()]
        found = True
    else:
        found = False
    write_data(d,file)
    return found

def del_edge(u,v,file="data.json"):
    d = read_data(file)
    found = False
    for edge in [str_pair(u,v),str_pair(v,u)]:
        if edge in d['edges']:
            _ = d['edges'].remove(edge)
            found = found or True
        else:
            found = found or False
        write_data(d,file)
        return found

def write_edge(u,v,file="data.json"):
    d = read_data(file)
    if (v,u) and (u,v) not in query_edges():
        d['edges'].append(str_pair(u,v))
    d['edges'] = list(set(d['edges']))
    write_data(d,file)
