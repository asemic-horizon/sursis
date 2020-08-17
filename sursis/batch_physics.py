import json
import os
import backend.graph_physics as chem
import backend.db as db
if os.path.isfile("physics.json"):
	with open("physics.json","r") as f: physics_args = json.load(f)
else:
	physics_args = {"outer_boundary_value":1.5,
				    "core_boundary_value":1.5, 
				    "crit_degree": 1,
					"crit_core_number": 3, "fast": False}

with db.nc() as conn:
	chem.update_physics(conn,model = "dirichlet", max_iter = 1000, tol = 1e-5, **physics_args)
