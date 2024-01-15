from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_swagger_ui import get_swaggerui_blueprint
import json

app = Flask(__name__)

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "File Management API"},
)

app.register_blueprint(swaggerui_blueprint)

app.config['MONGO_URI'] = 'mongodb://localhost:27017/file_management'
mongo = PyMongo(app)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file:
        try:
            # Parse JSON content from the uploaded file
            json_data = json.loads(file.read().decode('utf-8'))

            # Check if 'countries' field is present in the JSON
            if 'countries' not in json_data:
                return jsonify({'message': 'No "countries" field in the JSON file'}), 400

            # Insert each country as a separate document in MongoDB
            country_data = mongo.db.countries
            country_data.insert_many(json_data['countries'])

            return jsonify({'message': 'File uploaded and data inserted into MongoDB successfully'})
        except json.JSONDecodeError as e:
            return jsonify({'message': 'Error decoding JSON: {}'.format(str(e))}), 400
        except Exception as e:
            return jsonify({'message': 'Error processing the file: {}'.format(str(e))}), 500

@app.route('/countries', methods=['GET'])
def get_countries():
    country_data = mongo.db.countries.find({}, {'_id': 0})
    
    countries_list = list(country_data)
    
    if countries_list:
        return jsonify({'countries': countries_list})
    
    return jsonify({'message': 'No country data available'}), 404

if __name__ == '__main__':
    app.run(debug=True)
