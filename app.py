import streamlit as st
import random

mode = st.radio("Modality",
	["Enter new node","Connect nodes"])

if mode == "Enter new node":
	field = st.text_input('Text field')
	if st.button("Append"):
		with open('nodes.txt','a') as f:
			f.write(field+"\n")
else:
	with open('nodes.txt','r') as f:
		fields =  f.readlines()
	fields = [f.strip("\n") for f in fields]
	index = random.randint(0,len(fields)-1)
	field1 = st.selectbox("Source",fields,index=index)
	index = random.randint(0,len(fields)-1)
	field2 = st.selectbox("Target",fields,index=index)

	if st.button("Append"):
		with open('edges.txt','a') as f:
			f.write(f"{field1} {field2}\n")

