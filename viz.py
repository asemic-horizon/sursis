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

def draw_color(G, pot, window, labels, pos_fun=nx.spring_layout, cmap="gnuplot"):
        pos = pos_fun(G)
        font_size = 11 if G.number_of_nodes()<10 else 9
        alpha = 0.8
        node_size = 50
        scheme = mpl.pyplot.get_cmap(cmap)
        

        cnorm = colors.Normalize(vmin=window[0], vmax = window[2])
        smap = cm.ScalarMappable(norm=cnorm, cmap=scheme)
        colorvals = smap.to_rgba(pot)
        nx.draw(G,pos=pos,with_labels=labels, node_color = colorvals, node_size = node_size,font_size=font_size,width=0.2,alpha=alpha)
        cbar = mpl.pyplot.colorbar(smap,ticks=window,orientation='horizontal',label="Potential field")
        cbar.ax.set_xticklabels(["               Repulsive","Neutral", "Attractive                "])
        st.pyplot()


def draw(G, conn, labels = True, cmap = "terrain_r", pos_fun=nx.kamada_kawai_layout):
        energy = np.array(chem.read_node_prop(conn,G,"energy"))
        minv, maxv, avgv, medv = chem.prop_bounds(conn)
        window = [minv if -minv > maxv else -maxv, medv, maxv if -maxv > minv else -minv]
        draw_color(G,pot = energy, window = window, labels = labels, pos_fun = pos_fun, cmap = cmap)
