import streamlit as st
import matplotlib.cm as cm
import matplotlib as mpl
import matplotlib.colors as colors
import networkx as nx
import numpy as np
import physics as phys
import graph_physics as chem

def draw_bw(G, pos_fun=nx.spring_layout):
	pos = pos_fun(G)
	font_size = 10 if G.number_of_nodes()<10 else 6
	alpha = 1 if G.number_of_nodes()<150 else 0.855
	nx.draw(G,pos=pos,with_labels=True, node_color='w',font_size=font_size,width=0.2,alpha=alpha)
	st.pyplot()

def draw_color(G, pot, pos_fun=nx.spring_layout, cmap="gnuplot"):
	pos = pos_fun(G)
	font_size = 10 if G.number_of_nodes()<10 else 6
	alpha = 0.9
	node_size = 45
	scheme = mpl.pyplot.get_cmap(cmap)
	cnorm = colors.Normalize(vmin=-1, vmax = 1)
	smap = cm.ScalarMappable(norm=cnorm, cmap=scheme)
	colorvals = smap.to_rgba(pot)
	nx.draw(G,pos=pos,with_labels=True, node_color = colorvals, node_size = node_size,font_size=font_size,width=0.2,alpha=alpha)
	cbar = mpl.pyplot.colorbar(smap,ticks=[-1,0,1],orientation='horizontal',label="Potential field")
	cbar.ax.set_xticklabels(["               Repulsive","Neutral", "Attractive                "])
	st.pyplot()


def draw(G, conn, is_color, prop, pos_fun=nx.spring_layout,cmap="gnuplot"):
        pot = chem.read_node_prop(conn,G,prop)
        if is_color:
            draw_color(G,pot = pot, pos_fun = pos_fun, cmap = cmap)
        else:
            draw_bw(G, pos_fun)
