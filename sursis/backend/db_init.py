from backend import db
from networkx import line_graph as dual
import sqlite3, logging


def initialize(conn):
  sql_nodes_table =\
  """CREATE TABLE IF NOT EXISTS nodes (
          id integer PRIMARY KEY,
          name text NOT NULL,
          mass real,
          energy real,
          degree real);"""
  sql_edges_table =\
  """CREATE TABLE IF NOT EXISTS edges (
          id integer PRIMARY KEY,
          left integer NOT NULL,
          right integer NOT NULL,
          mass real,
          energy real,
          degree real);"""
  sql_named_edges_view=\
  """CREATE VIEW named_edges as 
      SELECT edges.id,
             n1.name as node_1,
             n2.name as node_2, 
             edges.mass, 
             edges.energy,
             edges.degree 
     FROM edges 
     LEFT JOIN nodes AS n1 
                     ON n1.id = edges.left 
     LEFT JOIN nodes AS n2 
                     ON n2.id = edges.right;"""
  try:
      c = conn.cursor()
      c.execute(sql_nodes_table)
      c.execute(sql_edges_table)
      c.execute(sql_named_edges_view)
  except sqlite3.Error as e:
      logging.error(e)




def reset(conn, G):
  initialize(conn)
  # NODES
  for node, data in G.nodes(data=True):
      db.push(conn,\
          """INSERT INTO nodes (name, mass, energy, degree)
          	VALUES (?, ?, ?, ?)""",
             node, data["mass"], data["energy"], G.degree[node])
  # EDGES
  H = dual(G)
  for edge, data in H.nodes(data = True):
      n1 = min(edge); n2 = max(edge)
      id_1, id_2 = db.get_node_id(conn,n1), db.get_node_id(conn,n2)
      db.push(conn,\
      	"""INSERT INTO edges (left, right, mass, energy, degree)
      	   VALUES (?, ?, ?, ?, ?)""",
      	   id_1, id_2, data["mass"], data["energy"], H.degree[edge])
