import streamlit as st
import matplotlib.cm as cm
import networkx as nx 
import numpy as np 
import physical as phys

def draw_bw(G, pos_fun=nx.spring_layout):
	pos = pos_fun(G)
	font_size = 11 if G.number_of_nodes()<50 else 9
	alpha = 1 if G.number_of_nodes()<150 else 0.75
	nx.draw(G,pos=pos,with_labels=True, node_color='w',font_size=font_size,width=0.2,alpha=alpha)
	st.pyplot()

def draw_color(G, pos_fun=nx.spring_layout, cmap=cm.bone):
	pos = pos_fun(G)
	font_size = 11 if G.number_of_nodes()<50 else 9
	alpha = 1
	potential = phys.graph_potential(G)
	color = (potential - potential.min())/(potential.max() - potential.min())
	nx.draw(G,pos=pos,with_labels=True, node_color=color,font_size=font_size,width=0.2,alpha=alpha)
	st.pyplot()

