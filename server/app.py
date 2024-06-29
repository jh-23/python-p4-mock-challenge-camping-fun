#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request, session
import os
from sqlalchemy.exc import IntegrityError


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

api = Api(app)
migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

class Campers(Resource):
    
    def get(self):
        
        camper_list = [camper.to_dict(only=('id', 'name', 'age')) for camper in Camper.query.all()]
        
        response = make_response(
            camper_list,
            200
        )
        
        return response
    
    def post(self):
        
        json = request.get_json()
        
        try:
            new_camper = Camper(
                name = json.get('name'),
                age = json.get('age')
            )
            
            db.session.add(new_camper)
            db.session.commit()
        
            response_dict = new_camper.to_dict()
        
            response = make_response(
                response_dict,
                201
            )
        
            return response
        
        except ValueError:
            return {"errors": ["validation errors"]}, 400

    
api.add_resource(Campers, '/campers')

class CampersByID(Resource):
    
    def get(self, id):
        
        camper = Camper.query.filter(Camper.id == id).first()
        
        if camper:
            camper_dict = camper.to_dict(only=('id', 'name', 'age', 'signups'))
            response = make_response(
                camper_dict,
                200
            )
        
        else:
            response = make_response(
                {"error": "Camper not found"},
                404
            )
        
        return response
    
    def patch(self, id):
        
        json = request.get_json()
        
        camper = Camper.query.filter(Camper.id == id).first()
        
        try:
            if camper:
                for attr in json:
                    setattr(camper, attr, json[attr])
            
                db.session.add(camper)
                db.session.commit()
        
                response = make_response(
                    camper.to_dict(),
                    202
                )
            
            else:
                response = make_response(
                    {"error": "Camper not found"},
                    404
                )
        
            return response

        except ValueError:
            return {"errors": ["validation errors"]}, 400
        
api.add_resource(CampersByID, '/campers/<int:id>')

class Activities(Resource):
    
    def get(self):
        
        activity_list = [activity.to_dict(only=('id', 'name', 'difficulty')) for activity in Activity.query.all()]
        
        response = make_response(
            activity_list,
            200
        )
        
        return response

api.add_resource(Activities, '/activities')

class ActivityByID(Resource):
    
    def delete(self, id):
        
        activity = Activity.query.filter(Activity.id == id).first()
        
        if activity:
            db.session.delete(activity)
            db.session.commit()
        
            response = make_response(
                {}, 
                204
            )
        
        else:
            response = make_response(
                {"error": "Activity not found"},
                404
            )
            
        return response
    
api.add_resource(ActivityByID, '/activities/<int:id>')

class Signups(Resource):
    
    def post(self):
        
        json = request.get_json()
        
        try:
            new_signup = Signup(
                camper_id = json.get('camper_id'),
                activity_id = json.get('activity_id'),
                time = json.get('time')
            )
            
            db.session.add(new_signup)
            db.session.commit()
            
            response_dict = new_signup.to_dict(only=('id', 'camper_id', 'activity_id', 'time', 'activity', 'camper'))
            
            response = make_response(
                response_dict,
                201
            )
            
            return response
            
        except ValueError:
            return {"errors": ["validation errors"]}, 400

api.add_resource(Signups, '/signups')
        
if __name__ == '__main__':
    app.run(port=7777, debug=True)
