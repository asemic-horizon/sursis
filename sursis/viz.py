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


def draw_bw(G, pos_fun=nx.spring_layout):
        pos = pos_fun(G)
        font_size = 10 if G.number_of_nodes()<10 else 6
        alpha = 1 if G.number_of_nodes()<150 else 0.855
        nx.draw(G,pos=pos,with_labels=True, node_color='w',font_size=font_size,width=0.2,alpha=alpha)
        st.pyplot()

def draw_color(G, pot, window, labels, node_size = 50, pos_fun=nx.spring_layout, cmap="gnuplot"):
        pos = pos_fun(G)
        N = G.number_of_nodes()
        font_size = 11 if N<10 else 9
        if N<10:
                alpha = 1
        elif N<50:
                alpha = 0.8
        elif N<200:
                alpha = 0.7
        else:
                alpha = 0.7
        scheme = mpl.pyplot.get_cmap(cmap)
        

        cnorm = colors.Normalize(vmin=window[0], vmax = window[2])
        smap = cm.ScalarMappable(norm=MidpointNormalize(vmin=window[0],vmax=window[2],midpoint=window[1]), cmap=scheme)
        #smap = cm.ScalarMappable(norm=cnorm, cmap=scheme)
        colorvals = smap.to_rgba(pot)
        nx.draw(G,pos=pos,with_labels=labels, node_color = colorvals, node_size = node_size,font_size=font_size,width=0.2,alpha=alpha)
        cbar = mpl.pyplot.colorbar(smap,ticks=window,orientation='horizontal',label="Potential field")
        cbar.ax.set_xticklabels(["   (-)","Stationary", "(+)      "])
        st.pyplot()


def draw(G, conn, labels = True, cmap = "terrain_r", pos_fun=nx.kamada_kawai_layout):
        energy = np.array(chem.read_node_prop(conn,G,"energy"))
        mass = np.array(chem.read_node_prop(conn,G,"mass"))
        minm, maxm, avgm, medm = chem.prop_bounds(conn,prop="mass")
        multiplier = -1200/np.log10(medm)
        node_size = 35+multiplier*mass
        minv, maxv, avgv, medv = chem.prop_bounds(conn,slices=10)
        #pot = np.exp(energy)
        #window = [minv if -minv > maxv else -maxv, medv, maxv if -maxv > minv else -minv]
        skew = 3.5
        energy[energy>0] = skew*energy[energy>0]
        center = chem.boundary(conn,"nodes")
        window = [minv,center,skew*maxv]
        logging.info(f"Window: {window}, {[minm,maxm,avgm,medm]},{[minv,maxv,avgv,medv]}")   
        draw_color(G,pot = energy.reshape(-1,), node_size = node_size, window = window, labels = labels, pos_fun = pos_fun, cmap = cmap)
