# Sursis - network notebook for personal uses

Sursis is a simple web app built on top of [Streamlit](https://streamlit.io). In a way, it abuses the goals of Streamlit, which are closer to Jupyter notebooks, but is very simply written and does the trick for me.

The concept is that you have a single undirected, unweighted graph to connect across many domains. Not unlike a written personal notes.txt or outline, but not sequential and able to reach back and connect separate "moments".


Sursis runs locally; or preferrably on a cheap VPS/Digital Ocean-type VM so you'll be able to use it on your phone. 


## Installing

Clone the repository,

    pip install -r requirements.txt

To run,

    streamlit run app.py

## Usage demo

![demo](https://i.imgur.com/IysQtMs.mp4)

The coloring of nodes is giving by the solution to a Poisson equation Lx = w, where w are the observed "weights" (currently, the betweenness centrality of nodes). In this way we expect to capture an idea of the balance of forces in the graph structures.

Edges are also weighted in the exact same way, calculating the inverse Laplacian of the dual graph. It is expected that the layout algorithms take these weights into account, but I don't have much control over that right now.
