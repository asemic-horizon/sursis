import streamlit as st 
import networkx as nx 
import numpy as np
from time import ctime
from numpy.random import choice
import db

def separator():
	st.write("----")

def confirm():
	st.write(f"Operation confirmed at {ctime()}.")

def if_confirm(pred,err="(Not found)"):
	if pred:
		confirm()
	else:
		st.write(err)

def known_field_input(conn,tag="Node", default=None, offset = None):
	if default:
		index = nodes.index(default)
	elif offset:
		index = db.count_nodes(conn) - (offset + 1)
	else:
		index = db.count_nodes(conn) - 1
	nodes = db.list_nodes(conn)
	field_input = st.selectbox(tag,nodes,index=index)
	return field_input

def add_del(tag1="Add",tag2="Delete"):
	add = st.button(tag1)
	rem = st.button(tag2)
	return add, rem

def representative(fields):
	u, v = choice(range(len(fields)),2)
	return int(u), int(v)
	# middle = len(fields)//2 if len(fields)>4 else 1
	# middle_ = middle + 1 if middle>1 else 1
	# return middle, middle_


def similar(node,substring_length = 7, max_examples = 2):
	effective_length = min(len(node),substring_length)
	nodes = db.list_nodes()
	candidates = [n for n in nodes if n[:effective_length]==node[:effective_length] and n!=node]
	effective_num_candidates = min(len(candidates),max_examples)
	return list(set(np.random.choice(candidates,effective_num_candidates)))

def graph_stats(G):
	messages = [
	f"{nx.number_of_nodes(G)} nodes, {nx.number_of_edges(G)} edges, {100*nx.density(G):2.2f}% density",
	f"{100*nx.average_clustering(G):2.2f}% of triangles, {100*nx.algorithms.cluster.transitivity(G):2.2f}% of triads",
	f"{nx.number_connected_components(G)} components",
	]
	for msg in messages:
		st.write(f"* {msg}")

