# Sursis - [personal] <- [notebook] -> [network]

Sursis is a simple web app built on top of [Streamlit](https://streamlit.io). In a way, it abuses the goals of Streamlit, which are closer to Jupyter notebooks, but is very simply written and does the trick for me.

The concept is that you have a single undirected, unweighted graph to connect across many domains. Not unlike a written personal notes.txt or outline, but not sequential and able to reach back and connect separate "moments".


Sursis runs locally; or preferrably on a cheap VPS/Digital Ocean-type VM so you'll be able to use it on your phone. 



## Usage demo

![](https://imgur.com/a/dB9Xb5l.gif)

*(An animation should be opening above. Sometimes github doesn't load it and I don't know why. If you see nothing, please [click here](https://imgur.com/a/dB9Xb5l).)*

The coloring of nodes is giving by the solution to a Poisson equation Lx = w, where w are the observed "weights" (currently, the betweenness centrality of nodes). In this way we expect to capture an idea of the balance of forces in the graph structures.

Edges are also weighted in the exact same way, calculating the inverse Laplacian of the dual graph. It is expected that the layout algorithms take these weights into account, but I don't have much control over that right now.

## Installing

Clone the repository and create an environment

    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt

If you don't have a preexisting notebook, run 

     python initialize_script.py

Note that for the time being the notebook is always stored as `data.sqlite`.

To run,

    streamlit run app.py

You *will* get an error in the default visualization screen with an empty notebook/graph. Just add some nodes and then connections.
