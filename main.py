import bottle
import sqlite3
import json
import uuid
from contextlib import closing

app = application = bottle.Bottle()

MINIMAL_CORS = {
	'Content-type' : 'application/json',
	'Access-Control-Allow-Origin' : 'localhost:8098',
}

DB_PATH = '/mnt/sdcard/CoberturaTerritorial.db'

@app.route("/<filepath:re:.*\.(css|js)>", method='GET')
def asset_files(filepath):
	return bottle.static_file(filepath, root='./static/')

@app.error(404)
def error404(error):
	return 'Nothing here, sorry'

@app.route('/COBERTURA_TERRITORIAL/v1/', method='GET')
def get_regions():
	try:
		with sqlite3.connect(DB_PATH) as connection:
			with closing(connection.cursor()) as cursor:
				cursor.execute("SELECT UPPER([id]) AS id, UPPER([región]) AS nm FROM [Cobertura Territorial] WHERE SUBSTR([id], 1, 2)='08' AND [distrito] IS NULL AND [provincia] IS NULL", ())
				cursor.row_factory = sqlite3.Row
				ds_ = [dict(r) for r in cursor.fetchall()]
				return bottle.HTTPResponse(body=json.dumps({'data': ds_}), status=200, headers=MINIMAL_CORS)
	except sqlite3.OperationalError as e:
		return bottle.HTTPResponse(body=json.dumps({'msg': str(e)}), status=500)

@app.route('/COBERTURA_TERRITORIAL/v1/provincia/', method='GET')
def get_provinces():
	try:
		with sqlite3.connect(DB_PATH) as connection:
			with closing(connection.cursor()) as cursor:
				cursor.execute("SELECT DISTINCT UPPER([id]) AS id, UPPER([provincia]) AS nm FROM [Cobertura Territorial] WHERE SUBSTR([id], 1, 2)='08' AND [distrito] IS NULL AND [provincia] IS NOT NULL", ())
				cursor.row_factory = sqlite3.Row
				ds_ = [dict(r) for r in cursor.fetchall()]
				return bottle.HTTPResponse(body=json.dumps({'data': ds_}), status=200, headers=MINIMAL_CORS)
	except sqlite3.OperationalError as e:
		return bottle.HTTPResponse(body=json.dumps({'msg': str(e)}), status=500)

@app.route('/COBERTURA_TERRITORIAL/v1/distrito/<id>/', method='GET')
def get_districts(id:str):
	try:
		with sqlite3.connect(DB_PATH) as connection:
			with closing(connection.cursor()) as cursor:
				cursor.execute("SELECT DISTINCT UPPER([id]) AS id, UPPER([distrito]) AS nm FROM [Cobertura Territorial] WHERE SUBSTR([id], 1, 2)='08' AND SUBSTR([id], 3, 2)=? AND [distrito] IS NOT NULL", (id, ))
				cursor.row_factory = sqlite3.Row
				ds_ = [dict(r) for r in cursor.fetchall()]
				return bottle.HTTPResponse(body=json.dumps({'data': ds_}), status=200, headers=MINIMAL_CORS)
	except sqlite3.OperationalError as e:
		return bottle.HTTPResponse(body=json.dumps({'msg': str(e)}), status=500)

# openAPI v.3.x
@app.route('/COBERTURA_TERRITORIAL/v1/oa/', method='GET')
def get_oa():
	_paths_ = {}
	for route_ in app.routes:
		_paths_[str(route_.rule)] = { route_.method : { 'summary' : '', 'responses': { '200' : { 'description' : 'success' }  } }}
	__doc__ = { 'openapi' : '3.0.0', 'info' : { 'title' : 'Cobertura Territorial API', 'summary': 'Cobertura Territorial - CREE Cusco', 'description': 'Circunscribir a un espacio geográfico, aspectos como colegios, unidades de gestión, etc.', 'contact': { 'name' : 'Luis Carrillo Gutiérrez', 'email' : '...@gmail.com'}, 'version' : '0.0.1' }, 'paths' : _paths_ }
	return bottle.HTTPResponse(body=json.dumps(__doc__), status=200, headers=MINIMAL_CORS)

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=8098, reloader=True, debug=True)