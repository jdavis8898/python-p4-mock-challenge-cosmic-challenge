#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''

class Scientists(Resource):

    def get(self):
        scientists = [scientist.to_dict(rules=("-missions",))
                        for scientist in Scientist.query.all()]
        
        return make_response(scientists, 200)
    
    def post(self):

        form_data = request.get_json()

        try:
            new_scientist = Scientist(name=form_data["name"], field_of_study=form_data["field_of_study"])
            
            db.session.add(new_scientist)
            db.session.commit()

            return make_response(new_scientist.to_dict(), 201)
        
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)

api.add_resource(Scientists, "/scientists")

### Alternate to above if not using RESTful ###
# @app.route("/scientists", methods = ["GET", "POST"])
# def scientists():
    
#     if request.method == "GET":
#         scientists = Scientist.query.all()
        
#         scientists_dict = [scientist.to_dict(rules=("-missions",)) for scientist in scientists]

#         response = make_response(
#             scientists_dict,
#             200
#         )
    
#     elif request.method == "POST":

#         try:
#             form_data = request.get_json()

#             new_scientist = Scientist(
#                 name = form_data['name'],
#                 field_of_study = form_data['field_of_study']
#             )

#             db.session.add(new_scientist)
#             db.session.commit()

#             response = make_response(
#                 new_scientist.to_dict(),
#                 201
#             )

#         except ValueError:
#             response= make_response(
#                 {"errors": ["validation errors"]},
#                 400
#             )

#     return response
################################################

class ScientistById(Resource):

    def get(self, id):
        scientist = Scientist.query.filter(Scientist.id==id).first()

        if scientist:
            body = scientist.to_dict()
            status = 200
        
        else:
            body = {"error": "Scientist not found"}
            status = 404
        
        return make_response(body, status)
    
    def patch(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()


        if not scientist:
            return make_response({'error': 'Scientist not found'}, 404)

        form_data = request.get_json()

        try:
            for attr in form_data:
                setattr(scientist, attr, form_data[attr])

            db.session.commit()

            scientist_dict = scientist.to_dict(rules=("-missions",))

            return make_response(scientist_dict, 202)

        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)
    
    def delete(self, id):
        scientist = Scientist.query.filter(Scientist.id==id).first()

        if scientist:
            db.session.delete(scientist)
            db.session.commit()
            body = {}
            status = 204
        
        else:
            body = {"error": "Scientist not found"}
            status = 404
        
        return make_response(body, status)


api.add_resource(ScientistById, "/scientists/<int:id>")

### Alternate to above if not using RESTful ###
# @app.route("/scientists/<int:id>", methods = ["GET", "DELETE", "PATCH"])
# def scientist_by_id(id):
#     scientist = Scientist.query.filter(Scientist.id == id).first()

#     if scientist:
#         if request.method == "GET":

#             response = make_response(
#                 scientist.to_dict(),
#                 200
#             )
#         elif request.method == "DELETE":
#             ### If did not setup cascade delete in models ###
#             assoc_missions = Mission.query.filter(Mission.scientist_id == id).all()

#             for assoc_mission in assoc_missions:
#                 db.session.delete(assoc_mission)
#             #################################################

#             db.session.delete(scientist)
#             db.session.commit()

#             response = make_response(
#                 {},
#                 204
#             )
        
#         elif request.method == "PATCH":
#             try:
#                 form_data = request.get_json()

#                 for attr in form_data:
#                     setattr(scientist, attr, form_data[attr])

#                 db.session.commit()

#                 response = make_response(
#                     scientist.to_dict(),
#                     202
#                 )

#             except ValueError:
#                 response = make_response(
#                     {"errors": ["validation errors"]},
#                     400
#                 )

#     else:
#         response = make_response(
#             {"error": "Scientist not found"},
#             404
#         )
    
#     return response
################################################

class Planets(Resource):

    def get(self):
        planets = [planet.to_dict(rules=('-missions',))
                   for planet in Planet.query.all()]

        return make_response(planets, 200)

api.add_resource(Planets, "/planets")

### Alternate to above if not using RESTful ###
# @app.route("/planets", mehtods = ["GET"])
# def planets():
#     planets = Planet.query.all()
    
#     planets_dict = [planet.to_dict(rules=("-mission",)) for planet in planets]

#     response = make_response(
#         planets_dict,
#         200
#     )

#     return response
################################################

class Missions(Resource):

    def post(self):

        form_data = request.get_json()

        try:
            mission = Mission(
            name=form_data["name"],
            scientist_id=form_data["scientist_id"],
            planet_id=form_data["planet_id"]
            )

            db.session.add(mission)
            db.session.commit()

            return make_response(mission.to_dict(), 201)

        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(Missions, "/missions")

### Alternate to above if not using RESTful ###
# @app.route("missions", methods = ["POST"])
# def missions():
#     try:
#         form_data = request.get_json()

#         new_mission = Mission(
#             name = form_data['name'],
#             planet_id = form_data['planet_id'],
#             scientist_id = form_data['scientist_id']
#         )

#         db.session.add(new_mission)
#         db.commit()

#         response = make_response(
#             new_mission.to_dict(),
#             201
#         )

#     except ValueError:
#         response = make_response(
#             {"errors": ["validation errors"]},
#             400
#         )
    
#     return response
################################################

if __name__ == '__main__':
    app.run(port=5555, debug=True)