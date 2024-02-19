from dotenv import load_dotenv
import os
from flask import Flask, render_template,redirect,url_for,request
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user,logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.orm import joinedload
from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


app = Flask(__name__,static_url_path='/static')
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'thisismylittlesecret'
load_dotenv()

password = os.getenv('password')

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://root:{password}@localhost:3306/agrosphere"
# app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://avnadmin:{password}@dbms-agm-karthikgowdams03-dbms-ams.a.aivencloud.com:15253/agrosphere"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(UserMixin):
    pass
    
@login_manager.user_loader
def user_loader(id):
    
    with db.engine.connect() as connection:
        query = text("SELECT * FROM farmer WHERE id = :id")
        result = connection.execute(query, {"id": id})
        farmer=result.first() 
        
        if farmer:
            user = User()
            user.id =farmer.id
            user.role=farmer.role
            user.name=farmer.name
            return user
    return None

# models

class Crop(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    weather_condition = db.Column(db.String(100))
    harvests = db.relationship('Harvestandyield', back_populates='crop', cascade='all, delete-orphan')

class Farmer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    land_size = db.Column(db.Float, nullable=False)
    crop_performance = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    fields = db.relationship('Field', backref='farmer', cascade='all, delete-orphan')
    harvests = db.relationship('Harvestandyield', back_populates='farmer', cascade='all, delete-orphan')
    markets = db.relationship('Marketplace', back_populates='farmer', cascade='all, delete-orphan')
    
    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True
    
class Field(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'), nullable=False)
    size = db.Column(db.Float, nullable=False)
    soil_type = db.Column(db.String(100), nullable=False)
    
class Harvestandyield(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    field_id = db.Column(db.Integer, db.ForeignKey('field.id'), nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    farmer = db.relationship('Farmer', back_populates='harvests')
    crop = db.relationship('Crop', back_populates='harvests')
    field = db.relationship('Field')
    
class Marketplace(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'), nullable=False)
    price = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    farmer = db.relationship('Farmer', back_populates='markets')
    crop = db.relationship('Crop')


# login
@app.route('/login',methods=['GET','POST'])
def login():
    
    if request.method=='POST':
        email = str(request.form.get('email'))
        password = str(request.form.get('password'))

        with db.engine.connect() as connection:
            query =  text("SELECT * FROM farmer WHERE email = :email AND password = :password")
            result = connection.execute(query, {"email": email, "password": password})
            farmer = result.first()

            print(farmer)
            if farmer:
                user=User()
                user.id=farmer.id
                user.role=farmer.role
                user.name=farmer.name
                # print(farmer.id)
                login_user(user)
                return redirect(url_for('home'))
            
        return "Invalid credentials"
    return render_template('login.html')


# Register
@app.route('/register',methods=['GET','POST'])
def register():
    
    if request.method=='POST':
        name = str(request.form.get('name'))
        email = str(request.form.get('email'))
        password = str(request.form.get('password'))
        # print(password)
        # try:
        #     with db.engine.connect() as connection:
        #         query = text("INSERT INTO agrosphere.farmer (name,email,password,land_size,crop_performance,role) VALUES (:name,:email,:password,:land_size,:crop_performance,:role)")
        #         connection.execute(query, {"name": name, "email": email, "password": password, "land_size":0, "crop_performance": '',"role":"user"})
        #         connection.commit()
        # except Exception as e:
        #     print(e)
        farmer_data=Farmer(name=name, email=email, password=password,land_size=0,crop_performance='',role='user')
        
        db.session.add(farmer_data)
        db.session.commit()
        
        farmer = Farmer.query.filter_by(email=email, password=password).first()
        print(farmer.id)
        user=User()
        user.id=farmer.id
        user.role=farmer.role
        user.name=farmer.name
        login_user(user)

        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/home')
def home():
    if current_user.is_authenticated:
        return render_template('home.html')
    return redirect(url_for('login'))


# Crops

@app.route('/crops')
def crop():
    if current_user.is_authenticated:
        crops = Crop.query.all()
        return render_template('crop.html', crops=crops)
    return redirect(url_for('login'))

@app.route('/crop/create',methods=['GET','POST'])
def create_crop():
    
    if current_user.is_authenticated:
        if current_user.role != 'admin':
            return render_template('forbidden.html')
        
        if request.method=='POST':
            
            crop_name = request.form.get('name')
            crop_type = request.form.get('type')
            weather_condition = request.form.get('weather_condition')
            
            crop_data = Crop(name=crop_name, type=crop_type, weather_condition=weather_condition)
            db.session.add(crop_data)
            db.session.commit()
            
            # return "Form submitted", 200
            return redirect(url_for('crop'))
        return render_template('create-crop.html')
    return redirect(url_for('login'))

    
@app.route('/crop/edit/<int:id>',methods=['GET','POST'])
def edit_crop(id):

    if current_user.is_authenticated:
        if current_user.role != 'admin':
            return render_template('forbidden.html')
        
        if request.method=='POST':
            
            crop = Crop.query.get(id)
            crop.name = request.form.get('name')
            crop.type = request.form.get('type')
            crop.weather_condition = request.form.get('weather_condition')
            
            db.session.commit()
            
            # return "Form submitted", 200
            return redirect(url_for('crop'))
            
        crop = Crop.query.get(id)
        if crop:
            return render_template('edit-crop.html',crop=crop)
        return render_template('pagenotfound.html')
    return redirect(url_for('login'))

@app.route('/crop/delete/<int:id>',methods=['POST'])
def delete_crop(id):
    
    # get details from the post request
    if current_user.is_authenticated:
        if current_user.role != 'admin':
            return render_template('forbidden.html')
        
        crop = Crop.query.get(id)
        if crop:
            db.session.delete(crop)
            db.session.commit()
            
            # return 'Crop Deleted', 200 
            return redirect(url_for('crop'))
        return render_template('pagenotfound.html')
    return redirect(url_for('login'))


# farmers

@app.route('/farmers')
def farmer():
    
    if current_user.is_authenticated:
        if current_user.role=='user':
            return redirect(url_for('farmer_profile',farmer_id=current_user.id))
        farmers = Farmer.query.all()
        
        return render_template('farmer.html', farmers=farmers)
    return redirect(url_for('login'))
    
@app.route('/farmer/<int:farmer_id>')
def farmer_profile(farmer_id):
    
    if current_user.is_authenticated:
        if current_user.role=='user':
            if farmer_id!=current_user.id:
                    return render_template('forbidden.html')
            else:
                farmer_id=current_user.id

        farmer = db.session.query(Farmer, Field,Crop)\
        .join(Field, Field.farmer_id == Farmer.id)\
        .join(Crop, Field.crop_id == Crop.id)\
        .filter(Farmer.id == farmer_id).all()
        # print(farmer)
        
        count=0
        for items in farmer:
            count+=1
        
        if count==0:
            farmer=Farmer.query.get(farmer_id)
            
        farmer_data={'farmer':farmer,'count':count}
        
        # calculate land size
        fields=Field.query.filter(Field.farmer_id==farmer_id).all()
        field_size=0
        for f in fields:
            field_size+=f.size
            
        # list all harvested crops
        harvests = db.session.query(Harvestandyield, Crop).join(Crop, Harvestandyield.crop_id == Crop.id).filter(Harvestandyield.farmer_id==farmer_id).all()
        harvested_crops=[]
        harvest_quantity=0
        for h,c in harvests:
            harvested_crops.append(c.name)
            harvest_quantity+=h.quantity
        harvest_data={'quantity':harvest_quantity,'crops':harvested_crops}
        
        # list all crops in market
        markets=db.session.query(Marketplace, Crop).join(Crop, Marketplace.crop_id == Crop.id).filter(Marketplace.farmer_id==farmer_id).all()
        market_quantity=0
        market_crops=[]
        for m,c in markets:
            market_crops.append(c.name)
            market_quantity+=m.quantity
        market_data={'quantity':market_quantity,'crops':market_crops}
        
        return render_template('profile.html', farmer=farmer_data,field_size=field_size,harvest_data=harvest_data,market_data=market_data)
    
    return redirect(url_for('login'))

# write for accessing farmer on a particular crop
@app.route('/farmer/crop/<int:crop_id>',methods=['GET','POST'])
def farmer_crop(crop_id):
        
        if current_user.is_authenticated:
            if current_user.role=='user':
                return redirect(url_for('farmer_profile',farmer_id=current_user.id))
            
            crop = Crop.query.get(crop_id)

            farmers = db.session.query(Farmer, Field, Crop)\
            .join(Field, Field.farmer_id == Farmer.id)\
            .join(Crop, Field.crop_id == Crop.id)\
            .filter(Crop.id == crop_id).all()
            
            return render_template('farmerbycrop.html', farmers=farmers,crop=crop)
        return redirect(url_for('login'))

# @app.route('/farmers/create',methods=['POST'])
# def create_farmer():
#     # get details from the post request
#     farmer_id= request.form.get('id')
#     farmer_name = request.form.get('name')
#     contact_details = request.form.get('contact_details')
#     land_size = request.form.get('land_size')
#     crop_performance = request.form.get('crop_performance')
    
#     farmer_data = Farmer(id=farmer_id, name=farmer_name, contact_details=contact_details, land_size=land_size, crop_performance=crop_performance)
#     db.session.add(farmer_data)
#     db.session.commit()
#     # return redirect(url_for('farmers'))
#     return "Form submitted", 200

@app.route('/farmer/edit/<int:id>',methods=['GET','POST'])
def edit_farmer(id):
    
    # get details from the post request
    if not current_user.is_authenticated:
        return render_template('forbidden.html')
    
    if request.method=='POST':
        if current_user.id!=id and current_user.role!='admin':
            return render_template('forbidden.html')
        
        farmer = Farmer.query.get(id)
        if farmer:
            farmer.name = request.form.get('name')
            farmer.email = request.form.get('email')
            farmer.crop_performance = request.form.get('crop_performance')
            
            db.session.commit()
            
        # return "Form submitted", 200
        return redirect(url_for('farmer'))
    
    farmer = Farmer.query.get(id)
    if farmer:
        farmer_id=farmer.id
        if farmer_id!=current_user.id and current_user.role!='admin':
            return render_template('forbidden.html')
        
        return render_template('edit-farmer.html',farmer=farmer)
    return render_template('pagenotfound.html')

@app.route('/farmer/delete/<int:id>',methods=['POST'])
def delete_farmer(id):
    
    if not current_user.is_authenticated:
        return render_template('forbidden.html')
    
    # get details from the post request
    if current_user.role=='user':
        return render_template('forbidden.html')
    
    farmer = Farmer.query.get(id)
    if farmer:
        db.session.delete(farmer)
        db.session.commit()
        
        # return 'Farmer Deleted', 200
        return redirect(url_for('farmer'))
    return render_template('pagenotfound.html')


# fields

@app.route('/fields')
def field():
    
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            fields_with_crops = db.session.query(Field, Crop, Farmer).join(Crop, Field.crop_id == Crop.id).join(Farmer, Farmer.id == Field.farmer_id).all()
        else:
            fields_with_crops = db.session.query(Field, Crop, Farmer).join(Crop, Field.crop_id == Crop.id).join(Farmer, Farmer.id == Field.farmer_id).filter(Field.farmer_id == current_user.id).all()
        
        crops = Crop.query.all()
        
        return render_template('field.html', fields=fields_with_crops, crops=crops)
    return redirect(url_for('login'))    

@app.route('/field/create',methods=['GET','POST'])
def create_field():
    
    # get details from the post request
    if not current_user.is_authenticated:
        return render_template('forbidden.html')
    
    if request.method=='POST':
        farmer_id=current_user.id
        # print(farmer_id)
        crop_id = request.form.get('crop_id')
        size = float(request.form.get('size'))
        soil_type = request.form.get('soil_type')
        # crop_id=crop.id 
        field_data = Field(farmer_id=farmer_id, crop_id=crop_id, size=size, soil_type=soil_type)
        
        farmer=Farmer.query.get(farmer_id)
        farmer.land_size+=size
        db.session.add(field_data)
        db.session.commit()
        
        # return "Form submitted", 200
        return redirect(url_for('field'))

    crops=Crop.query.all()
    return render_template('create-field.html',crops=crops)

@app.route('/field/edit/<int:id>',methods=['GET','POST'])
def edit_field(id):
    
    # get details from the post request
    if not current_user.is_authenticated:
        return render_template('forbidden.html')
        
    if request.method=='POST':
        crop_id=int(request.form.get('crop_id'))
        print(crop_id)
        field = Field.query.get(id)
        
        if field:
            farmer_id=field.farmer_id
            if farmer_id!=current_user.id and current_user.role!='admin':
                return render_template('forbidden.html')
            
            field.crop_id = crop_id
            field.size = float(request.form.get('size'))
            field.soil_type = request.form.get('soil_type')
            db.session.commit()

            farmer=Farmer.query.get(farmer_id)
            field=Field.query.filter_by(farmer_id=farmer_id).all()
            field_size=0
            for f in field:
                field_size+=f.size
            farmer.land_size=field_size
            db.session.commit()
            
        # return "Form submitted", 200
        return redirect(url_for('field'))
    
    field = db.session.query(Field, Crop,Farmer).join(Crop, Field.crop_id == Crop.id).join(Farmer,Farmer.id==Field.farmer_id).filter(Field.id==id).first()
    if field:
        farmer_id=field[0].farmer_id
        if farmer_id!=current_user.id and current_user.role!='admin':
            return render_template('forbidden.html')
        
        crop=field[1]
        crops=Crop.query.all()
        crops.remove(crop)
        crops.insert(0,crop)
        # print(crops)
        
        return render_template('edit-field.html',field=field,crops=crops)
    return render_template('pagenotfound.html')

@app.route('/field/delete/<int:id>',methods=['POST'])
def delete_field(id):
    
    # get details from the post request
    if not current_user.is_authenticated:
        return render_template('forbidden.html')
    
    field = Field.query.get(id)
    if field: 
        farmer_id=field.farmer_id
        
        if farmer_id!=current_user.id and current_user.role!='admin':
            return render_template('forbidden.html')
        
        db.session.delete(field)
        db.session.commit()
        
        Farmer.query.get(farmer_id).land_size-=field.size
        db.session.commit()
        
        # return 'Field Deleted', 200
        return redirect(url_for('field'))
    return render_template('pagenotfound.html')


# harvests

@app.route('/harvests')
def harvest():
    
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            harvests = db.session.query(Harvestandyield, Crop, Farmer).join(Crop, Harvestandyield.crop_id == Crop.id).join(Farmer, Farmer.id == Harvestandyield.farmer_id).all()
        else:
            harvests = db.session.query(Harvestandyield, Crop, Farmer).join(Crop, Harvestandyield.crop_id == Crop.id).join(Farmer, Farmer.id == Harvestandyield.farmer_id).filter(Harvestandyield.farmer_id == current_user.id).all()
        
        fields = Field.query.filter(Field.farmer_id == current_user.id)
        crops = Crop.query.all()
        
        return render_template('harvest.html', harvests=harvests, fields=fields, crops=crops)
    return redirect(url_for('login'))
    
# @app.route('/harvests/add',methods=['GET','POST'])
# def harvest_profile():
#     crops = Crop.query.all()
    # fields = Field.query.filter(Field.farmer_id==current_user.id).all() #taking fields of current user
#     if current_user.role=='admin':
        # farmers = Farmer.query.all() # taking all farmers. assign current farmer's fields to other farmers??
#     else:
#         farmers = Farmer.query.get(current_user.id)
#     print(fields)
#     return render_template('create-harvest.html', crops=crops, farmers=farmers, fields=fields)

@app.route('/harvest/create',methods=['GET','POST'])
def create_harvest():
    
    # get details from the post request
    if not current_user.is_authenticated:
        return render_template('forbidden.html')
    
    if request.method=='POST':
        field_id = int(request.form.get('field_id'))
        farmer_id=current_user.id
        crop_id= int(request.form.get('crop_id'))
        qty=request.form.get('quantity')
        
        harvest_data = Harvestandyield(field_id=field_id, farmer_id=farmer_id, crop_id=crop_id,quantity=qty)
        db.session.add(harvest_data)
        db.session.commit()
        
        fields=Field.query.filter(Field.farmer_id==current_user.id)
        farmer = Farmer.query.get(farmer_id) 
          
        # return "Form submitted", 200
        return redirect(url_for('harvest'))
    
    crop_in_fields=db.session.query(Field, Crop).join(Crop, Field.crop_id == Crop.id).filter(Field.farmer_id==current_user.id).all()
    fields=Field.query.filter(Field.farmer_id==current_user.id).all()
    farmer= Farmer.query.get(current_user.id)
    return render_template('create-harvest.html',crops=crop_in_fields,fields=fields,farmer=farmer)

@app.route('/harvest/edit/<int:id>',methods=['GET','POST'])
def edit_harvest(id):
    
    # get details from the post request
    if not current_user.is_authenticated:
        return render_template('forbidden.html')
    if request.method=='POST':
        crop=int(request.form.get('crop_id'))
        field=int(request.form.get('field_id'))
        print(field)
        quantity=float(request.form.get('quantity'))
        harvest = Harvestandyield.query.filter_by(id=id).first()
        print(harvest.farmer_id)
        if harvest:
            farmer_id=harvest.farmer_id
            if farmer_id!=current_user.id and current_user.role!='admin':
                return render_template('forbidden.html')
            
            harvest.field_id = field
            harvest.crop_id = crop
            harvest.quantity = quantity
            
            db.session.commit()
            
        # return "Form submitted", 200
        return redirect(url_for('harvest'))
    
    harvest = db.session.query(Harvestandyield, Crop,Farmer,Field).join(Crop, Harvestandyield.crop_id == Crop.id).join(Farmer,Farmer.id==Harvestandyield.farmer_id).join(Field,Field.id==Harvestandyield.field_id).filter(Harvestandyield.id==id).first()
    # print(harvest)
    if harvest:
        farmer_id=harvest[0].farmer_id 
        if farmer_id!=current_user.id and current_user.role!='admin':
            return render_template('forbidden.html')
        
        crop=(harvest[3],harvest[1])
        crop_with_field=db.session.query(Field, Crop).join(Crop, Field.crop_id == Crop.id).filter(Field.farmer_id==farmer_id).all()
        if len(crop_with_field)>0 and crop_with_field.count(crop)>0:crop_with_field.remove(crop)
        crop_with_field.insert(0,crop)
        
        field=harvest[3]
        fields=Field.query.filter(Field.farmer_id==farmer_id).all()
        if len(fields)>0:fields.remove(field)
        fields.insert(0,field)
        
        return render_template('edit-harvest.html',harvest=harvest,crops=crop_with_field,fields=fields)
    return render_template('pagenotfound.html')

@app.route('/harvest/delete/<int:id>',methods=['POST'])
def delete_harvest(id):
    
    # get details from the post request
    if not current_user.is_authenticated:
        return render_template('forbidden.html')
    
    harvest = Harvestandyield.query.get(id)
    if harvest:
        farmer_id=harvest.farmer_id
        if farmer_id!=current_user.id and current_user.role!='admin':
            return render_template('forbidden.html')
    
        db.session.delete(harvest)
        db.session.commit()
        
        # return 'Harvest Deleted', 200
        return redirect(url_for('harvest'))
    return render_template('pagenotfound.html')


# markets

@app.route('/markets')
def market():
    
    if current_user.is_authenticated:
        
        markets = db.session.query(Marketplace, Crop,Farmer).join(Crop, Marketplace.crop_id == Crop.id).join(Farmer,Farmer.id==Marketplace.farmer_id).all()
        crops=Crop.query.all()
        
        return render_template('marketplace.html', markets=markets,crops=crops)
    return redirect(url_for('login'))

@app.route('/market/create',methods=['GET','POST'])
def create_market():
    
    # get details from the post request
    if not current_user.is_authenticated:
        return render_template('forbidden.html')
    
    if request.method=='POST':
        crop_id=int(request.form.get('crop_id'))
        farmer_id = current_user.id
        price = request.form.get('price')
        quantity = request.form.get('quantity')
        
        market_data = Marketplace(farmer_id=farmer_id, crop_id=crop_id, price=price, quantity=quantity)
        db.session.add(market_data)
        db.session.commit()
        
        # return "Form submitted", 200
        return redirect(url_for('market'))
    
    # get crops which are present in farmers field's
    crop_in_fields=db.session.query(Field, Crop).join(Crop, Field.crop_id == Crop.id).filter(Field.farmer_id==current_user.id).all()
    farmer=Farmer.query.get(current_user.id)
    return render_template('create-market.html',crops=crop_in_fields,farmer=farmer)

@app.route('/market/edit/<int:id>',methods=['GET','POST'])
def edit_market(id):
    
    if not current_user.is_authenticated:
        return render_template('forbidden.html')
    
    if request.method=='POST':
        # get details from the post request
        
        market = Marketplace.query.get(id)
        if market:
            farmer_id=market.farmer_id
            
            if farmer_id!=current_user.id and current_user.role!='admin':
                return render_template('forbidden.html')
            
            crop_id = int(request.form.get('crop_id'))

            market.crop_id = int(crop_id)
            market.price = request.form.get('price')
            market.quantity = request.form.get('quantity')
            
            db.session.commit()
            
        # return "Form submitted", 200
        return redirect(url_for('market'))
    
    # join market crops table
    market = db.session.query(Marketplace, Crop,Farmer).join(Crop, Marketplace.crop_id == Crop.id).join(Farmer,Farmer.id==Marketplace.farmer_id).filter(Marketplace.id==id).first()
    if market:
        farmer_id=market[0].farmer_id
        crop=market[1]
        crops=Crop.query.all()
        if len(crops)>0 and crops.count(crop)>0:crops.remove(crop)
        crops.insert(0,crop)
        
        if farmer_id!=current_user.id and current_user.role!='admin':
            return render_template('forbidden.html')
        
        return render_template('edit-market.html',market=market,crops=crops)
    return render_template('pagenotfound.html')
        
@app.route('/market/delete/<int:id>',methods=['POST'])
def delete_market(id):
    
    # get details from the post request
    if not current_user.is_authenticated:
        return render_template('forbidden.html')
    
    market = Marketplace.query.get(id)
    if market:
        farmer_id=market.farmer_id
        if farmer_id!=current_user.id and current_user.role!='admin':
            return render_template('forbidden.html')

        db.session.delete(market)
        db.session.commit()
        
        # return 'Market Deleted', 200
        return redirect(url_for('market'))
    return render_template('pagenotfound.html')


if __name__ == '__main__':
    app.run(debug=True)