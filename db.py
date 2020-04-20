import os, json
import networkx as nx 

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
def str_pair(u,v):
	return f'{u};{v}'

def graph(file="data.json"):
	G = nx.Graph()
	for node in query_nodes(file):
		G.add_node(node)
	for u,v in query_edges(file):
		G.add_edge(u,v)
	return G
	
def query_nodes(file="data.json"):
	d = read_data(file)
	return d['nodes']

def query_edges(file="data.json"):
	d = read_data(file)
	return [v.split(";") for v in d['edges']]

def write_node(node,file="data.json"):
	d = read_data(file)
	d['nodes'].append(node)
	write_data(d,file)

def write_edge(u,v,file="data.json"):
	d = read_data(file)
	d['edges'].append(str_pair(u,v))
	write_data(d,file)
