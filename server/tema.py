from flask import Flask, json, Response, request, jsonify
from itertools import count, filterfalse
from functools import reduce
import psycopg2

server = Flask(__name__)

# Fac legatura cu baza de date PostgreSQL
conn = psycopg2.connect(host='db',
						port='5432',
						user='meteo_user',
						password='meteo_pass',
						database='meteo_db')
	
conn.autocommit=True	
curr = conn.cursor()

NOT_FOUND = "20000"  # Codul returnat de psycopg2 pentru erori NOT_FOUND
CONFLICT = "23505"   # Codul returnat de psycopg2 pentru erori CONFLICT


def get_temperatures_by_city_or_country(id, statement):
	args = request.args
	fromDate = args.get('from')
	untilDate = args.get('until')
	params = []
	conditions = []
	if id == None:
		return Response(400)

	# Construiesc clauza WHERE
	if fromDate:
		conditions.append('TO_CHAR(t.timestamp, \'YYYY-MM-DD\') >= %s')
		params.append(fromDate)
	if untilDate:
		conditions.append('TO_CHAR(t.timestamp, \'YYYY-MM-DD\') <= %s')
		params.append(untilDate)
	# Pun clauza nula daca nu am nimic
	clause = '' if len(conditions) == 0 else ' WHERE ' + ' AND '.join(conditions)
	query = statement % (id, clause)
	curr.execute(query, params)
	# Iau rezultatele si le parsez
	table_data = curr.fetchall()
	fields = ['id', 'valoare','timestamp']
	result_data = process_get_response(fields, table_data)

	return json_response(result_data, 200)

def make_put_request(expected_types, expected_keys, query, id):
	data = request.json
	# Verific daca requestul este valid
	if (id == None or not valid_body(expected_types, expected_keys, request) or int(id) != data['id']):
		return Response(status=400)
	
	# Construiesc parametrii cererii (adaug id-ul la final, de asta fac slice)
	expected_keys = expected_keys[1:]
	params = [data[x] for x in expected_keys]
	params.append(id)
	# Execut query-ul si verific erorile care pot aparea
	try:
		curr.execute(query,params)

	except psycopg2.errors.lookup(NOT_FOUND): 
		return Response(status=404)
	except psycopg2.errors.lookup(CONFLICT): 
		return Response(status=409)
	except:
		return Response(status=404)

	return Response(status=200)

def make_post_request(expected_types, expected_keys, query):
	# Verific daca requestul este valid

	if not valid_body(expected_types, expected_keys, request):
		return Response(status=400)
	
	# Construiesc parametrii pentru cerere
	data = request.json
	params = [data[x] for x in expected_keys]

	# Execut query-ul si verific erorile care pot aparea
	try:
		curr.execute(query,  params)
		returned_id = curr.fetchone()[0]
	except psycopg2.errors.lookup(NOT_FOUND): 
		return Response(status=404)
	except psycopg2.errors.lookup(CONFLICT):
		return Response(status=409)
	except:
		return Response(status=404)

	return json_response({'id':returned_id}, 201)

def make_delete_request(query, id):
	# Verific daca exista id-ul
	if id == None:
		return Response(status=400)

	curr.execute(query, (id,))
	# Verific daca s-a modificat vreo entitate (sters)
	if (curr.rowcount == 0):
		return Response(status=404)
	else:
		return Response(status=200)


def make_get_request(fields, query):
	# Execut query-ul si procesez raspunsul
	curr.execute(query)
	table_data = curr.fetchall()
	result = process_get_response(fields, table_data)

	return json_response(result, 200)

def json_response(response, status):
	return Response(
		response=json.dumps(response, sort_keys=False),
		status=status,
		mimetype='application/json' 
	)

def valid_body(expected_types, expected_keys, request):
	request_types = []
	# Verific daca exista toate elementele si daca au tipul corespunzator
	try:
		keys = list(request.get_json().keys())
	except:
		return False

	if expected_keys != list(keys):
		return False
	for val in request.json:
		request_types.append(type(request.json[val]).__name__)
	for  indx, req_type in enumerate(request_types):
		if req_type not in expected_types[indx]:
			return False
	return True

def process_get_response(fields, table_data):
	result = []
	for num, row in enumerate(table_data):
		resultRow = {}	
		for i in range(len(fields)):
			resultRow[fields[i]] = row[i]
		result.append(resultRow)
	return result

# =============================== COUNTRIES ============================================

@server.route("/api/countries", methods=["POST"])
def add_country():
	expected_types = [['str'], ['int','float'], ['int','float']]
	expected_keys = ['nume', 'lat', 'lon']
	query = 'INSERT INTO Tari(nume_tara, latitudine, longitudine) VALUES (%s, %s, %s) RETURNING id'
	return make_post_request(expected_types, expected_keys, query)

@server.route("/api/countries", methods=["GET"])
def get_countries():
	fields = ['id','nume', 'lat', 'lon']
	query = 'SELECT id, nume_tara, latitudine::float, longitudine::float FROM Tari'
	return make_get_request(fields, query)

@server.route("/api/countries/<id>", methods=["PUT"])
def modify_country(id=None):
	expected_types = [['int'],['str'], ['int','float'],['int', 'float']]
	expected_keys = ['id', 'nume', 'lat', 'lon']
	query = 'UPDATE Tari SET nume_tara = %s, latitudine = %s, longitudine = %s WHERE id = %s'
	return make_put_request(expected_types, expected_keys, query, id)

@server.route("/api/countries/<id>", methods=["DELETE"])
def delete_country(id=None):
	query = 'DELETE FROM Tari WHERE id = %s'
	return make_delete_request(query, id)

# ================================ CITIES =================================================

@server.route("/api/cities", methods=["POST"])
def add_city():
	expected_types = [['int'], ['str'], ['int', 'float'], ['int', 'float']]
	expected_keys = ['idTara', 'nume', 'lat', 'lon']
	query = 'INSERT INTO Orase(id_tara, nume_oras, latitudine, longitudine) VALUES (%s, %s,%s, %s) RETURNING id'
	return make_post_request(expected_types, expected_keys, query)

@server.route("/api/cities", methods=["GET"])
def get_cities():
	fields = ['id', 'idTara','nume', 'lat', 'lon']
	query = 'SELECT id, id_tara, nume_oras, latitudine::float, longitudine::float FROM Orase'
	return make_get_request(fields, query)

@server.route("/api/cities/country/<id_Tara>", methods=["GET"])
def get_cities_by_country(id_Tara=None):
	if id_Tara == None:
		return Response(status=400)

	fields = ['id', 'idTara','nume', 'lat', 'lon']
	query = 'SELECT id, id_tara, nume_oras, latitudine::float , longitudine::float FROM Orase WHERE id_tara = %s' % (id_Tara)
	return make_get_request(fields, query)

@server.route("/api/cities/<id>", methods=["PUT"])
def modify_city(id=None):
	expected_types = [['int'],['int'],['str'], ['int', 'float'],['int', 'float']]
	expected_keys = ['id', 'idTara', 'nume', 'lat', 'lon']
	query = 'UPDATE Orase SET id_tara = %s, nume_oras = %s,latitudine = %s, longitudine = %s WHERE id = %s'
	return make_put_request(expected_types, expected_keys, query, id)


@server.route("/api/cities/<id>", methods=["DELETE"])
def delete_city(id=None):
	query = 'DELETE FROM Orase WHERE id = %s'
	return make_delete_request(query, id)

# ================================== TEMPERATURES =========================================


@server.route("/api/temperatures", methods=["POST"])
def add_temperature():
	expected_types = [['int'], ['int', 'float']]
	expected_keys = ['idOras', 'valoare']
	query = 'INSERT INTO Temperaturi(id_oras, valoare) VALUES (%s, %s) RETURNING id'
	return make_post_request(expected_types, expected_keys, query)

@server.route("/api/temperatures", methods=["GET"])
def get_temperatures():
	args = request.args
	lat = args.get('lat')
	lon = args.get('lon')
	fromDate = args.get('from')
	toDate = args.get('until')
	params = []
	conditions = []
	# Construiesc clauza folosind parametrii de request
	if lat:
		conditions.append('o.latitudine=%s')
		params.append(lat)
	if lon:
		conditions.append('o.longitudine=%s')
		params.append(lon)
	if fromDate:
		conditions.append('TO_CHAR(t.timestamp, \'YYYY-MM-DD\') >= %s')
		params.append(fromDate)
	if toDate:
		conditions.append('TO_CHAR(t.timestamp, \'YYYY-MM-DD\') <= %s')
		params.append(toDate)
	#  Daca nu exista parametrii, clauza e nula
	#  Fac inner join pe id_oras
	clause = '' if len(conditions) == 0 else (' WHERE ' + ' AND '.join(conditions))
	try:
		query = ''' SELECT t.id, t.valoare::float, TO_CHAR(t.timestamp, 'YYYY-MM-DD')
					FROM Temperaturi t 
					INNER JOIN Orase o ON o.id=t.id_oras 
					%s ''' % clause
		curr.execute(query, params)

		table_data = curr.fetchall()
		fields = ['id', 'valoare','timestamp']
		result = process_get_response(fields, table_data)
	except psycopg2.Error: 
		return Response(status=404)

	return json_response(result,200)

@server.route("/api/temperatures/cities/<id_oras>", methods=["GET"])
def get_temperatures_by_city(id_oras=None):

	#  Fac inner join pe id_oras si caut si dupa oras folosind dupa id-ul primit
	query = ''' SELECT t.id, t.valoare::float, TO_CHAR(t.timestamp, 'YYYY-MM-DD')
					FROM Temperaturi t 
					INNER JOIN Orase o ON o.id=t.id_oras AND o.id=%s
					%s '''
	return get_temperatures_by_city_or_country(id_oras, query)
	

@server.route("/api/temperatures/countries/<id_tara>", methods=["GET"])
def get_temperatures_by_country(id_tara=None):

	#  Fac inner join pe id_oras si caut si dupa tara folosind id-ul primit
	query = ''' SELECT t.id, t.valoare::float, TO_CHAR(t.timestamp, 'YYYY-MM-DD')
					FROM Temperaturi t 
					INNER JOIN Orase o ON o.id=t.id_oras AND o.id_tara=%s
					%s '''
	return get_temperatures_by_city_or_country(id_tara, query)

@server.route("/api/temperatures/<id>", methods=["PUT"])
def modify_temperature(id=None):
	expected_types = [['int'],['int'], ['int' ,'float'],]
	expected_keys = ['id', 'idOras', 'valoare']
	query = 'UPDATE Temperaturi SET id_oras = %s, valoare = %s WHERE id = %s'
	return make_put_request(expected_types, expected_keys, query, id)

@server.route("/api/temperatures/<id>", methods=["DELETE"])
def delete_temperatures(id=None):
	query = 'DELETE FROM Temperaturi WHERE id = %s'
	return make_delete_request(query, id)


if __name__ == '__main__':
	server.run('0.0.0.0', debug=True)
