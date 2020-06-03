import logging
logging.basicConfig(filename="physics.log",level = logging.INFO)



import streamlit as st
import matplotlib.cm as cm
import matplotlib as mpl
import matplotlib.colors as colors
import networkx as nx
import numpy as np
from backend import graph_physics as chem



# set the colormap and centre the colorbar
class MidpointNormalize(colors.Normalize):
        """
        Normalise the colorbar so that diverging bars work there way either side from a prescribed midpoint value)

        e.g. im=ax1.imshow(array, norm=MidpointNormalize(midpoint=0.,vmin=-100, vmax=100))
        """
        def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
                self.midpoint = midpoint
                colors.Normalize.__init__(self, vmin, vmax, clip)

        def __call__(self, value, clip=None):
                # I'm ignoring masked values and all kinds of edge cases to make a
                # simple example...
                x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
                return np.ma.masked_array(np.interp(value, x, y), np.isnan(value))


def draw_bw(G):
        pos = nx.spectral_layout(G)
        pos = nx.kamada_kawai_layout(G,pos=pos,weight="mass")
        font_size = 10 if G.number_of_nodes()<10 else 6
        alpha = 1 if G.number_of_nodes()<150 else 0.855
        nx.draw(G,pos=pos,with_labels=True, node_color='w',font_size=font_size,width=0.2,alpha=alpha)
        st.pyplot()

def draw_color(G, pot, window, labels, node_size = 50, cmap="gnuplot"):
        pos = nx.kamada_kawai_layout(G,weight="weight")
        N = G.number_of_nodes()
        font_size = 11 if N<10 else 9
        if N<10:
                alpha = 1
        elif 10<N<50:
                font_size = 9
                alpha = 0.8
        elif 50<N<100:
                font_size = 8
                alpha = 0.7
        else:
                alpha = 0.7
                font_size = 7
        scheme = mpl.pyplot.get_cmap(cmap)
        

        cnorm = colors.Normalize(vmin=window[0], vmax = window[2])
        smap = cm.ScalarMappable(norm=MidpointNormalize(vmin=window[0],vmax=window[2],midpoint=window[1]), cmap=scheme)
        #smap = cm.ScalarMappable(norm=cnorm, cmap=scheme)
        colorvals = smap.to_rgba(pot)
        nx.draw(G,pos=pos,with_labels=labels, node_color = colorvals, node_size = node_size,font_size=font_size,width=0.2,alpha=alpha)
        cbar = mpl.pyplot.colorbar(smap,ticks=window,orientation='horizontal',label="Potential field")
        cbar.ax.set_xticklabels(["   (-)","Stationary", "(+)      "])
        st.pyplot()


def draw(G, conn, labels = True, cmap = "terrain_r"):
        energy = np.array(chem.read_node_prop(conn,G,"energy"))
        mass = np.array(chem.read_node_prop(conn,G,"mass"))
        minm, maxm, avgm, medm = chem.prop_bounds(conn,prop="mass")
        multiplier = -3200/np.log10(avgm)
        node_size = 15+multiplier*mass
        minv, maxv, avgv, medv = chem.prop_bounds(conn,slices=10)

        #center = chem.boundary(conn,"nodes")
        window = [minv,0,maxv]
        #logging.info(f"Window: {window}, {[minm,maxm,avgm,medm]},{[minv,maxv,avgv,medv]}")   
        draw_color(G,pot = energy.reshape(-1,), node_size = node_size, window = window, labels = labels, cmap = cmap)
