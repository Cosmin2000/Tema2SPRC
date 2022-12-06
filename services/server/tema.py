from flask import Flask, json, Response, request, jsonify
from itertools import count, filterfalse
from functools import reduce
import psycopg2

server = Flask(__name__)

conn = psycopg2.connect(host='db',
							port='5432',
							user='meteo_user',
							password='meteo_pass',
							database='meteo_db')
	
conn.autocommit=True	
curr = conn.cursor()

def valid_body(types_ref, request):
	request_types = []
	if (len(request.json) != len(types_ref)):
		return False
	for val in request.json:
		request_types.append(type(request.json[val]).__name__)
	# verific daca argumentele au tipul potrivit
	# print(request_types, flush=True)
	# if (types_ref!=request_types):
	# 	return False
	for  indx, req_type in enumerate(request_types):
		if req_type not in types_ref[indx]:
			return False

	return True

def process_get_response(fields, table_data):
	result = []
	for num, row in enumerate(table_data):
		# am facut in cast fiindca imi transporta datele lon si lat de tip string
		resultRow = {}
		for i in range(len(fields) - 2):
			resultRow[fields[i]] = row[i]
		resultRow[fields[len(fields) - 2]] = float(row[len(fields) - 2])
		resultRow[fields[len(fields) - 1]] = float(row[len(fields) - 1])
		result.append(resultRow)
	return result


@server.route("/api/countries", methods=["POST"])
def add_country():
	data = request.json
	types_ref = [['str'], ['int','float'], ['int','float']]

	if not valid_body(types_ref, request):
		return Response(status=400)

	try:
		curr.execute('INSERT INTO Tari(nume_tara, latitudine, longitudine) VALUES (%s, %s, %s) RETURNING id',  (data['nume'], data['lat'], data['lon']))
		returned_id = curr.fetchone()[0]
	except psycopg2.Error: 
		# exista deja o tara cu acelasi id
		return Response(
			status=409)

	response = {'id':returned_id}
	return Response(
		response=json.dumps(response),
		status=201
	)

@server.route("/api/countries", methods=["GET"])
def get_countries():
	data = request.json

	try:
		curr.execute('SELECT * FROM Tari')
		table_data = curr.fetchall()
		fields = ['id','nume', 'lat', 'lon']
		
		result = process_get_response(fields, table_data)
	except psycopg2.Error: 
		# o eroare in caz ca s-a intamplat ceva in baza
		return Response(
			status=404)

	return Response(
		response=json.dumps(result, sort_keys=False),
		status=200,
	)

@server.route("/api/countries/<id>", methods=["PUT"])
def modify_country(id=None):
	data = request.json

	types_ref = [['int'],['str'], ['int','float'],['int', 'float']]
	# verific daca argumentele au tipul potrivit
	if (id == None or not valid_body(types_ref, request) or int(id) != data['id']):
		return Response(status=400)
	

	try:
		curr.execute('UPDATE Tari SET nume_tara = %s, longitudine = %s, latitudine = %s WHERE id = %s',(data['nume'], data['lon'], data['lat'], data['id']))

	except psycopg2.errors.lookup("20000"): 
		# nu s-a gasit tara cu id-ul specificat
		return Response(
			status=404)
	except psycopg2.errors.lookup("23505"): 
		# unique violation
		return Response(
			status=409)

	return Response(
		status=200
	)

@server.route("/api/countries/<id>", methods=["DELETE"])
def delete_country(id=None):
	data = request.json

	if id == None:
		return Response(status = 400)

	curr.execute('DELETE FROM Tari WHERE id = %s', (id,))
	if (curr.rowcount == 0):
		return Response(
			status=404
		)
	else:
		return Response(
			status=200
		)


# ===================== CITIES ======================================

@server.route("/api/cities", methods=["POST"])
def add_city():
	data = request.json
	types_ref = [['int'], ['str'], ['int', 'float'], ['int', 'float']]

	if not valid_body(types_ref, request):
		return Response(status=400)

	try:
		curr.execute('INSERT INTO Orase(id_tara, nume_oras, latitudine, longitudine) VALUES (%s, %s,%s, %s) RETURNING id',  ( data['idTara'],data['nume'], data['lat'], data['lon']))
		returned_id = curr.fetchone()[0]
	except psycopg2.Error as e: 
		# exista deja o tara cu acelasi id
		print(e)
		return Response(
			status=409)

	response = {'id':returned_id}
	return Response(
		response=json.dumps(response),
		status=201
	)

@server.route("/api/cities", methods=["GET"])
def get_cities():
	data = request.json

	try:
		curr.execute('SELECT id, id_tara, nume_oras, latitudine, longitudine FROM Orase')
		table_data = curr.fetchall()
		fields = ['id', 'idTara','nume', 'lat', 'lon']

		result = process_get_response(fields, table_data)
	except psycopg2.Error: 
		# o eroare in caz ca s-a intamplat ceva in baza
		return Response(
			status=404)

	return Response(
		response=json.dumps(result, sort_keys=False),
		status=200,
	)

@server.route("/api/cities/country/<id_Tara>", methods=["GET"])
def get_cities_by_country(id_Tara=None):
	data = request.json

	if id_Tara == None:
		return Response(status=400)

	try:
		curr.execute('SELECT * FROM Orase WHERE id_tara = %s',(id_Tara))
		table_data = curr.fetchall()
		fields = ['id', 'idTara','nume', 'lat', 'lon']
		result = process_get_response(fields, table_data)
	except psycopg2.Error:
		return Response(status=500)

	return Response(status=200,
					response=json.dumps(result, sort_keys=False))

@server.route("/api/cities/<id>", methods=["PUT"])
def modify_city(id=None):
	data = request.json

	print(request.json, flush=True)
	print(id, flush=True)
	types_ref = [['int'],['int'],['str'], ['int', 'float'],['int', 'float']]
	# verific daca argumentele au tipul potrivit
	if (id == None or not valid_body(types_ref, request) or int(id) != data['id']):
		return Response(status=400)

	try:
		curr.execute('UPDATE Orase SET id_tara = %s, nume_oras = %s,latitudine = %s, longitudine = %s WHERE id = %s',
		(data['idTara'] ,data['nume'], data['lat'], data['lon'], id))

	except psycopg2.errors.lookup("20000"): 
		# nu s-a gasit tara cu id-ul specificat
		return Response(
			status=404)
	except psycopg2.errors.lookup("23505"): 
		# unique violation
		return Response(
			status=409)

	return Response(
		status=200
	)


@server.route("/api/cities/<id>", methods=["DELETE"])
def delete_city(id=None):
	data = request.json

	if id == None:
		return Response(status = 400)

	curr.execute('DELETE FROM Orase WHERE id = %s', (id,))
	if (curr.rowcount == 0):
		return Response(
			status=404
		)
	else:
		return Response(
			status=200
		)

# @server.route("/movie/<id>", methods=["GET", "PUT", "DELETE"])
# def handle_request(id=None):
# 	global MOVIES

# 	if request.method == "GET":
# 		if id:
# 			movie_id = int(id)
# 			if movie_id not in MOVIES:
# 				return Response(status=404)

# 			movies = {"id": movie_id, "nume": MOVIES[movie_id]["nume"]}
# 		else:
# 			movies = [{"id": movie_id, "nume": movie["nume"]}
# 				for movie_id, movie in MOVIES.items()]

# 		return Response(response=json.dumps(movies), status=200,
# 			mimetype="application/json")
# 	elif request.method == "POST":
# 		json_data = request.json

# 		if json_data and "nume" in json_data and json_data["nume"] != "":
# 			movie_id = _get_first_available_id()
# 			MOVIES[movie_id] = json_data

# 			return Response(status=201)
# 		else:
# 			return Response(status=400)
# 	elif request.method == "PUT":
# 		movie_id = int(id)

# 		if movie_id not in MOVIES:
# 			return Response(status=404)

# 		json_data = request.json
# 		if json_data and "nume" in json_data and json_data["nume"] != "":
# 			MOVIES[movie_id] = json_data
# 			return Response(status=200)

# 		return Response(status=404)
# 	elif request.method == "DELETE":
# 		movie_id = int(id)
# 		if movie_id not in MOVIES:
# 			return Response(status=404)

# 		del(MOVIES[movie_id])

# 		return Response(status=200)
# 	else:
# 		return Response(status=400)


# @server.route("/reset", methods=["DELETE"])
# def delete_all():
# 	global MOVIES
# 	MOVIES = {}

# 	return Response(status=200)

if __name__ == '__main__':
	server.run('0.0.0.0', debug=True)
