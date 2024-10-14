#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response, abort
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)


class Plants(Resource):

    def get(self):
        plants = [plant.to_dict() for plant in Plant.query.all()]
        return make_response(jsonify(plants), 200)

    def post(self):
        data = request.get_json()

        new_plant = Plant(
            name=data['name'],
            image=data['image'],
            price=data['price'],
        )

        db.session.add(new_plant)
        db.session.commit()

        return make_response(new_plant.to_dict(), 201)


api.add_resource(Plants, '/plants')


class PlantByID(Resource):

    def get(self, id):
        plant = Plant.query.filter_by(id=id).first().to_dict()
        return make_response(jsonify(plant), 200)


api.add_resource(PlantByID, '/plants/<int:id>')

# PATCH /plants/<id>: Update plant's 'is_in_stock' status
@app.route('/plants/<int:id>', methods=['PATCH'])
def update_plant(id):
    plant = db.session.get(Plant, id)  # Fetch plant using Session.get()
    
    if not plant:
        abort(404, description="Plant not found")
    
    data = request.get_json()
    
    # Update only the 'is_in_stock' attribute (can expand to other fields if needed)
    if 'is_in_stock' in data:
        plant.is_in_stock = data['is_in_stock']
    
    db.session.commit()
    
    # Return the updated plant as JSON
    return jsonify({
        "id": plant.id,
        "name": plant.name,
        "image": plant.image,
        "price": plant.price,
        "is_in_stock": plant.is_in_stock
    })

@app.route('/plants/<int:id>', methods=['DELETE'])
def delete_plant(id):
    plant = db.session.get(Plant, id)  # Fetch plant using Session.get()
    
    if not plant:
        abort(404, description="Plant not found")
    
    db.session.delete(plant)
    db.session.commit()
    
    # Return an empty string and status code 204 (No Content)
    return '', 204


if __name__ == '__main__':
    app.run(port=5555, debug=True)
