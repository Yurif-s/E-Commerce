# Importando o Flask
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# definindo a instância do Flask
app = Flask(__name__)
# Configuração para usar SQLAlchemy usando SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
# Definindo a instância do objeto SQLAlchemy
db = SQLAlchemy(app)

# Modelagem
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

# Definir rota de adição de produto
@app.route('/api/products/add', methods=['POST'])
def adicionarProduto():
    data = request.json
    if 'name' in data and 'price' in data:
        product = Product(name=data['name'], price=data['price'],description=data.get('description', ''))
        db.session.add(product)
        db.session.commit()
        return jsonify({'message': 'Product added successfully'})
    return jsonify({'message': 'Invalid product data'}), 400

@app.route('/api/products/delete/<int:product_id>', methods=['DELETE'])
def deleteProduto(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully'})
    return jsonify({'message': 'Product Not Found'}), 404

@app.route('/api/products/<int:product_id>', methods=['GET'])
def getProductDetails(product_id):
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
def updateProduct(product_id):
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

# Definir uma rota raiz (pag inicial) e a função que será executada ao requisitar
@app.route('/')
# Definir as funções do site
def index():
    return render_template('index.html')

if __name__ == '__main__': 
    app.run(debug=True)