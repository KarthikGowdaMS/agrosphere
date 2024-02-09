from dotenv import load_dotenv
import os
from flask import Flask, render_template,redirect,url_for,request
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user,logout_user
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'thisismylittlesecret'
load_dotenv()

db_url = os.getenv('db_url')

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
db = SQLAlchemy(app)

class User(UserMixin):
    pass
    
users={'username':'karthik','password':'karthik'}
@login_manager.user_loader
def user_loader(username):
    
    if username not in users['username']:
        return

    user = User()
    user.id = username
    return user

# Register

# login
@app.route('/login',methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == users['username'] and password == users['password']:
        user = User()
        user.id = username
        login_user(user)
        return redirect(url_for('crop'))
    return "Invalid username or password"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Models
class Crop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    weather_condition = db.Column(db.String(100))

class Farmer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_details = db.Column(db.String(100), nullable=False)
    land_size = db.Column(db.String(100), nullable=False)
    crop_performance = db.Column(db.String(100), nullable=False)
    
class Field(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'), nullable=False)
    size = db.Column(db.String(100), nullable=False)
    soil_type = db.Column(db.String(100), nullable=False)
    
class Harvestandyield(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    field_id = db.Column(db.Integer, db.ForeignKey('field.id'), nullable=False)
    farmer_id = db.Column(db.Integer,db.ForeignKey('farmer.id') ,nullable=False)
    crop_id = db.Column(db.Integer,db.ForeignKey('crop.id') ,nullable=False)
    
class Marketplace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'), nullable=False)
    price = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.String(100), nullable=False)


@app.route('/')
def index():
    return render_template('index.html')



# Crops
# login required for this route


@app.route('/crops')
@login_required
def crop():
    crops = Crop.query.all()
    return render_template('crop.html', crops=crops)

@app.route('/crops/create',methods=['POST'])
def create_crop():
    # get details from the post request
    crop_id= request.form.get('id')
    crop_name = request.form.get('name')
    crop_type = request.form.get('type')
    weather_condition = request.form.get('weather_condition')
    
    crop_data = Crop(id=crop_id, name=crop_name, type=crop_type, weather_condition=weather_condition)
    db.session.add(crop_data)
    db.session.commit()
    return redirect(url_for('crops'))
    # return "Form submitted", 200
    
@app.route('/crops/edit/<int:id>',methods=['POST'])
def edit_crop(id):
    # get details from the post request
    crop = Crop.query.get(id)
    crop.name = request.form.get('name')
    crop.type = request.form.get('type')
    crop.weather_condition = request.form.get('weather_condition')
    
    db.session.commit()
    # return redirect(url_for('crops'))
    return "Form submitted", 200

@app.route('/crops/delete/<int:id>',methods=['POST'])
def delete_crop(id):
    # get details from the post request
    crop = Crop.query.get(id)
    db.session.delete(crop)
    db.session.commit()
    return 'Crop Deleted', 200 


# farmers

@app.route('/farmers')
def farmer():
    farmers = Farmer.query.all()
    return render_template('index.html', farmers=farmers)

@app.route('/farmers/create',methods=['POST'])
def create_farmer():
    # get details from the post request
    farmer_id= request.form.get('id')
    farmer_name = request.form.get('name')
    contact_details = request.form.get('contact_details')
    land_size = request.form.get('land_size')
    crop_performance = request.form.get('crop_performance')
    
    farmer_data = Farmer(id=farmer_id, name=farmer_name, contact_details=contact_details, land_size=land_size, crop_performance=crop_performance)
    db.session.add(farmer_data)
    db.session.commit()
    # return redirect(url_for('farmers'))
    return "Form submitted", 200

@app.route('/farmers/edit/<int:id>',methods=['POST'])
def edit_farmer(id):
    # get details from the post request
    farmer = Farmer.query.get(id)
    farmer.name = request.form.get('name')
    farmer.contact_details = request.form.get('contact_details')
    farmer.land_size = request.form.get('land_size')
    farmer.crop_performance = request.form.get('crop_performance')
    
    db.session.commit()
    # return redirect(url_for('farmers'))
    return "Form submitted", 200

@app.route('/farmers/delete/<int:id>',methods=['POST'])
def delete_farmer(id):
    # get details from the post request
    farmer = Farmer.query.get(id)
    db.session.delete(farmer)
    db.session.commit()
    return 'Farmer Deleted', 200


# fields

@app.route('/fields')
def field():
    fields = Field.query.all()
    return render_template('index.html', fields=fields)

@app.route('/fields/create',methods=['POST'])
def create_field():
    # get details from the post request
    field_id= request.form.get('id')
    farmer_id = request.form.get('farmer_id')
    crop_id = request.form.get('crop_id')
    size = request.form.get('size')
    soil_type = request.form.get('soil_type')
    
    field_data = Field(id=field_id, farmer_id=farmer_id, crop_id=crop_id, size=size, soil_type=soil_type)
    db.session.add(field_data)
    db.session.commit()
    return "Form submitted", 200

@app.route('/fields/edit/<int:id>',methods=['POST'])
def edit_field(id):
    # get details from the post request
    field = Field.query.get(id)
    field.farmer_id = request.form.get('farmer_id')
    field.crop_id = request.form.get('crop_id')
    field.size = request.form.get('size')
    field.soil_type = request.form.get('soil_type')
    
    db.session.commit()
    return "Form submitted", 200

@app.route('/fields/delete/<int:id>',methods=['POST'])
def delete_field(id):
    # get details from the post request
    field = Field.query.get(id)
    db.session.delete(field)
    db.session.commit()
    return 'Field Deleted', 200


# harvests

@app.route('/harvests')
def harvest():
    harvests = Harvestandyield.query.all()
    return render_template('index.html', harvests=harvests)

@app.route('/harvests/create',methods=['POST'])
def create_harvest():
    # get details from the post request
    harvest_id= request.form.get('id')
    field_id = request.form.get('field_id')
    farmer_id = request.form.get('farmer_id')
    crop_id = request.form.get('crop_id')
    
    harvest_data = Harvestandyield(id=harvest_id, field_id=field_id, farmer_id=farmer_id, crop_id=crop_id)
    db.session.add(harvest_data)
    db.session.commit()
    return "Form submitted", 200

@app.route('/harvests/edit/<int:id>',methods=['POST'])
def edit_harvest(id):
    # get details from the post request
    harvest = Harvestandyield.query.get(id)
    harvest.field_id = request.form.get('field_id')
    harvest.farmer_id = request.form.get('farmer_id')
    harvest.crop_id = request.form.get('crop_id')
    
    db.session.commit()
    return "Form submitted", 200

@app.route('/harvests/delete/<int:id>',methods=['POST'])
def delete_harvest(id):
    # get details from the post request
    harvest = Harvestandyield.query.get(id)
    db.session.delete(harvest)
    db.session.commit()
    return 'Harvest Deleted', 200


# markets

@app.route('/markets')
def market():
    markets = Marketplace.query.all()
    return render_template('index.html', markets=markets)

@app.route('/markets/create',methods=['POST'])
def create_market():
    # get details from the post request
    market_id= request.form.get('id')
    farmer_id = request.form.get('farmer_id')
    crop_id = request.form.get('crop_id')
    price = request.form.get('price')
    quantity = request.form.get('quantity')
    
    market_data = Marketplace(id=market_id, farmer_id=farmer_id, crop_id=crop_id, price=price, quantity=quantity)
    db.session.add(market_data)
    db.session.commit()
    return "Form submitted", 200

@app.route('/markets/edit/<int:id>',methods=['POST'])
def edit_market(id):
    # get details from the post request
    market = Marketplace.query.get(id)
    market.farmer_id = request.form.get('farmer_id')
    market.crop_id = request.form.get('crop_id')
    market.price = request.form.get('price')
    market.quantity = request.form.get('quantity')
    
    db.session.commit()
    return "Form submitted", 200

@app.route('/markets/delete/<int:id>',methods=['POST'])
def delete_market(id):
    # get details from the post request
    market = Marketplace.query.get(id)
    db.session.delete(market)
    db.session.commit()
    return 'Market Deleted', 200



if __name__ == '__main__':
    app.run(debug=True)