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
# def _check_body(request, fields): 
# 	return all(filed in request.json and type(request.json[field]) in types
# 			for field, types in fields.items())


@server.route("/api/countries", methods=["POST"])
def add_country():
	data = request.json
	types_ref = ['str', 'float', 'float']

	request_types = []
	for val in request.json:
		request_types.append(type(request.json[val]).__name__)
	# verific daca argumentele au tipul potrivit
	if (types_ref!=request_types):
		return Response(
			status=400)
	
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

@server.route("/api/countries/<id>", methods=["POST"])
def get_countries(id=None):
	data = request.json
	types_ref = ['str', 'float', 'float']

	request_types = []
	for val in request.json:
		request_types.append(type(request.json[val]).__name__)
	# verific daca argumentele au tipul potrivit
	if (types_ref!=request_types):
		return Response(
			status=400)
	
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


@server.route("/movie/<id>", methods=["GET", "PUT", "DELETE"])
def handle_request(id=None):
	global MOVIES

	if request.method == "GET":
		if id:
			movie_id = int(id)
			if movie_id not in MOVIES:
				return Response(status=404)

			movies = {"id": movie_id, "nume": MOVIES[movie_id]["nume"]}
		else:
			movies = [{"id": movie_id, "nume": movie["nume"]}
				for movie_id, movie in MOVIES.items()]

		return Response(response=json.dumps(movies), status=200,
			mimetype="application/json")
	elif request.method == "POST":
		json_data = request.json

		if json_data and "nume" in json_data and json_data["nume"] != "":
			movie_id = _get_first_available_id()
			MOVIES[movie_id] = json_data

			return Response(status=201)
		else:
			return Response(status=400)
	elif request.method == "PUT":
		movie_id = int(id)

		if movie_id not in MOVIES:
			return Response(status=404)

		json_data = request.json
		if json_data and "nume" in json_data and json_data["nume"] != "":
			MOVIES[movie_id] = json_data
			return Response(status=200)

		return Response(status=404)
	elif request.method == "DELETE":
		movie_id = int(id)
		if movie_id not in MOVIES:
			return Response(status=404)

		del(MOVIES[movie_id])

		return Response(status=200)
	else:
		return Response(status=400)


@server.route("/reset", methods=["DELETE"])
def delete_all():
	global MOVIES
	MOVIES = {}

	return Response(status=200)

if __name__ == '__main__':
	server.run('0.0.0.0', debug=True)
