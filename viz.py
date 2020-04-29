import streamlit as st
import matplotlib as plt
import networkx as nx 
import numpy as np 

def draw_bw(G, pos_fun):
	pos = pos_fun(G)
	font_size = 11 if G.number_of_nodes()<50 else 9
	alpha = 1 if G.number_of_nodes()<150 else 0.75
	nx.draw(G,pos=pos,with_labels=True, node_color='w',font_size=font_size,width=0.2,alpha=alpha)
	st.pyplot()