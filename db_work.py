# import psycopg2
# from psycopg2 import Error


def insert_stock(connection, cursor, ticker, name=None, count=1):
	if not name:
		name = ticker
	insert_query = f"INSERT INTO stocks (name, ticker, count) VALUES ('{name}', '{ticker}', {count});"
	cursor.execute(insert_query)
	connection.commit()
	if cursor.rowcount == 1:
		# Successful save
		return True
	else:
		# Something happened during insert
		return False

def delete_stock(connection, cursor, **kwargs):

	filter_query = ""
	if kwargs:
		filter_query = 'where'
		for key, val in kwargs.items():
			filter_query += f" {key} = '{val}' and"
		filter_query = filter_query[:-3]
	else:
		return False
	delete_query = "delete from stocks " + filter_query + ";"
	cursor.execute(delete_query)
	connection.commit()
	if cursor.rowcount > 0:
		# Successful delete
		return True
	else:
		# Something happened during delete
		return False


def select_stocks(cursor):
	select_query = "select name, ticker, count from stocks;"
	cursor.execute(select_query)
	records = cursor.fetchall()

	return records


def select_stocks_filter(cursor, **kwargs):
	filter_query = ''
	if kwargs:
		filter_query += 'where'
		for key, val in kwargs.items():
			filter_query += f" {key} = '{val}' and"
		filter_query = filter_query[:-3]
	select_query = "select name, ticker, count from stocks " + filter_query + ";" 
	cursor.execute(select_query)
	records = cursor.fetchall()

	return records

