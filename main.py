import json
from flask import Flask, jsonify, request, abort
from flask_httpauth import HTTPBasicAuth

# Ініціалізація додатка
app = Flask(__name__)
auth = HTTPBasicAuth()

# Змінні для зберігання користувачів і каталогу
users = {}
catalog = {}

# Шляхи до файлів
users_file = 'users.json'
catalog_file = 'catalog.json'

@auth.get_password
def get_password(username):
    print(f"Authentication attempt for username: {username}")  # Додано для перевірки
    return users.get(username)

# Завантаження даних користувачів із файлу
def load_users_from_file(filename):
    global users
    try:
        with open(filename, 'r') as file:
            users = json.load(file)
    except FileNotFoundError:
        print(f"Warning: File {filename} not found. Starting with empty users.")
        users = {}
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON in {filename}. Starting with empty users.")
        users = {}


# Завантаження каталогу товарів із файлу
def load_catalog_from_file(filename):
    global catalog
    try:
        with open(filename, 'r') as file:
            catalog = json.load(file)
    except FileNotFoundError:
        print(f"Warning: File {filename} not found. Starting with empty catalog.")
        catalog = {}
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON in {filename}. Starting with empty catalog.")
        catalog = {}


# Збереження користувачів у файл
def save_users_to_file(filename):
    try:
        with open(filename, 'w') as file:
            json.dump(users, file, indent=4)
    except Exception as e:
        print(f"Error: Failed to save users to {filename}. Reason: {e}")


# Збереження каталогу товарів у файл
def save_catalog_to_file(filename):
    try:
        with open(filename, 'w') as file:
            json.dump(catalog, file, indent=4)
    except Exception as e:
        print(f"Error: Failed to save catalog to {filename}. Reason: {e}")


# Завантаження даних при запуску програми
load_users_from_file(users_file)
load_catalog_from_file(catalog_file)


# Аутентифікація
@auth.get_password
def get_password(username):
    return users.get(username)


@auth.error_handler
def unauthorized():
    return jsonify({"error": "Unauthorized access"}), 401


# Ендпоінт: GET і POST для /items
@app.route('/items', methods=['GET', 'POST'])
@auth.login_required
def manage_items():
    if request.method == 'GET':
        return jsonify({"catalog": catalog})
    elif request.method == 'POST':
        # Отримання даних із запиту
        data = request.json
        if not data or "id" not in data or "name" not in data or "price" not in data:
            abort(400, "Invalid data")
        # Додавання товару
        item_id = str(data["id"])  # Перетворюємо ID в строку для JSON-сумісності
        if item_id in catalog:
            abort(400, "Item already exists")
        catalog[item_id] = {
            "name": data["name"],
            "price": data["price"]
        }
        save_catalog_to_file(catalog_file)  # Збереження каталогу
        return jsonify({"message": "Item added", "item": catalog[item_id]}), 201


# Ендпоінт: GET, PUT, DELETE для /items/<id>
@app.route('/items/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def manage_item(item_id):
    item_id = str(item_id)  # Перетворюємо ID в строку для JSON-сумісності
    if item_id not in catalog:
        abort(404, "Item not found")

    if request.method == 'GET':
        return jsonify({"item": catalog[item_id]})
    elif request.method == 'PUT':
        data = request.json
        if not data or "name" not in data or "price" not in data:
            abort(400, "Invalid data")
        # Оновлення товару
        catalog[item_id] = {
            "name": data["name"],
            "price": data["price"]
        }
        save_catalog_to_file(catalog_file)  # Збереження каталогу
        return jsonify({"message": "Item updated", "item": catalog[item_id]})
    elif request.method == 'DELETE':
        # Видалення товару
        deleted_item = catalog.pop(item_id)
        save_catalog_to_file(catalog_file)  # Збереження каталогу
        return jsonify({"message": "Item deleted", "item": deleted_item})


# Запуск додатка
if __name__ == '__main__':
    app.run(debug=True)
