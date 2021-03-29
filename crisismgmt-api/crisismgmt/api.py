"""
api.py
- provides the API endpoints for consuming and producing
  REST requests and responses
"""

from flask import Blueprint, jsonify, request, make_response, current_app
from flask_cors import CORS, cross_origin
from datetime import datetime, timedelta
from sqlalchemy import exc
from functools import wraps
from .models import db, User
import jwt

api = Blueprint('api', __name__)

ODAPI_URL = 'http://127.0.0.1:8000/'

@api.route('/')
def index():
    response = { 'Status': "API is up and running!" }
    return make_response(jsonify(response), 200)


@api.route('/register', methods=('POST',))
def register():
    try:
        data = request.get_json()
        user = User(**data)
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({ 'message': e.args }), 500


@api.route('/login', methods=('POST',))
def login():
    data = request.get_json()
    user = User.authenticate(**data)

    if not user:
        return jsonify({ 'message': 'Invalid credentials', 'authenticated': False }), 401

    token = jwt.encode({
        'sub': user.email,
        'iat':str(datetime.utcnow()),
        'exp': str(datetime.utcnow() + timedelta(minutes=30))},
        current_app.config['SECRET_KEY'])
    student_id = User.query.filter_by(email=data['email']).first().user_id
    is_admin = User.query.filter_by(email=data['email']).first().is_admin
    return jsonify({ 'user_id': user_id , 'is_admin': is_admin, 'token': token.decode('UTF-8') }), 200

 

@api.route('/maps/filter', methods=('GET',))
def get_safe_locations():
    try:
        safe = []
        unsafe = []
        latitude = request.args.get('latitude', default=0, type=float)
        longitude = request.args.get('longitude', default=0, type=float)
        is_safe = request.args.get('is_safe', default=None, type=bool)
        not_safe = request.args.get('not_safe', default=None, type=bool)
        
        #Append latitude and longitude to array safe

        #Return array 
        payload = {'safe': safe.to_dict(), 'token': token.decode('UTF-8') };
        return jsonify(payload), 200; 
                   
  
# This is a decorator function which will be used to protect authentication-sensitive API endpoints
def token_required(f):
    @wraps(f)
    def _verify(*args, **kwargs):
        auth_headers = request.headers.get('Authorization', '').split()

        invalid_msg = {
            'message': 'Invalid token. Registeration and / or authentication required',
            'authenticated': False
        }
        expired_msg = {
            'message': 'Expired token. Reauthentication required.',
            'authenticated': False
        }

        if len(auth_headers) != 2:
            return jsonify(invalid_msg), 401

        try:
            token = auth_headers[1]
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
            user = User.query.filter_by(email=data['sub']).first()
            if not user:
                raise RuntimeError('User not found')
            return f(user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify(expired_msg), 401 # 401 is Unauthorized HTTP status code
        except (jwt.InvalidTokenError, Exception) as e:
            print(e)
            return jsonify(invalid_msg), 401

    return _verify
