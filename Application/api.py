from flask_restful import Api
from app import flask_app
api = Api(flask_app)


api.add_resource(User_API, '/api/v1/user', endpoint='user')