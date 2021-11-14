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

# insert_stock(connection, cursor, name, ticker, count)
#     	# records = select_stocks_filter(cursor, name=name)
#     	# print(records)

# try:
#     # Connect to an existing database
#     connection = psycopg2.connect(user="postgres",
#                                   password="postgres",
#                                   database="testdb")

#     # Create a cursor to perform database operations
#     cursor = connection.cursor()
#     # Print PostgreSQL details
#     print("PostgreSQL server information")
#     print(connection.get_dsn_parameters(), "\n")
#     while True:
#     	a = input()
#     	if a == 'q':
#     		break
#     	name, ticker, count = a.split()
#     	count = int(count)
#     	

#     	# Executing a SQL query
#     	cursor.execute("SELECT * from stocks;")
#     	# Fetch result
#     	record = cursor.fetchall()
#     	print(record, "\n")

# except (Exception, Error) as error:
#     print("Error while connecting to PostgreSQL", error)
# finally:
#     if (connection):
#         cursor.close()
#         connection.close()
#         print("PostgreSQL connection is closed")