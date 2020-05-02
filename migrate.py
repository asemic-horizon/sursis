# data migration script
import db

with db.nc("data.sqlite") as conn:
	db.initialize(conn)
	db.convert_json(conn,"data.json")
	