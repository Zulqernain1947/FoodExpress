from flask import request, Response, jsonify
from flask_restful import Resource
from database.models import Restaurant

class restaurantApi(Resource):
    def get(self):
        try:
            data=Restaurant.objects().to_json()
            return Response(data,mimetype="application/json",status=200)
        except Exception as e:
            return Response(status=404)