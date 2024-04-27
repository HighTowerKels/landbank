from flask import Flask, flash, render_template, request, redirect, url_for, jsonify, abort, Response, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, FloatField, SelectField
from wtforms.validators import InputRequired, Length, NumberRange, ValidationError
from wtforms.validators import Email
from flask_migrate import Migrate
from wtforms.validators import InputRequired, Length, Email 
from flask_mail import Mail
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
import re
from datetime import datetime, time
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from sqlalchemy.orm import relationship
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__, static_url_path='/static')
basedir = os.path.abspath(os.path.dirname((__file__)))
database = "app.db"
con = sqlite3.connect(os.path.join(basedir, database))
mail = Mail(app)
app.config['SECRET_KEY'] = "jhkxhiuydu"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, database)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['MAIL_SERVER'] = 'intexcoin.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'info@intexcoin.com'
app.config['MAIL_SERVER'] = 'server148.web-hosting.com'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.add_url_rule('/static/uploads/<filename>', 'uploads', build_only=True)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(255)  )
    lastname = db.Column(db.String(255))

    email = db.Column(db.String(255), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(100), nullable=True)  # Making user_location nullable
    nin_number = db.Column(db.String(20), nullable=True)  # Making nin_number nullable
    nin_slip = db.Column(db.String(100), nullable=True)  # Making nin_photo nullable
    bio = db.Column(db.Text, nullable=True)  # Making bio nullable
    phone_number = db.Column(db.String(20), nullable=True)  # Making phone_number nullable
    phone_number_two = db.Column(db.String(20), nullable=True)
    biz_name = db.Column(db.String(100), nullable=True)
    biz_bio = db.Column(db.Text, nullable=True)
    biz_location = db.Column(db.String(100), nullable=True)
    biz_number = db.Column(db.String(20), nullable=True)
    cac_numbers = db.Column(db.String(100), nullable=True)
    cac_slip = db.Column(db.String(100), nullable=True)




    is_admin = db.Column(db.Boolean, default=False)
    cart_items = db.relationship('CartItem', backref='user', lazy=True)
    profile_picture = db.Column(db.String(255))  # Add profile picture column


    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = generate_password_hash(password)
    def create(self, firstname='', lastname='', email='', password=''):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = generate_password_hash(password, method='sha256')
    
    def is_profile_updated(self):
        # Check if all mandatory fields are filled
        required_fields = [self.location, self.cac_numbers, self.nin_number, self.nin_slip, self.bio, self.phone_number]
        return all(required_fields)

        # Optionally, check if specific optional fields are filled
        # For example, check if the second phone number is filled
        # if not self.second_phone_number:
        #     return False

        # # Optionally, check if uploaded documents are valid
        # # For example, check if the NIN photo exists
        # if not os.path.exists(self.nin_photo):
        #     return False
    
    
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    def commit(self):
        db.session.commit()   
    def get_id(self):
        return str(self.id)
    def total_properties_uploaded(self):
        return Property.query.filter_by(user_id=self.id).count()

class Realtor(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    user = db.relationship('User', backref=db.backref('realtor', uselist=False))
    facebook_link = db.Column(db.String(255), nullable=True)
    instagram_link = db.Column(db.String(255), nullable=True)
    realtor_description = db.Column(db.Text, nullable=True)

    def save(self):
        db.session.add(self)
        db.session.commit()

class PropertyOwner(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    user = db.relationship('User', backref=db.backref('propertyowner', uselist=False))
    facebook_link = db.Column(db.String(255), nullable=True)
    instagram_link = db.Column(db.String(255), nullable=True)
    property_owner_description = db.Column(db.Text, nullable=True)

    def save(self):
        db.session.add(self)
        db.session.commit()

class Developer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    user = db.relationship('User', backref=db.backref('developer', uselist=False))
    company_name = db.Column(db.String(255), nullable=True)
    company_registration_number = db.Column(db.String(255), nullable=True)
    company_location = db.Column(db.String(255), nullable=True)
    facebook_link = db.Column(db.String(255), nullable=True)
    instagram_link = db.Column(db.String(255), nullable=True)
    developer_description = db.Column(db.Text, nullable=True)

    def save(self):
        db.session.add(self)
        db.session.commit()
        
# Property Model
class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_available = db.Column(db.String, nullable=False)
    property_ownership = db.Column(db.String, nullable=False)

    location = db.Column(db.String(255), nullable=False)
    property_lga = db.Column(db.String(255), nullable=False)
    property_type = db.Column(db.String, nullable=False)
    property_subtype = db.Column(db.String, nullable=False)
    property_negotiation = db.Column(db.String, nullable=False)
    property_price = db.Column(db.String, nullable=False)
    property_percent = db.Column(db.String, nullable=False)
    property_charges = db.Column(db.String, nullable=False)
    property_num_rooms = db.Column(db.Integer, nullable=False)
    property_num_baths = db.Column(db.Integer, nullable=False)
    property_num_toilets = db.Column(db.Integer, nullable=False)
    property_num_parlour = db.Column(db.Integer, nullable=False)
    property_size_min = db.Column(db.String, nullable=False)
    property_size_max = db.Column(db.String, nullable=False)
    completed_furnished = db.Column(db.Boolean, nullable=False, default=False)
    completed_unfurnished = db.Column(db.Boolean, nullable=False, default=False)
    carcas = db.Column(db.Boolean, nullable=False, default=False)
    newly_built = db.Column(db.Boolean, nullable=False, default=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    property_description = db.Column(db.String, nullable=False)
    property_likes = db.Column(db.Integer, default=0)
    property_shares = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User', backref='properties')
    approved = db.Column(db.Boolean, default=False)  # Define the 'approved' field
    image_filenames = db.Column(db.String)  # Store as comma-separated string
    document_filenames = db.Column(db.String) 
    
    time_posted = db.Column(db.Time) 


   
    def save(self):
        db.session.add(self)
        db.session.commit()

class Shared(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shared_property_available = db.Column(db.String, nullable=False)
    shared_property_ownership = db.Column(db.String, nullable=False)
    shared_lga = db.Column(db.String(255), nullable=False)

    location = db.Column(db.String(255), nullable=False)
    shared_property_type = db.Column(db.String, nullable=False)
    shared_subtype = db.Column(db.String, nullable=False)
    shared_negotiation = db.Column(db.String, nullable=False)
    shared_price = db.Column(db.String, nullable=False)
    shared_percent = db.Column(db.String, nullable=False)
    shared_charges = db.Column(db.String, nullable=False)
    shared_num_rooms = db.Column(db.Integer, nullable=False)
    shared_num_baths = db.Column(db.Integer, nullable=False)
    shared_num_toilets = db.Column(db.Integer, nullable=False)
    shared_num_parlour = db.Column(db.Integer, nullable=False)
    amenities = db.Column(db.String(255))
    shared_description = db.Column(db.Text, nullable=False)
    completed_furnished = db.Column(db.Boolean, nullable=False, default=False)
    completed_unfurnished = db.Column(db.Boolean, nullable=False, default=False)
    shared_likes = db.Column(db.Integer, default=0)
    shared_shares = db.Column(db.Integer, default=0)
    fully_furnished = db.Column(db.Boolean, nullable=False, default=False)
    partly_unfurnished = db.Column(db.Boolean, nullable=False, default=False)
    parking_space = db.Column(db.Boolean, nullable=False, default=False)
    laundry_room = db.Column(db.Boolean, nullable=False, default=False)
    shared_kitchen = db.Column(db.Boolean, nullable=False, default=False)
    shared_bathroom = db.Column(db.Boolean, nullable=False, default=False)
    noise_level = db.Column(db.Boolean, nullable=False, default=False)
    visitors = db.Column(db.Boolean, nullable=False, default=False)
    fitness_center = db.Column(db.Boolean, nullable=False, default=False)
    internet_service = db.Column(db.Boolean, nullable=False, default=False)
   
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User', backref='shared_properties')
    approved = db.Column(db.Boolean, default=False)
    image_filenames = db.Column(db.String)
    
    time_posted = db.Column(db.Time) 

    def save(self):
        db.session.add(self)
        db.session.commit()
        
        
        
        
class ShortLet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shortlet_property_available = db.Column(db.String, nullable=False)
    shortlet_property_ownership = db.Column(db.String, nullable=False)
    shortlet_lga = db.Column(db.String(255), nullable=False)

    location = db.Column(db.String(255), nullable=False)
    shortlet_property_type = db.Column(db.String, nullable=False)
    shortlet_subtype = db.Column(db.String, nullable=False)
    shortlet_negotiation = db.Column(db.String, nullable=False)
    shortlet_price = db.Column(db.String, nullable=False)
    shortlet_percent = db.Column(db.String, nullable=False)
    shortlet_charges = db.Column(db.String, nullable=False)
    shortlet_num_rooms = db.Column(db.Integer, nullable=False)
    shortlet_stay = db.Column(db.String, nullable=False)
    shortlet_num_toilets = db.Column(db.Integer, nullable=False)
    available = db.Column(db.Boolean, nullable=False, default=False)
    unavailable = db.Column(db.Boolean, nullable=False, default=False)
    shortlet_check_in = db.Column(db.Boolean, nullable=False, default=False)
    free_cancellation = db.Column(db.Boolean, nullable=False, default=False)
    fully_furnished = db.Column(db.Boolean, nullable=False, default=False)
    partly_unfurnished = db.Column(db.Boolean, nullable=False, default=False)
    parking_space = db.Column(db.Boolean, nullable=False, default=False)
    laundry_room = db.Column(db.Boolean, nullable=False, default=False)
    shared_kitchen = db.Column(db.Boolean, nullable=False, default=False)
    shared_bathroom = db.Column(db.Boolean, nullable=False, default=False)
    noise_level = db.Column(db.Boolean, nullable=False, default=False)
    visitors = db.Column(db.Boolean, nullable=False, default=False)
    fitness_center = db.Column(db.Boolean, nullable=False, default=False)
    internet_service = db.Column(db.Boolean, nullable=False, default=False)
   
    
    
    shortlet_description = db.Column(db.Text, nullable=False)
    shortlet_likes = db.Column(db.Integer, default=0)
    shortlet_shares = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User', backref='shortlet_properties')
    approved = db.Column(db.Boolean, default=False)
    image_filenames = db.Column(db.String)
    shortlet_date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    shortlet_time_posted = db.Column(db.Time) 

    def save(self):
        db.session.add(self)
        db.session.commit()
        

class JVA(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jva_property_ownership = db.Column(db.String, nullable=False)
    jva_lga = db.Column(db.String(255), nullable=False)

    jva_property_available = db.Column(db.String, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    jva_property_type = db.Column(db.String, nullable=False)
    jva_subtype = db.Column(db.String, nullable=False)
    jva_negotiation = db.Column(db.String, nullable=False)
    jva_price = db.Column(db.String, nullable=False)
    jva_percent = db.Column(db.String, nullable=False)
    jva_charges = db.Column(db.String, nullable=False)
   
    jva_description = db.Column(db.Text, nullable=False)
    
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
   
    jva_likes = db.Column(db.Integer, default=0)
    jva_shares = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User', backref='jva_properties')
    approved = db.Column(db.Boolean, default=False)  # Define the 'approved' field
    image_filenames = db.Column(db.String)  # Store as comma-separated string
    document_filenames = db.Column(db.String) 
    time_posted = db.Column(db.Time) 

    def save(self):
        db.session.add(self)
        db.session.commit()



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    property_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Define a relationship with the User model
    user = db.relationship('User', backref=db.backref('notifications', lazy=True))


class Secure(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    def not_auth(self):
        return "not allowed"

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Define relationships
    property = db.relationship('Property', backref='cart_items')



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# @app.route('/create_property', methods=['GET', 'POST'])
# @login_required
# def create_property():
#     if request.method == 'POST':
#         # Extract form data
#         price_type = request.form['price_type']
#         square_feet = request.form['square_feet']
#         percent = request.form['percent']
#         location = request.form['location']
#         price = request.form['price']
#         service_type = request.form['service_type']
#         description = request.form['description']
#         num_rooms = int(request.form['num_rooms'])
#         num_baths = int(request.form['num_baths'])
#         num_toilets = int(request.form['num_toilets'])
#         property_type = request.form['property_type']

#         # Ensure the UPLOAD_FOLDER exists
#         upload_folder = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
#         os.makedirs(upload_folder, exist_ok=True)

#         # Upload Main Image
#         image_files = request.files.getlist('fileUpload[]')
#         document_files = request.files.getlist('documentUpload[]')

#         # Initialize lists to store uploaded filenames
#         uploaded_image_filenames = []
#         uploaded_document_filenames = []

#         # Save uploaded files and generate comma-separated filenames
#         for file in image_files:
#             if file and allowed_file(file.filename):
#                 filename = secure_filename(file.filename)
#                 file.save(os.path.join(upload_folder, filename))
#                 uploaded_image_filenames.append(filename)
#                 print("Uploaded Image:", filename)
#             else:
#                 flash(f"Failed to upload image: {file.filename}", 'error')

#         for file in document_files:
#             if file and allowed_file(file.filename):
#                 filename = secure_filename(file.filename)
#                 file.save(os.path.join(upload_folder, filename))
#                 uploaded_document_filenames.append(filename)
#                 print("Uploaded Document:", filename)
#             else:
#                 flash(f"Failed to upload document: {file.filename}", 'error')

#         # If no images were uploaded successfully, return to the form
#         if not uploaded_image_filenames:
#             flash("No images uploaded", 'error')
#             return redirect(request.url)

#         # Convert lists to comma-separated strings
#         image_filenames = ','.join(uploaded_image_filenames)
#         document_filenames = ','.join(uploaded_document_filenames)

#         # Create new Property object
#         new_property = Property(
#             location=location,
#             price_type=price_type,
#             percent=percent,
#             square_feet=square_feet,
#             price=price,
#             service_type=service_type,
#             description=description,
#             num_rooms=num_rooms,
#             num_baths=num_baths,
#             num_toilets=num_toilets,
#             property_type=property_type,
#             approved=False,
#             image_filenames=image_filenames,
#             document_filenames=document_filenames,
#             user=current_user ,
#             time_posted=datetime.now().time()
#         )

#         # Add and commit to the database
#         db.session.add(new_property)
#         db.session.commit()
#         flash('Property has been created')
#         return redirect(url_for('dashboard'))

#     return render_template('creatinglisting.html')




@app.route('/create_property', methods=['GET', 'POST'])
@login_required
def create_property():
    if not current_user.is_profile_updated():
        flash('Please update your profile before creating a property!', 'warning')
        return redirect(url_for('update_profile'))

    
    if request.method == 'POST':
        # Extract form data
        property_ownership = request.form.get('property_ownership')

        property_available = request.form.get('property_available')
        location = request.form.get('location')
        property_type = request.form.get('property_type')
        property_subtype = request.form.get('property_subtype')
        property_negotiation = request.form.get('property_negotiation', '')
        property_price = request.form.get('property_price')
        property_percent = request.form.get('property_percent')
        property_charges = request.form.get('property_charges')
        property_num_rooms = int(request.form.get('property_num_rooms', 0))
        property_num_baths = int(request.form.get('property_num_baths', 0))
        property_num_toilets = int(request.form.get('property_num_toilets', 0))
        property_num_parlour = int(request.form.get('property_num_parlour', 0))
        property_size_min = request.form.get('property_size_min')
        property_size_max = request.form.get('property_size_max')
        property_description = request.form.get('property_description')
        property_lga = request.form.get('property_lga')
        # Handle checkboxes
        completed_furnished = request.form.get('completedFurnished') == 'on'
        completed_unfurnished = request.form.get('completedUnfurnished') == 'on'
        carcas = request.form.get('carcas') == 'on'
        newly_built = request.form.get('newlyBuilt') == 'on'
        # Ensure the UPLOAD_FOLDER exists
        upload_folder = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
        os.makedirs(upload_folder, exist_ok=True)

        # Upload Main Image
        image_files = request.files.getlist('fileUpload[]')
        document_files = request.files.getlist('documentUpload[]')

        # Initialize lists to store uploaded filenames
        uploaded_image_filenames = []
        uploaded_document_filenames = []

        # Save uploaded files and generate comma-separated filenames
        num_uploaded_images = 0

        for file in image_files:
            if num_uploaded_images >= 5:
                flash("You can upload a maximum of 5 images", 'error')
                break  
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_folder, filename)
                try:
                    file.save(file_path)
                    uploaded_image_filenames.append(filename)
                    print("Uploaded Image:", filename)
                    num_uploaded_images += 1
                except Exception as e:
                    flash(f"Failed to save image: {str(e)}", 'error')
        else:
            flash(f"Failed to upload image: {file.filename}", 'error')

        for file in document_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(upload_folder, filename))
                uploaded_document_filenames.append(filename)
                print("Uploaded Document:", filename)
            else:
                flash(f"Failed to upload document: {file.filename}", 'error')

        # If no images were uploaded successfully, return to the form
        if not uploaded_image_filenames:
            flash("No images uploaded", 'error')
            return redirect(create_property)

        # Convert lists to comma-separated strings
        image_filenames = ','.join(uploaded_image_filenames)
        document_filenames = ','.join(uploaded_document_filenames)
       #

        # Create new JVA object
        new_property = Property(
            property_ownership = property_ownership,
            property_available=property_available,
            location=location,
            property_type=property_type,
            property_subtype=property_subtype,
            property_negotiation=property_negotiation,
            property_price=property_price,
            property_percent=property_percent,
            property_charges=property_charges,
            property_num_rooms=property_num_rooms,
            property_num_baths=property_num_baths,
            property_num_toilets=property_num_toilets,
            property_num_parlour=property_num_parlour,
            property_size_min=property_size_min,
            property_size_max=property_size_max,
            property_description=property_description,
            property_lga = property_lga,
            completed_furnished=completed_furnished,
            completed_unfurnished=completed_unfurnished,
            carcas=carcas,
            newly_built=newly_built,
            approved=False,
            image_filenames=image_filenames,
            document_filenames=document_filenames,
            user=current_user,
           
        )
        
        # Add and commit to the database
        db.session.add(new_property)
        db.session.commit()
        flash('Property has been created')
        return redirect(url_for('dashboard'))

    return render_template('createlisting.html')



@app.route('/create_shared', methods=['GET', 'POST'])
@login_required
def create_shared():
    if not current_user.is_profile_updated():
        flash('Please update your profile before creating a property!', 'warning')
        return redirect(url_for('update_profile'))

    if request.method == 'POST':
        # Extract form data
        shared_property_ownership = request.form.get('shared_property_ownership')
        shared_property_available = request.form.get('shared_property_available')
        location = request.form.get('location')
        shared_property_type = request.form.get('shared_property_type')
        shared_subtype = request.form.get('shared_subtype')
        shared_negotiation = request.form.get('shared_negotiation')
        shared_price = request.form.get('shared_price')
        shared_percent = request.form.get('shared_percent')
        shared_charges = request.form.get('shared_charges')
        shared_num_rooms = int(request.form.get('shared_num_rooms', 0))
        shared_num_baths = int(request.form.get('shared_num_baths', 0))
        shared_num_toilets = int(request.form.get('shared_num_toilets', 0))
        shared_num_parlour = int(request.form.get('shared_num_parlour', 0))
        shared_description = request.form.get('shared_description')
        shared_lga = request.form.get('lga')
        # Amenities
        amenities = []
        if 'fullyFurnished' in request.form:
            amenities.append('Fully Furnished')
        if 'partlyFurnished' in request.form:
            amenities.append('Partly Furnished')
        if 'parkingSpace' in request.form:
            amenities.append('Parking Space')
        if 'laundryRoom' in request.form:
            amenities.append('Laundry Room')
        if 'sharedKitchen' in request.form:
            amenities.append('Shared Kitchen')
        if 'sharedBathroom' in request.form:
            amenities.append('Shared Bathroom')
        if 'noiseLevel' in request.form:
            amenities.append('Noise Level')
        if 'visitors' in request.form:
            amenities.append('Visitors Allowed')
        if 'fitnessCenter' in request.form:
            amenities.append('Fitness Center')
        if 'internet' in request.form:
            amenities.append('Internet Service')

        # Ensure the UPLOAD_FOLDER exists
        upload_folder = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
        os.makedirs(upload_folder, exist_ok=True)

        # Upload Main Image
        image_files = request.files.getlist('fileUpload[]')
        
        # Initialize lists to store uploaded filenames
        uploaded_image_filenames = []

        # Save uploaded files and generate comma-separated filenames
        num_uploaded_images = 0
        for file in image_files:
            if num_uploaded_images >= 5:
                flash("You can upload a maximum of 5 images", 'error')
                break  
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_folder, filename)
                try:
                    file.save(file_path)
                    uploaded_image_filenames.append(filename)
                    print("Uploaded Image:", filename)
                    num_uploaded_images += 1
                except Exception as e:
                    flash(f"Failed to save image: {str(e)}", 'error')
        else:
            flash(f"Failed to upload image: {file.filename}", 'error')

        # If no images were uploaded successfully, return to the form
        if not uploaded_image_filenames:
            flash("No images uploaded", 'error')
            return redirect(create_shared)

        # Convert lists to comma-separated strings
        image_filenames = ','.join(uploaded_image_filenames)

        # Create new Shared object
        new_shared = Shared(
            shared_property_ownership=shared_property_ownership,
            shared_property_available=shared_property_available,
            location=location,
            shared_property_type=shared_property_type,
            shared_subtype=shared_subtype,
            shared_negotiation=shared_negotiation,
            shared_price=shared_price,
            shared_percent=shared_percent,
            shared_charges=shared_charges,
            shared_num_rooms=shared_num_rooms,
            shared_num_baths=shared_num_baths,
            shared_num_toilets=shared_num_toilets,
            shared_num_parlour=shared_num_parlour,
            shared_description=shared_description,
            amenities=', '.join(amenities),  # Convert list to comma-separated string
            image_filenames=image_filenames,
            user=current_user,
            shared_lga = shared_lga,
            time_posted=datetime.now().time()
        )

        # Add and commit to the database
        db.session.add(new_shared)
        db.session.commit()
        flash('Shared property has been created')
        return redirect(url_for('dashboard'))

    return render_template('create_shared.html')


@app.route('/create_shortlet', methods=['GET', 'POST'])
@login_required
def create_shortlet():
    if not current_user.is_profile_updated():
        flash('Please update your profile before creating a property!', 'warning')
        return redirect(url_for('update_profile'))

    if request.method == 'POST':
        # Extract form data
        shortlet_property_available = request.form.get('shortlet_property_available')
        shortlet_property_ownership = request.form.get('shortlet_property_ownership')
        location = request.form.get('location')
        shortlet_property_type = request.form.get('shortlet_property_type')
        shortlet_subtype = request.form.get('shortlet_subtype')
        shortlet_negotiation = request.form.get('shortlet_negotiation')
        shortlet_price = request.form.get('shortlet_price')
        shortlet_percent = request.form.get('shortlet_percent')
        shortlet_charges = request.form.get('shortlet_charges')
        shortlet_num_rooms = request.form.get('shortlet_num_rooms')
        shortlet_stay = request.form.get('shortlet_stay')
        shortlet_num_toilets = request.form.get('shortlet_num_toilets')
        shortlet_description = request.form.get('shortlet_description')
        fully_furnished = 'fullyFurnished' in request.form
        partly_furnished = 'partlyFurnished' in request.form
        parking_space = 'parkingSpace' in request.form
        laundry_room = 'laundryRoom' in request.form
        shared_kitchen = 'sharedKitchen' in request.form
        shared_bathroom = 'sharedBathroom' in request.form
        noise_level = 'noiseLevel' in request.form
        visitors = 'visitors' in request.form
        fitness_center = 'fitnessCenter' in request.form
        internet_service = 'internet' in request.form
        shortlet_lga = request.form.get('lga')
        # Ensure the UPLOAD_FOLDER exists
        upload_folder = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
        os.makedirs(upload_folder, exist_ok=True)

        # Upload Main Image
        image_files = request.files.getlist('fileUpload[]')

        # Initialize lists to store uploaded filenames
        uploaded_image_filenames = []

        # Save uploaded files and generate comma-separated filenames
        num_uploaded_images = 0

        for file in image_files:
            if num_uploaded_images >= 5:
                flash("You can upload a maximum of 5 images", 'error')
                break  
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_folder, filename)
                try:
                    file.save(file_path)
                    uploaded_image_filenames.append(filename)
                    print("Uploaded Image:", filename)
                    num_uploaded_images += 1
                except Exception as e:
                    flash(f"Failed to save image: {str(e)}", 'error')
        else:
            flash(f"Failed to upload image: {file.filename}", 'error')

        # Convert lists to comma-separated strings
        image_filenames = ','.join(uploaded_image_filenames)

        # Create new ShortLet object
        new_shortlet = ShortLet(
            shortlet_property_available=shortlet_property_available,
            shortlet_property_ownership=shortlet_property_ownership,
            location=location,
            shortlet_property_type=shortlet_property_type,
            shortlet_subtype=shortlet_subtype,
            shortlet_negotiation=shortlet_negotiation,
            shortlet_price=shortlet_price,
            shortlet_percent=shortlet_percent,
            shortlet_charges=shortlet_charges,
            shortlet_num_rooms=shortlet_num_rooms,
            shortlet_stay=shortlet_stay,
            shortlet_num_toilets=shortlet_num_toilets,
            shortlet_description=shortlet_description,
            fully_furnished=fully_furnished,
            partly_unfurnished=partly_furnished,
            parking_space=parking_space,
            laundry_room=laundry_room,
            shared_kitchen=shared_kitchen,
            shared_bathroom=shared_bathroom,
            noise_level=noise_level,
            visitors=visitors,
            fitness_center=fitness_center,
            internet_service=internet_service,
            shortlet_date_posted=datetime.utcnow(),
            approved=False,
            image_filenames=image_filenames,
            user=current_user,
            shortlet_time_posted=datetime.now().time(),
            shortlet_lga = shortlet_lga
        )

        # Add and commit to the database
        db.session.add(new_shortlet)
        db.session.commit()
        flash('Shortlet property has been created')
        return redirect(url_for('dashboard'))

    return render_template('create_shortlet.html')

@app.route('/create_jva', methods=['GET', 'POST'])
@login_required
def create_jva():
    if not current_user.is_profile_updated():
        flash('Please update your profile before creating a property!', 'warning')
        return redirect(url_for('update_profile'))

    if request.method == 'POST':
        # Extract form data
        jva_property_ownership = request.form.get('jva_property_ownership')
        jva_lga = request.form.get('lga')
        jva_property_available = request.form.get('jva_property_available')
        location = request.form.get('location')
        jva_property_type = request.form.get('jva_property_type')
        jva_subtype = request.form.get('jva_subtype')
        jva_negotiation = request.form.get('jva_negotiation')
        jva_price = request.form.get('jva_price')
        jva_percent = request.form.get('jva_percent')
        jva_charges = request.form.get('jva_charges')
        
        jva_description = request.form['jva_description']
       
        # Ensure the UPLOAD_FOLDER exists
        upload_folder = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
        os.makedirs(upload_folder, exist_ok=True)

        # Upload Main Image
        image_files = request.files.getlist('fileUpload[]')
        document_files = request.files.getlist('documentUpload[]')

        # Initialize lists to store uploaded filenames
        uploaded_image_filenames = []
        uploaded_document_filenames = []

        # Save uploaded files and generate comma-separated filenames
        num_uploaded_images = 0

        for file in image_files:
            if num_uploaded_images >= 5:
                flash("You can upload a maximum of 5 images", 'error')
                break  
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_folder, filename)
                try:
                    file.save(file_path)
                    uploaded_image_filenames.append(filename)
                    print("Uploaded Image:", filename)
                    num_uploaded_images += 1
                except Exception as e:
                    flash(f"Failed to save image: {str(e)}", 'error')
        else:
            flash(f"Failed to upload image: {file.filename}", 'error')
        for file in document_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(upload_folder, filename))
                uploaded_document_filenames.append(filename)
                print("Uploaded Document:", filename)
            else:
                flash(f"Failed to upload document: {file.filename}", 'error')

        # If no images were uploaded successfully, return to the form
        if not uploaded_image_filenames:
            flash("No images uploaded", 'error')
            return redirect(create_property)

        # Convert lists to comma-separated strings
        image_filenames = ','.join(uploaded_image_filenames)
        document_filenames = ','.join(uploaded_document_filenames)

        # Create new JVA object
        new_jva = JVA(
            jva_property_ownership = jva_property_ownership,

            jva_property_available=jva_property_available,
            location=location,
            jva_property_type=jva_property_type,
            jva_subtype=jva_subtype,
            jva_negotiation=jva_negotiation,
            jva_price=jva_price,
            jva_percent=jva_percent,
            jva_charges=jva_charges,
            
            jva_description=jva_description,
           
            approved=False,
            image_filenames=image_filenames,
            document_filenames=document_filenames,
            user=current_user,
            time_posted=datetime.now().time(),
            jva_lga = jva_lga
        )

        # Add and commit to the database
        db.session.add(new_jva)
        db.session.commit()
        flash('JVA has been created')
        return redirect(url_for('dashboard'))

    return render_template('creating_jva.html')


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # Check if current user is an admin (you should have a way to identify admin users)
    if not current_user.is_admin:
        return redirect(url_for('index'))  # Redirect to homepage if not admin

    # Fetch pending properties for approval
    pending_properties = Property.query.filter_by(approved=False).all()
    pending_shortlet = ShortLet.query.filter_by(approved=False).all()
    pending_shared = Shared.query.filter_by(approved = False).all()
    pending_jva = JVA.query.filter_by(approved = False).all()

    return render_template('admin_dashboard.html', pending_properties=pending_properties, pending_shortlet = pending_shortlet, pending_shared = pending_shared, pending_jva = pending_jva)


@app.route('/approve_property/<int:property_id>')
@login_required
def approve_property(property_id):
    # Check if current user is an admin
    if not current_user.is_admin:
        return redirect(url_for('index'))  # Redirect to homepage if not admin

    # Find the property by ID
    property_to_approve = Property.query.get_or_404(property_id)

    # Approve the property
    property_to_approve.approved = True
    db.session.commit()

    # Send notification to the user
    send_approval_notification(property_to_approve.user.email)

    flash('Property has been approved')
    return redirect(url_for('admin_dashboard'))



@app.route('/approve_shortlet/<int:shortlet_id>')
@login_required
def approve_shortlet(shortlet_id):
    # Check if current user is an admin
    if not current_user.is_admin:
        return redirect(url_for('index'))  # Redirect to homepage if not admin

    # Find the property by ID
    shortlet_to_approve = ShortLet.query.get_or_404(shortlet_id)

    # Approve the property
    shortlet_to_approve.approved = True
    db.session.commit()

    # Send notification to the user
    send_approval_notification(shortlet_to_approve.user.email)

    flash('Property Shortlet has been approved')
    return redirect(url_for('admin_dashboard'))


@app.route('/approve_shared/<int:shared_id>')
@login_required
def approve_shared(shared_id):
    # Check if current user is an admin
    if not current_user.is_admin:
        return redirect(url_for('index'))  # Redirect to homepage if not admin

    # Find the property by ID
    shared_to_approve = Shared.query.get_or_404(shared_id)

    # Approve the property
    shared_to_approve.approved = True
    db.session.commit()

    # Send notification to the user
    send_approval_notification(shared_to_approve.user.email)

    flash('Property Shared apartment has been approved')
    return redirect(url_for('admin_dashboard'))


@app.route('/approve_jva/<int:jva_id>')
@login_required
def approve_jva(jva_id):
    # Check if current user is an admin
    if not current_user.is_admin:
        return redirect(url_for('index'))  # Redirect to homepage if not admin

    # Find the property by ID
    jva_to_approve = JVA.query.get_or_404(jva_id)

    # Approve the property
    jva_to_approve.approved = True
    db.session.commit()

    # Send notification to the user
    send_approval_notification(jva_to_approve.user.email)

    flash('Property JVA has been approved')
    return redirect(url_for('admin_dashboard'))





from flask_mail import Message

def send_approval_notification(user_email, property_id):
    """
    Sends an approval notification to the user's email and stores the message in the user's dashboard.
    """
    # Send email notification
    msg = Message(subject="Your property has been approved!",
                  recipients=[user_email],
                  body="Your property has been approved.")
    mail.send(msg)
    
    # Update user's notification dashboard
    user = User.query.filter_by(email=user_email).first()
    if user:
        user.notifications.append(Notification(message="Your property has been approved.", property_id=property_id))
        db.session.commit()
    else:
        flash('User not found')  # Handle the case where user is not found

def send_rejection_notification(user_email, property_id):
    """
    Sends a rejection notification to the user's email and stores the message in the user's dashboard.
    """
    # Send email notification
    msg = Message(subject="Your property has been rejected",
                  recipients=[user_email],
                  body="Your property has been rejected.")
    mail.send(msg)
    
    # Update user's notification dashboard
    user = User.query.filter_by(email=user_email).first()
    if user:
        user.notifications.append(Notification(message="Your property has been rejected.", property_id=property_id))
        db.session.commit()
    else:
        flash("User not found!")  # Handle the case where user is not found



@app.route('/reject_property/<int:property_id>')
@login_required
def reject_property(property_id):
    # Check if current user is an admin
    if not current_user.is_admin:
        return redirect(url_for('index'))  # Redirect to homepage if not admin

    # Find the property by ID
    property_to_reject = Property.query.get_or_404(property_id)

    # Delete the property
    db.session.delete(property_to_reject)
    db.session.commit()

    # Send notification to the user
    send_rejection_notification(property_to_reject.user.email)

    flash('Property has been rejected')
    return redirect(url_for('admin_dashboard'))


@app.route('/reject_shortlet/<int:shortlet_id>')
@login_required
def reject_shortlet(shortlet_id):
    # Check if current user is an admin
    if not current_user.is_admin:
        return redirect(url_for('index'))  # Redirect to homepage if not admin

    # Find the property by ID
    shortlet_to_reject = ShortLet.query.get_or_404(shortlet_id)

    # Delete the property
    db.session.delete(shortlet_to_reject)
    db.session.commit()

    # Send notification to the user
    send_rejection_notification(shortlet_to_reject.user.email)

    flash('Property Shortlet has been rejected')
    return redirect(url_for('admin_dashboard'))

@app.route('/reject_shared/<int:shared_id>')
@login_required
def reject_shared(shared_id):
    # Check if current user is an admin
    if not current_user.is_admin:
        return redirect(url_for('index'))  # Redirect to homepage if not admin

    # Find the property by ID
    shared_to_reject = Shared.query.get_or_404(shared_id)

    # Delete the property
    db.session.delete(shared_to_reject)
    db.session.commit()

    # Send notification to the user
    send_rejection_notification(shared_to_reject.user.email)

    flash('Property Shared has been rejected')
    return redirect(url_for('admin_dashboard'))

@app.route('/reject_jva/<int:jva_id>')
@login_required
def reject_jva(jva_id):
    # Check if current user is an admin
    if not current_user.is_admin:
        return redirect(url_for('index'))  # Redirect to homepage if not admin

    # Find the property by ID
    jva_to_reject = JVA.query.get_or_404(jva_id)

    # Delete the property
    db.session.delete(jva_to_reject)
    db.session.commit()

    # Send notification to the user
    send_rejection_notification(jva_to_reject.user.email)

    flash('Property JVA has been rejected')
    return redirect(url_for('admin_dashboard'))




@app.route('/signin',methods=['GET','POST'])
def signin():
    user = User()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['passwords']
        user = User.query.filter_by(email=email,is_admin=True).first()
       
        if user:
            if user.password == password:
                login_user(user)
                return redirect('admin')

                
                
            


    return render_template('admin_login.html')
@app.route('/process',methods=['GET','POST'])

def process():
    auths = User()
    if request.method == "POST":
        
        password = request.form['pass']
        email = request.form['email']
        auths = User(
             password=password,email=email,is_admin=True)
        db.session.add(auths)
        db.session.commit()
        return "welcome sign up completed"
    return render_template('admin_signup.html')
    
@app.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    if not current_user.is_authenticated:
        flash('Please log in to add items to your cart.', 'info')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        property_id = request.form.get('property_id')

        # Validate property ID
        if not property_id or not property_id.isdigit():
            flash('Invalid property ID', 'error')
            return redirect(url_for('index'))

        # Check if the property exists
        property = Property.query.get(property_id)
        if not property:
            flash('Property not found', 'error')
            return redirect(url_for('index'))

        # Check if the property is already in the user's cart
        existing_cart_item = CartItem.query.filter_by(property_id=property_id, user_id=current_user.id).first()
        if existing_cart_item:
            flash('Property is already in your cart', 'error')
            return redirect(request.referrer or url_for('index'))  # Redirect back to the previous page or index

        # Add the property to the user's cart
        cart_item = CartItem(property_id=property_id, user_id=current_user.id)
        db.session.add(cart_item)
        try:
            db.session.commit()
            flash('Property added to your cart', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the property to your cart. Please try again.', 'error')
            app.logger.error(f"Error adding property to cart: {e}")
        return redirect(request.referrer or url_for('index'))  # Redirect back to the previous page or index

@app.route('/cart')
@login_required
def cart():
    user = current_user
    
    # Query the cart items for the current user
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    image_files = []
    for item in cart_items:
        # Assuming each cart item has a property with image_filenames attribute
        image_files.append(item.property.image_filenames.split(',')[0])  # Add the first image filename for each cart item
    
    return render_template('cart.html', cart_items=cart_items, image_files=image_files, user = user)

@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    # Find the cart item by ID
    cart_item = CartItem.query.get(item_id)
    if not cart_item:
        flash('Cart item not found', 'error')
        return redirect(url_for('cart'))
    
    # Check if the cart item belongs to the current user
    if cart_item.user_id != current_user.id:
        flash('You are not authorized to remove this item from the cart', 'error')
        return redirect(url_for('cart'))
    
    # Delete the cart item from the database
    db.session.delete(cart_item)
    db.session.commit()
    
    flash('Item removed from cart', 'success')
    return redirect(url_for('cart'))
    

@app.route('/')
def index():
    properties = Property.query.all()
    approved_properties = Property.query.filter_by(approved=True).all()
    pending_properties = Property.query.filter_by(approved=False).all()
    return render_template('index.html', properties=properties, approved_properties=approved_properties, pending_properties=pending_properties)


# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         firstname = request.form.get('firstname')
#         lastname = request.form.get('lastname')
#         email = request.form.get('email')
#         password = request.form.get('password')
#         nin = request.form.get('nin')
#         profile_picture_path = None  # Initialize profile picture path
        
#         # Ensure the UPLOAD_FOLDER exists
#         upload_folder = os.path.join(app.root_path, 'static', app.config['UPLOAD_FOLDER'])
#         os.makedirs(upload_folder, exist_ok=True)
#         print("UPLOAD_FOLDER:", upload_folder)
        
#         # Handle profile picture upload
#         if 'profile_picture' in request.files:
#             file = request.files['profile_picture']
#             if file.filename != '':
#                 if file and allowed_file(file.filename):
#                     filename = secure_filename(file.filename)
#                     file_path = os.path.join(upload_folder, filename)
#                     file.save(file_path)
#                     print("Uploaded Image Path:", file_path)  # Debugging line
#             # Set profile picture path relative to the 'static' folder
#                     profile_picture_path = 'uploads/' + filename
#                     print("Profile Picture Path:", profile_picture_path)  # Debugging line
#                 else:
#                     flash("Please upload a valid image (png, jpg, jpeg, gif)")
#                     return render_template('signup.html')

#         # Check if profile picture was uploaded
#         if profile_picture_path is None:
#             flash("Please upload a profile picture")
#             return render_template('signup.html')

#         # Create new user with profile picture
#         new_user = User(firstname=firstname, lastname=lastname, email=email, nin=nin,
#                         profile_picture=profile_picture_path)
#         new_user.set_password(password)
#         new_user.save()
#         return render_template('role_selection.html', user=new_user)

#     return render_template('signup.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')

        # Create new user without location
        new_user = User(firstname=firstname, lastname=lastname, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Redirect to the login page
        login_user(new_user)
        flash('Signup successful!', 'success')
        return redirect(url_for('listing'))

    return render_template('signup.html')



@app.route('/select_role/<int:user_id>', methods=['GET', 'POST'])
def select_role(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        role = request.form.get('role')

        if role == 'realtor':
            return render_template('realtor_signup.html', user=user)
        elif role == 'property_owner':
            return render_template('property_owner_signup.html', user=user)
        elif role == 'developer':
            return render_template('developer_signup.html', user=user)

    return render_template('role_selection.html', user=user)

@app.route('/realtor_signup/<int:user_id>', methods=['POST'])
def realtor_signup(user_id):
    user = User.query.get_or_404(user_id)

    facebook_link = request.form.get('facebook_link')
    instagram_link = request.form.get('instagram_link')
    realtor_description = request.form.get('realtor_description')

    realtor = Realtor(user=user, facebook_link=facebook_link, instagram_link=instagram_link,
                      realtor_description=realtor_description)
    realtor.save()
    

    return redirect(url_for('parking'))

@app.route('/property_owner_signup/<int:user_id>', methods=['POST'])
def property_owner_signup(user_id):
    user = User.query.get_or_404(user_id)

    facebook_link = request.form.get('facebook_link')
    instagram_link = request.form.get('instagram_link')
    property_owner_description = request.form.get('property_owner_description')

    property_owner = PropertyOwner(user=user, facebook_link=facebook_link, instagram_link=instagram_link,
                                   property_owner_description=property_owner_description)
    property_owner.save()

    return redirect(url_for('parking'))

@app.route('/developer_signup/<int:user_id>', methods=['POST'])
def developer_signup(user_id):
    user = User.query.get_or_404(user_id)

    company_name = request.form.get('company_name')
    company_registration_number = request.form.get('company_registration_number')
    company_location = request.form.get('company_location')
    facebook_link = request.form.get('facebook_link')
    instagram_link = request.form.get('instagram_link')
    developer_description = request.form.get('developer_description')

    developer = Developer(user=user, company_name=company_name,
                          company_registration_number=company_registration_number,
                          company_location=company_location,
                          facebook_link=facebook_link, instagram_link=instagram_link,
                          developer_description=developer_description)
    developer.save()
    

    return redirect(url_for('parking'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('listing'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')

    return render_template('login.html')

@app.route('/parking')
def parking():
    return render_template('parking.html')

@app.route('/forrent')
def forrent():
    user = current_user
    properties = Property.query.all()
    approved_properties = Property.query.filter_by(approved=True).all()
    pending_properties = Property.query.filter_by(approved=False).all()
    return render_template('for_rent.html', properties=properties, approved_properties=approved_properties, pending_properties=pending_properties, user=user)

@app.route('/forsale')
def forsale():
    user = current_user
    properties = Property.query.all()
    approved_properties = Property.query.filter_by(approved=True).all()
    pending_properties = Property.query.filter_by(approved=False).all()
    return render_template('for_sale.html', properties=properties, approved_properties=approved_properties, pending_properties=pending_properties, user=user)


@app.route('/jv')
def jv():
    user = current_user
    properties = Property.query.all()
    approved_properties = Property.query.filter_by(approved=True).all()
    pending_properties = Property.query.filter_by(approved=False).all()
    return render_template('jv.html', properties=properties, approved_properties=approved_properties, pending_properties=pending_properties, user=user)

@app.route('/shortlet')
def shortlet():
    user = current_user
    shortlet = ShortLet.query.all()
    approved_shortlet = ShortLet.query.filter_by(approved=True).all()
    pending_shortlet = ShortLet.query.filter_by(approved=False).all()
    return render_template('shortlet.html', shortlet=shortlet, approved_shortlet=approved_shortlet, pending_shortlet=pending_shortlet, user=user)


@app.route('/nav')
def nav():
    return render_template('nav.html')
@app.route('/dash_nav')
def dash_nav():
    user_id = current_user.id
    user = User.query.get(user_id)
    return render_template('dash_nav.html', user=user)    

@app.route('/listing')
def listing():
    user = current_user
    shared_instance = Shared.query.first()  # Or however you fetch a Shared object
    
    amenity = None  # Initialize amenity variable
    
    # Check if shared_instance is not None before accessing its attributes
    if shared_instance:
        amenity = shared_instance.amenities 
    
    properties = Property.query.all()
    shortlet = ShortLet.query.all()
    shared = Shared.query.all()
    jva = JVA.query.all()
    
    approved_properties = Property.query.filter_by(approved=True).all()
    pending_properties = Property.query.filter_by(approved=False).all()
    
    approved_shortlets = ShortLet.query.filter_by(approved=True).all()
    pending_shortlets = ShortLet.query.filter_by(approved=False).all()
    
    approved_shared = Shared.query.filter_by(approved=True).all()
    pending_shared = Shared.query.filter_by(approved=False).all()
    
    approved_jva = JVA.query.filter_by(approved=True).all()
    pending_jva = JVA.query.filter_by(approved=False).all()
    
    return render_template('listing.html' ,shared_instance= shared_instance ,amenity= amenity ,  properties=properties, approved_properties=approved_properties, pending_properties=pending_properties, approved_shortlets = approved_shortlets, pending_shortlets = pending_shortlets, shortlet = shortlet, shared = shared, approved_shared = approved_shared, pending_shared = pending_shared, jva = jva, approved_jva= approved_jva, pending_jva = pending_jva, user=user)



@app.route('/listinguser')
def listinguser():
    user = current_user
    properties = Property.query.all()
    approved_properties = Property.query.filter_by(approved=True).all()
    pending_properties = Property.query.filter_by(approved=False).all()
    return render_template('listing_user.html', properties=properties, approved_properties=approved_properties, pending_properties=pending_properties, user=user)



# @app.route('/property/details/<int:property_id>',  methods=['GET', 'POST'])
# def property_details(property_id):
#     property = Property.query.get(property_id)
#     approved_properties = Property.query.filter_by(approved=True).all()
#     pending_properties = Property.query.filter_by(approved=False).all()
#     if not property:
#         return("error")
#     return render_template('property_details.html',  property=property, approved_properties=approved_properties, pending_properties=pending_properties)
@app.route('/property/details/<int:property_id>', methods=['GET', 'POST'])
def property_details(property_id):
    user = current_user

    property = Property.query.get(property_id)
    if not property:
        flash('Property not found', 'error')
        return redirect(url_for('index'))

    if not current_user.is_authenticated:
        flash('Please log in to add items to your cart.', 'info')
        return redirect(url_for('login'))

    # Assuming you have a property_images attribute in your Property model
    property_images = property.image_filenames.split(',') if property.image_filenames else []
    
    
    if request.method == 'POST':
        if 'add_to_cart' in request.form:
            cart_item = CartItem(property_id=property_id, user_id=current_user.id)
            db.session.add(cart_item)
            try:
                db.session.commit()
                flash('Property added to your cart', 'success')
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while adding the property to your cart. Please try again.', 'error')
                app.logger.error(f"Error adding property to cart: {e}")
            return redirect(url_for('property_details', property_id=property_id))

    return render_template('property_details.html', property=property,image_files=property_images, user = user)






@app.route('/shortlet/details/<int:shortlet_id>', methods=['GET', 'POST'])
def shortlet_details(shortlet_id):
    user = current_user

    shortlet = ShortLet.query.get(shortlet_id)
    if not shortlet:
        flash('Shortlet not found', 'error')
        return redirect(url_for('index'))

    if not current_user.is_authenticated:
        flash('Please log in to add items to your cart.', 'info')
        return redirect(url_for('login'))

    # Assuming you have a property_images attribute in your Property model
    shortlet_images = shortlet.image_filenames.split(',') if shortlet.image_filenames else []
    
    
    if request.method == 'POST':
        if 'add_to_cart' in request.form:
            cart_item = CartItem(shortlet_id=shortlet_id, user_id=current_user.id)
            db.session.add(cart_item)
            try:
                db.session.commit()
                flash('Shortlet added to your cart', 'success')
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while adding the property to your cart. Please try again.', 'error')
                app.logger.error(f"Error adding property to cart: {e}")
            return redirect(url_for('shortlet_details', shortlet_id=shortlet_id))

    return render_template('shortlet_details.html', shortlet=shortlet,image_files=shortlet_images, user = user)







def jinja2_enumerate(iterable):
    return enumerate(iterable)

# Add the filter to Jinja2 environment
app.jinja_env.filters['enumerate'] = jinja2_enumerate


@app.route('/dashboard')
@login_required
def dashboard():
    user_id = current_user.id
    user = User.query.get(user_id)
    user_notifications = current_user.notifications
    properties = Property.query.all()
    approved_properties = Property.query.filter_by(approved=True).all()
    pending_properties = Property.query.filter_by(approved=False).all()
    return render_template('dashboard.html', notifications=user_notifications , properties=properties, approved_properties=approved_properties, pending_properties=pending_properties, user=user)


from flask import render_template

@app.route('/search_properties', methods=['POST'])
def search_properties():
    if request.method == 'POST':
        # Get search parameters from the form
        location = request.form.get('location')
        property_type = request.form.get('property_type')
        price_range = request.form.get('price_range')
        user = current_user
        # Perform the search based on the provided parameters and filter by approved properties
        properties = Property.query.filter_by(approved=True)

        if location:
            properties = properties.filter(Property.location.ilike(f'%{location}%'))

        if property_type:
            properties = properties.filter(Property.property_type.ilike(f'%{property_type}%'))

        if price_range:
            min_price, max_price = map(int, price_range.split('-'))
            properties = properties.filter(Property.price >= min_price, Property.price <= max_price)

        # Execute the query to get the search results
        properties = properties.all()

        # Render a new page with the search results
        return render_template('search_results.html', properties=properties, user = user)

    return "Search Properties Page"




@app.route('/creatinglisting')
def createlisting():
    user = current_user
    properties = Property.query.all()
    approved_properties = Property.query.filter_by(approved=True).all()
    pending_properties = Property.query.filter_by(approved=False).all()
    return render_template('createlisting.html', properties=properties, approved_properties=approved_properties, pending_properties=pending_properties, user=user)

@app.route('/cardpayment')
def cardpayment():
    return render_template('card.html')

@app.route('/bankpayment/')
def bankpayment():
    return render_template('bank.html')

@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if request.method == 'POST':
        user_id = current_user.id
        user = User.query.get(user_id)
        
        if user:
            # Update user profile fields
            user.phone_number = request.form['phone_number']
            user.location = request.form['house_number']
            user.nin_number = request.form['nin_number']
            user.phone_number_two = request.form['alitnumber']
            user.bio = request.form['bio']
            
            
            if 'biz_name' in request.form:
                user.biz_name = request.form['biz_name']

            if 'biz_bio' in request.form:
                user.biz_bio = request.form['biz_bio']

            if 'biz_location' in request.form:
                user.biz_location = request.form['biz_location']

            if 'biz_number' in request.form:
                user.biz_number = request.form['biz_number']

            if 'cac_numbers' in request.form:
                user.cac_numbers = request.form['cac_numbers']
            
            # Handle file uploads for user documents
            if 'nin_slip' in request.files:
                nin_slip = request.files['nin_slip']
                if nin_slip.filename != '':
                    filename = secure_filename(nin_slip.filename)
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    nin_slip.save(file_path)
                    user.nin_slip = file_path
            
            if 'cac_slip' in request.files:
                cac_slip = request.files['cac_slip']
                if cac_slip.filename != '':
                    filename = secure_filename(cac_slip.filename)
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    cac_slip.save(file_path)
                    user.cac_slip = file_path

            # Commit user profile changes
            db.session.commit()

            # Create new profile
            new_profile = User(
                phone_number=user.phone_number,
                location=user.location,
                nin_number=user.nin_number,
                phone_number_two=user.phone_number_two,
                bio=user.bio,
                biz_name=user.biz_name,
                biz_bio=user.biz_bio,
                biz_location=user.biz_location,
                biz_number=user.biz_number,
                cac_numbers=user.cac_numbers,
                # Populate other fields as needed
            )

            # Add and commit new profile to the database
            db.session.add(new_profile)
            db.session.commit()

            flash('Profile updated successfully! New profile has been created.', 'success')
            return redirect(url_for('dashboard'))  # Redirect to the appropriate page
        else:
            flash('User not found!', 'error')
            return redirect(url_for('dashboard'))  # Redirect to the appropriate page
    else:
        # Handle GET request if needed
        return render_template('settings.html', user=current_user)  # Render the update profile form

@app.route('/verification')
def verification():
    user_id = current_user.id 
    user = User.query.get(user_id)  # Get the user instance (replace user_id with the actual user ID)
    total_properties = user.total_properties_uploaded()

    # Retrieve pending properties
    pending_properties = Property.query.filter_by(user_id=user_id, approved=False).all()
    total_pending_properties = len(pending_properties) if pending_properties else 0

    # Retrieve approved properties
    approved_properties = Property.query.filter_by(user_id=user_id, approved=True).all()
    total_approved_properties = len(approved_properties) if approved_properties else 0

    return render_template('verification.html', 
                           total_properties=total_properties, 
                           total_pending_properties=total_pending_properties, 
                           total_approved_properties=total_approved_properties,
                           pending_properties=pending_properties,
                           approved_properties=approved_properties, user=user)

@app.route('/transferpayment')
def transferpayment():
    user = current_user
    properties = Property.query.all()
    approved_properties = Property.query.filter_by(approved=True).all()
    pending_properties = Property.query.filter_by(approved=False).all()
    return render_template('bank.html', properties=properties, approved_properties=approved_properties, pending_properties=pending_properties, user=user)

@app.route('/settings')
def settings():
    user = current_user
    properties = Property.query.all()
    approved_properties = Property.query.filter_by(approved=True).all()
    pending_properties = Property.query.filter_by(approved=False).all()
    return render_template('settings.html', properties=properties, approved_properties=approved_properties, pending_properties=pending_properties, user=user)



@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route("/db/renew")
def database():
    db.drop_all()
    db.create_all()
    return "Hello done!!!"

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)
