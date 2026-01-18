#!/usr/bin/env python3

from flask import request, session, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    
    def post(self):
        try:
            json = request.get_json()
            
            user = User(
                username=json.get('username'),
                image_url=json.get('image_url'),
                bio=json.get('bio')
            )
            
            user.password_hash = json['password']
            
            db.session.add(user)
            db.session.commit()
            
            session['user_id'] = user.id
            
            return user.to_dict(), 201
            
        except ValueError as e:
            return {'error': str(e)}, 422
        except IntegrityError:
            db.session.rollback()
            return {'error': 'Username must be unique'}, 422

class CheckSession(Resource):
    
    def get(self):
        user_id = session.get('user_id')
        
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            if user:
                return user.to_dict(), 200
        
        return {}, 401

class Login(Resource):
    
    def post(self):
        json = request.get_json()
        username = json.get('username')
        password = json.get('password')
        
        user = User.query.filter(User.username == username).first()
        
        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict(), 200
        
        return {'error': 'Invalid username or password'}, 401

class Logout(Resource):
    
    def delete(self):
        user_id = session.get('user_id')
        
        if not user_id:
            return {'error': 'Unauthorized'}, 401
        
        session['user_id'] = None
        return {}, 204

class RecipeIndex(Resource):
    
    def get(self):
        user_id = session.get('user_id')
        
        if not user_id:
            return {'error': 'Unauthorized'}, 401
        
        recipes = Recipe.query.filter(Recipe.user_id == user_id).all()
        return [recipe.to_dict() for recipe in recipes], 200
    
    def post(self):
        user_id = session.get('user_id')
        
        if not user_id:
            return {'error': 'Unauthorized'}, 401
        
        try:
            json = request.get_json()
            
            recipe = Recipe(
                title=json.get('title'),
                instructions=json.get('instructions'),
                minutes_to_complete=json.get('minutes_to_complete'),
                user_id=user_id
            )
            
            db.session.add(recipe)
            db.session.commit()
            
            return recipe.to_dict(), 201
            
        except ValueError as e:
            return {'error': str(e)}, 422

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)