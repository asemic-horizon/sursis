sqlite3 data.sqlite "select * from nodes" > nodes.txt
sqlite3 data.sqlite "select * from edges" > edges.txt
sqlite3 data.sqlite "select * from edges" > named_edges.txt
