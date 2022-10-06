def psql_connect(psql):
    return psql.connect(dbname='luas_db', user='posgres', 
                        password='66atituf', host='localhost')

def fetch_all(psql, table_name):
	cursor = psql.connect().cursor()
	cursor.execute("SELECT * FROM " + table_name)
	data = cursor.fetchall()
	if data is None:
		return "Problem!"
	else:
		return data


def fetch_one(psql, table_name, column, value):
	cursor = psql_connect(psql).cursor()
	cursor.execute("SELECT * FROM " + table_name + " WHERE " + column + " = '" + str(value) + "'")
	data = cursor.fetchone()
	if data is None:
		return "Problem!"
	else:
		return data


def count_all(psql):
	cursor = psql_connect(psql).cursor()
	cursor.execute("SHOW TABLES")
	tables = cursor.fetchall()
	data = ()
	for (table) in tables:
		data += ((table[0], count_table(psql, table[0])),)
	return data


def count_table(psql, table_name):
	cursor = psql_connect(psql).cursor()
	cursor.execute("SELECT COUNT(*) FROM " + table_name)
	table_count = cursor.fetchone()
	return table_count[0]


def clean_data(data):
	del data["cat"]
	del data["act"]
	del data["id"]
	del data["modifier"]
	return data


def insert_one(psql, table_name, data):
	data = clean_data(data)
	columns = ','.join(data.keys())
	values = ','.join([str("'" + e + "'") for e in data.values()])
	insert_command = "INSERT into " + table_name + " (%s) VALUES (%s) " % (columns, values)
	try:
		con = psql_connect(psql)
		cursor = con.cursor()
		cursor.execute(insert_command)
		con.commit()
		return True
	except Exception as e:
		print("Problem inserting into db: " + str(e))
		return False


def update_one(psql, table_name, data, modifier, item_id):
	data = clean_data(data)
	update_command = "UPDATE " + table_name + " SET {} WHERE " + modifier + " = " + item_id + " LIMIT 1"
	update_command = update_command.format(", ".join("{}= '{}'".format(k, v) for k, v in data.items()))
	try:
		con = psql_connect(psql)
		cursor = con.cursor()
		cursor.execute(update_command)
		con.commit()
		return True
	except Exception as e:
		print("Problem updating into db: " + str(e))
		return False


def delete_one(psql, table_name, modifier, item_id):
	try:
		con = psql_connect(psql)
		cursor = con.cursor()
		delete_command = "DELETE FROM " + table_name + " WHERE " + modifier + " = " + item_id + " LIMIT 1"
		cursor.execute(delete_command)
		con.commit()
		return True
	except Exception as e:
		print("Problem deleting from db: " + str(e))
		return False
