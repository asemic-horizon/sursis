from backend import db

with db.nc() as conn:
	db.initialize()