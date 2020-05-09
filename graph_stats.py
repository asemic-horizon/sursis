import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx 
import collections
def plot_degree_distribution(graph):
	degree_sequence = sorted([d for n, d in graph.degree()], reverse=True)  # degree sequence
	degreeCount = collections.Counter(degree_sequence)
	deg, cnt = zip(*degreeCount.items())
	plt.scatter(deg,cnt)

def stats_view(graph):

	plot_degree_distribution(graph)