from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.json'  # Our API url (can of course be a local resource)

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "student"
    },
    # oauth_config={  # OAuth config. See https://github.com/swagger-api/swagger-ui#oauth2-configuration .
    #    'clientId': "your-client-id",
    #    'clientSecret': "your-client-secret-if-required",
    #    'realm': "your-realms",
    #    'appName': "your-app-name",
    #    'scopeSeparator': " ",
    #    'additionalQueryStringParams': {'test': "hello"}
    # }
)

app.register_blueprint(swaggerui_blueprint)

app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/school'
mongo = PyMongo(app)

@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()

    # Generate Student Id sequentially
    last_student = mongo.db.students.find_one({}, sort=[("student_id", -1)])
    new_student_id = 'ST0001' if not last_student else 'ST{:04d}'.format(int(last_student['student_id'][2:]) + 1)

    student = {
        'student_id': new_student_id,
        'name': data['name'],
        'age': data['age'],
        'dob': data['dob'],
        'class': data['class'],
        'div': data['div'],
        'guardian_name': data['guardian_name'],
        'address': data['address']
    }

    mongo.db.students.insert_one(student)
    return jsonify({'message': 'Student added successfully', 'student_id': new_student_id})

@app.route('/students', methods=['GET'])
def get_all_students():
    students = list(mongo.db.students.find({}, {'_id': 0}))
    return jsonify({'students': students})

@app.route('/students/<student_id>', methods=['GET'])
def get_student(student_id):
    student = mongo.db.students.find_one({'student_id': student_id}, {'_id': 0})
    if student:
        return jsonify({'student': student})
    return jsonify({'message': 'Student not found'}), 404

@app.route('/students/<student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.get_json()
    updated_student = {
        'name': data['name'],
        'age': data['age'],
        'dob': data['dob'],
        'class': data['class'],
        'div': data['div'],
        'guardian_name': data['guardian_name'],
        'address': data['address']
    }

    result = mongo.db.students.update_one({'student_id': student_id}, {'$set': updated_student})
    if result.modified_count > 0:
        return jsonify({'message': 'Student updated successfully'})
    return jsonify({'message': 'Student not found'}), 404

@app.route('/students/search/<name>', methods=['GET'])
def search_students(name):
    students = list(mongo.db.students.find({'name': {'$regex': name, '$options': 'i'}}, {'_id': 0}))
    return jsonify({'students': students})

@app.route('/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    result = mongo.db.students.delete_one({'student_id': student_id})
    if result.deleted_count > 0:
        return jsonify({'message': 'Student deleted successfully'})
    return jsonify({'message': 'Student not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
