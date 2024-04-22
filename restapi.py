from flask import Flask, request, jsonify
import redis

app = Flask(__name__)
r = redis.Redis(host='localhost', port=6379, db=0)

# Endpoint para obtener todas las recetas
@app.route('/recipes', methods=['GET'])
def get_recipes():
    recipe_keys = r.keys('recipe:*')
    recipes = []

    for key in recipe_keys:
        recipe_data = r.hgetall(key)
        decoded_recipe = {
            'id': int(key.decode().split(':')[1]),  # Obtener el ID de la clave de Redis
            'name': recipe_data[b'name'].decode(),
            'ingredients': recipe_data[b'ingredients'].decode(),
            'steps': recipe_data[b'steps'].decode()
        }
        recipes.append(decoded_recipe)

    return jsonify(recipes)

# Endpoint para obtener una receta por ID
@app.route('/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    recipe_key = f'recipe:{recipe_id}'
    recipe_data = r.hgetall(recipe_key)
    if recipe_data:
        recipe = {
            'id': recipe_id,
            'name': recipe_data[b'name'].decode(),
            'ingredients': recipe_data[b'ingredients'].decode(),
            'steps': recipe_data[b'steps'].decode()
        }
        return jsonify(recipe)
    else:
        return jsonify({'message': 'Receta no encontrada'}), 404

# Endpoint para agregar una nueva receta
@app.route('/recipes', methods=['POST'])
def add_recipe():
    data = request.json
    name = data.get('name')
    ingredients = data.get('ingredients')
    steps = data.get('steps')

    if not (name and ingredients and steps):
        return jsonify({'error': 'Faltan campos requeridos'}), 400

    recipe_id = r.incr('recipe_id')
    recipe_key = f'recipe:{recipe_id}'
    recipe_data = {
        'name': name,
        'ingredients': ingredients,
        'steps': steps
    }
    for field, value in recipe_data.items():
        r.hset(recipe_key, field, value)

    return jsonify({'message': 'Receta agregada correctamente', 'id': recipe_id}), 201

# Otros endpoints como actualizar y eliminar recetas se pueden agregar de manera similar

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
