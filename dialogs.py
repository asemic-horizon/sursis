import streamlit as st
import ui_elems as ui
import db

def node_entry(conn):
	node = st.text_input('Enter new node name')
	add_button, del_button = ui.add_del()
	if node and add_button: 
		found = db.write_node(conn,node)
		conn.update()
		ui.if_confirm(found,"Name already exists")
	if node and del_button:
		found = db.del_node(conn,node)
		conn.update()
		ui.if_confirm(found)	
	return None 

def edge_entry(conn):
	node_1 = ui.known_field_input(conn,"Source","jazz")
	node_2 = ui.known_field_input(conn,"Target","espionage")
	add_button, del_button = ui.add_del()
	if node_1 and node_2 and add_button: 
		db.write_edge(conn, node_1,node_2)
		conn.update(); ui.confirm()
	if node_1 and node_2 and del_button:
		found = True
		while found:
			found = db.del_edge(conn,node_1, node_2)
		st.write("(Edge deleted.)")
		conn.update(); ui.confirm()
	return None

def node_merge(conn):
	nodes = db.list_nodes(conn)
	u,v = 1,3
	node_1 = st.selectbox("Source 1",nodes,index=u)
	node_2 = st.selectbox("Source 2",nodes,index=v)
	if node_1 in nodes and node_2 in nodes:
		if node_1 == node_2:
			defval = node_1
		else:
			defval = f"{node_1}/{node_2}"
		new_node = st.text_input("New node", value=defval)
		merge_button = st.button("Merge")
		if merge_button:
			db.merge_nodes(conn,node_1,node_2, new_node)
			conn.update(); ui.confirm()
	return None

def trail_node_entry(conn)
	nodes = db.list_nodes(conn)
	node_1 = st.selectbox("Existing",nodes,index=nodes.index("jazz"))
	node_2 = st.text_input('New')

	nonn_button = st.button("Add and connect")
	if node_1 and node_2 and nonn_button:
		db.write_node(conn,node_2)
		db.write_edge(conn,node_1,node_2)
		conn.update(); ui.confirm()
	return None

def dyad_entry(conn):
	node_1 = st.text_input('Enter new node 1 name')
	node_2 = st.text_input('Enter new node 2 name')
	add_button, del_button = ui.add_del()
	if node_1 and node_2 and add_button:
		db.write_node(conn,node_1)
		db.write_node(conn,node_2)
		db.write_edge(conn,node_1, node_2)
		conn.update(); ui.confirm()
	if node_1 and node_2 and del_button:
		db.del_edge(conn,node_1,node_2)
		db.del_node(conn,node_1)
		db.del_node(conn,node_2)
		conn.update(); ui.confirm()		parent = st.text_input('Enter head node name')
		left = st.text_input('Enter left child name')
		right = st.text_input('Enter right child name')
		add_button, del_button = ui.add_del()
		if parent and left and right and add_button:
			db.write_node(conn,parent)
			db.write_node(conn,left)
			db.write_node(conn,right)
			db.write_edge(conn,parent,left)
			db.write_edge(conn,parent,right)
			conn.update(); ui.confirm()
		if parent and left and right and del_button:
			db.del_node(conn, parent)
			db.del_node(conn, left)
			db.del_node(conn, right)
			db.del_edge(conn, parent,left)
			db.del_edge(conn, parent,right)
			conn.update(); ui.confirm()
	return None

def triad_entry(conn):
	parent = st.text_input('Enter head node name')
	left = st.text_input('Enter left child name')
	right = st.text_input('Enter right child name')
	add_button, del_button = ui.add_del()
	if parent and left and right and add_button:
		db.write_node(conn,parent)
		db.write_node(conn,left)
		db.write_node(conn,right)
		db.write_edge(conn,parent,left)
		db.write_edge(conn,parent,right)
		conn.update(); ui.confirm()
	if parent and left and right and del_button:
		db.del_node(conn, parent)
		db.del_node(conn, left)
		db.del_node(conn, right)
		db.del_edge(conn, parent,left)
		db.del_edge(conn, parent,right)
		conn.update(); ui.confirm()
	return None