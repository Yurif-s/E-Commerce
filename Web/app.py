# Importando o Flask
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_cors import CORS
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user

# definindo a instância do Flask
app = Flask(__name__)
# Configuração para usar SQLAlchemy usando SQLite
app.config['SECRET_KEY'] = '762a44e2-e5c4-4c7c-9d00-1c66f75ce221'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
# Criando a instância de login
login_manager = LoginManager()
# Definindo a instância do objeto SQLAlchemy
db = SQLAlchemy(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
CORS(app)

# Modelagem
# User (id, username, password)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=True)

# Produto (id, name, price, description)
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)

# conexão com o banco de dados.
with app.app_context():
    #  cria as tabelas correspondentes no banco de dados
    db.create_all()
    # executa as alterações acumuladas na sessão e aplicá-las ao banco de dados real
    db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register_user', methods=['POST'])
def register_user():
    data = request.json
    if 'username' in data and 'password' in data:
        user = User(username=data['username'], password=data['password'])
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User added successfully'})
    return jsonify({'message': 'Invalid user data'}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json

    user = User.query.filter_by(username=data.get('username')).first()

    if user and data.get('password') == user.password:
        login_user(user)
        return jsonify({'message': 'Logged in successfully'})
    
    return jsonify({'message': ' Unauthorized. Invalid credentials'}), 401 # 

@app.route('/logout', methods=['POST'])
@login_required # Requer uma autenticação de usuário para ser executado, caso contrário terá um status code 405 (NOT ALLOWED)
def logout():
    logout_user()
    return jsonify({'message': 'Logout successfully'})


# Definir rota de adição de produto
@app.route('/api/products/add', methods=['POST'])
@login_required
def add_product():
    data = request.json
    if 'name' in data and 'price' in data:
        product = Product(name=data['name'], price=data['price'],description=data.get('description', ''))
        db.session.add(product)
        db.session.commit()
        return jsonify({'message': 'Product added successfully'})
    return jsonify({'message': 'Invalid product data'}), 400

@app.route('/api/products/delete/<int:product_id>', methods=['DELETE'])
@login_required
def delete_produto(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully'})
    return jsonify({'message': 'Product Not Found'}), 404

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product_details(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'description': product.description
        })
    return jsonify({'message': 'Product Not Found'}), 404

@app.route('/api/products/update/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product Not Found'}), 404
    
    data = request.json
    if 'name' in data:
        product.name = data['name']
    if 'price' in data:
        product.price = data['price']
    if 'description' in data:
        product.description = data['description']
    db.session.commit()
    return jsonify({'message': 'Product Updated Successfully'}), 200

@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    product_list = []
    for product in products:
        product_data = {
            'id': product.id,
            'name': product.name,
            'price': product.price
        }
        product_list.append(product_data)
        
    return jsonify(product_list)

# Definir uma rota raiz (pag inicial) e a função que será executada ao requisitar
@app.route('/')
# Definir as funções do site
def index():
    return render_template('index.html')

if __name__ == '__main__': 
    app.run(debug=True)