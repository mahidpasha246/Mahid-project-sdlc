
import os
import re
import random
import secrets

from datetime import datetime, timedelta

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_from_directory
)

from flask_sqlalchemy import SQLAlchemy

from flask_wtf.csrf import CSRFProtect

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from werkzeug.utils import secure_filename

# ============================================================

# APPLICATION CONFIGURATION

# ============================================================

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ["DIGITAL_LEGACY_SECRET_KEY"]

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///digital_legacy.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["UPLOAD_FOLDER"] = "uploads"

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

db = SQLAlchemy(app)

csrf = CSRFProtect()

csrf.init_app(app)
# ============================================================

# CREATE UPLOAD FOLDER

# ============================================================

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# ============================================================

# ALLOWED FILE EXTENSIONS

# ============================================================

ALLOWED_EXTENSIONS = {

    "pdf",

    "png",

    "jpg",

    "jpeg",

    "doc",

    "docx"

}

def allowed_file(filename):

    return (

        "." in filename

        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

    )

# ============================================================

# VALIDATION FUNCTIONS

# ============================================================

def valid_username(username):

    return re.fullmatch(r"[A-Za-z0-9_]{4,30}", username) is not None

def valid_password(password):

    return re.fullmatch(

        r"(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,100}",

        password

    ) is not None

def valid_email(email):

    return re.fullmatch(

        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",

        email

    ) is not None

def valid_phone(phone):

    return re.fullmatch(r"[6-9]\d{9}", phone) is not None

def valid_name(name):

    return re.fullmatch(r"[A-Za-z ]{2,100}", name) is not None

def valid_relation(relation):

    return re.fullmatch(r"[A-Za-z ]{2,50}", relation) is not None

# ============================================================

# DATABASE MODELS

# ============================================================

class User(db.Model):

    id = db.Column(

        db.Integer,

        primary_key=True

    )

    username = db.Column(

        db.String(100),

        unique=True,

        nullable=False

    )

    password = db.Column(

        db.String(255),

        nullable=False

    )

    fullname = db.Column(

        db.String(100),

        nullable=False

    )

    email = db.Column(

        db.String(100),

        unique=True,

        nullable=False

    )

    phone = db.Column(

        db.String(20),

        unique=True,

        nullable=False

    )

    gender = db.Column(

        db.String(30),

        nullable=False

    )

    address = db.Column(

        db.String(300),

        nullable=False

    )

class Asset(db.Model):

    id = db.Column(

        db.Integer,

        primary_key=True

    )

    owner = db.Column(

        db.String(100),

        nullable=False

    )

    asset_name = db.Column(

        db.String(150),

        nullable=False

    )

    asset_type = db.Column(

        db.String(100),

        nullable=False

    )

    description = db.Column(

        db.String(500),

        nullable=False

    )

    date = db.Column(

        db.DateTime,

        default=datetime.utcnow

    )

class Activity(db.Model):

    id = db.Column(

        db.Integer,

        primary_key=True

    )

    username = db.Column(

        db.String(100),

        nullable=False

    )

    action = db.Column(

        db.String(300),

        nullable=False

    )

    date = db.Column(

        db.DateTime,

        default=datetime.utcnow

    )

class Beneficiary(db.Model):

    id = db.Column(

        db.Integer,

        primary_key=True

    )

    owner = db.Column(

        db.String(100),

        nullable=False

    )

    name = db.Column(

        db.String(100),

        nullable=False

    )

    email = db.Column(

        db.String(100),

        nullable=False

    )

    relation = db.Column(

        db.String(50),

        nullable=False

    )

class Document(db.Model):

    id = db.Column(

        db.Integer,

        primary_key=True

    )

    owner = db.Column(

        db.String(100),

        nullable=False

    )

    filename = db.Column(

        db.String(255),

        nullable=False

    )

    date = db.Column(

        db.DateTime,

        default=datetime.utcnow

    )

class Legacy(db.Model):

    id = db.Column(

        db.Integer,

        primary_key=True

    )

    owner = db.Column(

        db.String(100),

        nullable=False

    )

    beneficiary_id = db.Column(

        db.Integer,

        nullable=False

    )

    asset_id = db.Column(

        db.Integer,

        nullable=True

    )

    document_id = db.Column(

        db.Integer,

        nullable=True

    )

    release_date = db.Column(

        db.DateTime,

        nullable=False

    )

    status = db.Column(

        db.String(30),

        default="Pending",

        nullable=False

    )

    created_date = db.Column(

        db.DateTime,

        default=datetime.utcnow

    )

# ============================================================

# ACTIVITY LOG FUNCTION

# ============================================================

def log_activity(username, action):

    activity = Activity(

        username=username,

        action=action

    )

    db.session.add(activity)

    db.session.commit()

# ============================================================

# HOME

# ============================================================

@app.route("/")

@app.route("/home")

def home():

    return render_template("home.html")

# ============================================================

# REGISTER

# ============================================================

@app.route("/register", methods=["GET", "POST"])

def register():

    if request.method == "POST":

        fullname = request.form.get(

            "fullname",

            ""

        ).strip()

        username = request.form.get(

            "username",

            ""

        ).strip()

        email = request.form.get(

            "email",

            ""

        ).strip().lower()

        phone = request.form.get(

            "phone",

            ""

        ).strip()

        password = request.form.get(

            "password",

            ""

        )

        confirm_password = request.form.get(

            "confirm_password",

            ""

        )

        gender = request.form.get(

            "gender",

            ""

        ).strip()

        address = request.form.get(

            "address",

            ""

        ).strip()

        # -----------------------------

        # VALIDATION

        # -----------------------------

        if not valid_name(fullname):

            flash(

                "Full name should contain only letters and spaces.",

                "error"

            )

            return redirect("/register")

        if not valid_username(username):

            flash(

                "Username must contain 4-30 letters, numbers or underscores.",

                "error"

            )

            return redirect("/register")

        if not valid_email(email):

            flash(

                "Please enter a valid email address.",

                "error"

            )

            return redirect("/register")

        if not valid_phone(phone):

            flash(

                "Please enter a valid 10-digit Indian mobile number.",

                "error"

            )

            return redirect("/register")

        if not valid_password(password):

            flash(

                "Password must contain uppercase, lowercase, number and minimum 8 characters.",

                "error"

            )

            return redirect("/register")

        if password != confirm_password:

            flash(

                "Passwords do not match.",

                "error"

            )

            return redirect("/register")

        if gender not in ["Male", "Female", "Other"]:

            flash(

                "Please select a valid gender.",

                "error"

            )

            return redirect("/register")

        if len(address) < 3:

            flash(

                "Please enter a valid address.",

                "error"

            )

            return redirect("/register")

        # -----------------------------

        # DUPLICATE CHECKS

        # -----------------------------

        if User.query.filter_by(

            username=username

        ).first():

            flash(

                "Username already exists.",

                "error"

            )

            return redirect("/register")

        if User.query.filter_by(

            email=email

        ).first():

            flash(

                "Email already registered.",

                "error"

            )

            return redirect("/register")

        if User.query.filter_by(

            phone=phone

        ).first():

            flash(

                "Phone number already registered.",

                "error"

            )

            return redirect("/register")

        # -----------------------------

        # GENERATE OTP

        # -----------------------------

        otp = str(secrets.randbelow(900000) + 100000)

        # -----------------------------

        # SAVE REGISTRATION DATA

        # IN SESSION

        # -----------------------------

        session["register_data"] = {

            "fullname": fullname,

            "username": username,

            "email": email,

            "phone": phone,

            "password": generate_password_hash(password),

            "gender": gender,

            "address": address

        }

        session["register_otp"] = otp

        session["register_otp_expiry"] = (

            datetime.now() + timedelta(minutes=5)

        ).timestamp()

        return redirect("/verify-registration")

    return render_template("register.html")

# ============================================================

# VERIFY REGISTRATION OTP

# ============================================================

@app.route(

    "/verify-registration",

    methods=["GET", "POST"]

)

def verify_registration():

    register_data = session.get(

        "register_data"

    )

    saved_otp = session.get(

        "register_otp"

    )

    expiry = session.get(

        "register_otp_expiry"

    )

    if not register_data or not saved_otp:

        flash(

            "Registration session expired. Please register again.",

            "error"

        )

        return redirect("/register")

    if request.method == "POST":

        entered_otp = request.form.get(

            "otp",

            ""

        ).strip()

        # -----------------------------

        # CHECK EXPIRY

        # -----------------------------

        if not expiry or datetime.now().timestamp() > expiry:

            session.pop(

                "register_data",

                None

            )

            session.pop(

                "register_otp",

                None

            )

            session.pop(

                "register_otp_expiry",

                None

            )

            flash(

                "OTP expired. Please register again.",

                "error"

            )

            return redirect("/register")

        # -----------------------------

        # CHECK OTP

        # -----------------------------

        if entered_otp != saved_otp:

            flash(

                "Invalid OTP. Please try again.",

                "error"

            )

            return render_template(

                "verify_registration.html",

                otp=saved_otp

            )

        # -----------------------------

        # CREATE USER

        # -----------------------------

        existing_user = User.query.filter(

            (User.username == register_data["username"])

            | (User.email == register_data["email"])

            | (User.phone == register_data["phone"])

        ).first()

        if existing_user:

            session.pop(

                "register_data",

                None

            )

            session.pop(

                "register_otp",

                None

            )

            session.pop(

                "register_otp_expiry",

                None

            )

            flash(

                "Account information already exists. Please login.",

                "error"

            )

            return redirect("/login")

        hashed_password = register_data["password"]

        user = User(

            username=register_data["username"],

            password=hashed_password,

            fullname=register_data["fullname"],

            email=register_data["email"],

            phone=register_data["phone"],

            gender=register_data["gender"],

            address=register_data["address"]

        )

        db.session.add(user)

        db.session.commit()

        # -----------------------------

        # LOG ACTIVITY

        # -----------------------------

        log_activity(

            user.username,

            "Account created successfully."

        )

        # -----------------------------

        # CLEAR OTP SESSION

        # -----------------------------

        session.pop(

            "register_data",

            None

        )

        session.pop(

            "register_otp",

            None

        )

        session.pop(

            "register_otp_expiry",

            None

        )

        flash(

            "Account created successfully. Please login.",

            "success"

        )

        return redirect("/login")

    return render_template(

        "verify_registration.html",

        otp=saved_otp

    )

# ============================================================

# LOGIN

# ============================================================

@app.route("/login", methods=["GET", "POST"])

def login():

    if request.method == "POST":

        username = request.form.get(

            "username",

            ""

        ).strip()

        password = request.form.get(

            "password",

            ""

        )

        user = User.query.filter_by(

            username=username

        ).first()

        if not user:

            flash(

                "Invalid username or password.",

                "error"

            )

            return redirect("/login")

        if not check_password_hash(

            user.password,

            password

        ):

            flash(

                "Invalid username or password.",

                "error"

            )

            return redirect("/login")

        # -----------------------------

        # CREATE LOGIN SESSION

        # -----------------------------

        session["user"] = user.username

        session["user_id"] = user.id

        log_activity(

            user.username,

            "User logged in."

        )

        return redirect("/dashboard")

    return render_template("login.html")

# ============================================================

# DASHBOARD

# ============================================================

@app.route("/dashboard")

def dashboard():

    if "user" not in session:

        return redirect("/login")

    username = session["user"]

    # Count user's assets

    asset_count = Asset.query.filter_by(

        owner=username

    ).count()

    # Count user's beneficiaries

    beneficiary_count = Beneficiary.query.filter_by(

        owner=username

    ).count()

    # Count user's documents

    document_count = Document.query.filter_by(

        owner=username

    ).count()

    # Count user's legacy assignments

    legacy_count = Legacy.query.filter_by(

        owner=username

    ).count()

    # Recent activities

    recent_activities = (

        Activity.query

        .filter_by(username=username)

        .order_by(Activity.date.desc())

        .limit(5)

        .all()

    )

    # Current user

    user = User.query.filter_by(

        username=username

    ).first()

    return render_template(

        "dashboard.html",

        user=user,

        asset_count=asset_count,

        beneficiary_count=beneficiary_count,

        document_count=document_count,

        legacy_count=legacy_count,

        recent_activities=recent_activities

    )

# ============================================================

# PROFILE

# ============================================================

@app.route("/profile")

def profile():

    if "user" not in session:

        return redirect("/login")

    username = session["user"]

    user = User.query.filter_by(

        username=username

    ).first()

    if not user:

        session.clear()

        return redirect("/login")

    return render_template(

        "profile.html",

        user=user

    )

# ============================================================

# EDIT PROFILE

# ============================================================

@app.route(

    "/edit-profile",

    methods=["GET", "POST"]

)

def edit_profile():

    if "user_id" not in session:

        return redirect("/login")

    user = User.query.get(

        session["user_id"]

    )

    if not user:

        session.clear()

        return redirect("/login")

    if request.method == "POST":

        fullname = request.form.get(

            "fullname",

            ""

        ).strip()

        email = request.form.get(

            "email",

            ""

        ).strip().lower()

        phone = request.form.get(

            "phone",

            ""

        ).strip()

        gender = request.form.get(

            "gender",

            ""

        ).strip()

        address = request.form.get(

            "address",

            ""

        ).strip()

        if not valid_name(fullname):

            flash(

                "Please enter a valid full name.",

                "error"

            )

            return redirect("/edit-profile")

        if not valid_email(email):

            flash(

                "Please enter a valid email.",

                "error"

            )

            return redirect("/edit-profile")

        if not valid_phone(phone):

            flash(

                "Please enter a valid 10-digit phone number.",

                "error"

            )

            return redirect("/edit-profile")

        if gender not in [

            "Male",

            "Female",

            "Other"

        ]:

            flash(

                "Please select a valid gender.",

                "error"

            )

            return redirect("/edit-profile")

        if len(address) < 3:

            flash(

                "Please enter a valid address.",

                "error"

            )

            return redirect("/edit-profile")

        # -----------------------------

        # DUPLICATE EMAIL

        # -----------------------------

        email_user = User.query.filter(

            User.email == email,

            User.id != user.id

        ).first()

        if email_user:

            flash(

                "Email already used by another account.",

                "error"

            )

            return redirect("/edit-profile")

        # -----------------------------

        # DUPLICATE PHONE

        # -----------------------------

        phone_user = User.query.filter(

            User.phone == phone,

            User.id != user.id

        ).first()

        if phone_user:

            flash(

                "Phone number already used by another account.",

                "error"

            )

            return redirect("/edit-profile")

        user.fullname = fullname

        user.email = email

        user.phone = phone

        user.gender = gender

        user.address = address

        db.session.commit()

        log_activity(

            user.username,

            "Profile updated."

        )

        flash(

            "Profile updated successfully.",

            "success"

        )

        return redirect("/profile")

    return render_template(

        "edit_profile.html",

        user=user

    )

# ============================================================

# ADD ASSET

# ============================================================

@app.route("/add_asset", methods=["GET", "POST"])

@app.route("/add-asset", methods=["GET", "POST"])

def add_asset():

    if "user" not in session:

        return redirect("/login")

    if request.method == "POST":

        asset_name = request.form.get(

            "asset_name",

            ""

        ).strip()

        asset_type = request.form.get(

            "asset_type",

            ""

        ).strip()

        description = request.form.get(

            "description",

            ""

        ).strip()

        if not asset_name:

            flash(

                "Asset name is required.",

                "error"

            )

            return redirect("/add_asset")

        if not asset_type:

            flash(

                "Asset type is required.",

                "error"

            )

            return redirect("/add_asset")

        if not description:

            flash(

                "Description is required.",

                "error"

            )

            return redirect("/add_asset")

        asset = Asset(

            owner=session["user"],

            asset_name=asset_name,

            asset_type=asset_type,

            description=description

        )

        db.session.add(asset)

        db.session.commit()

        log_activity(

            session["user"],

            f"Asset added: {asset_name}"

        )

        flash(

            "Asset added successfully.",

            "success"

        )

        return redirect("/assets")

    return render_template(

        "add_asset.html"

    )

# ============================================================

# VIEW ASSETS

# ============================================================

@app.route("/assets")

def assets():

    if "user" not in session:

        return redirect("/login")

    assets_list = (

        Asset.query

        .filter_by(owner=session["user"])

        .order_by(Asset.date.desc())

        .all()

    )

    return render_template(

        "assets.html",

        assets=assets_list

    )

# ============================================================

# EDIT ASSET

# ============================================================

@app.route(

    "/edit-asset/<int:asset_id>",

    methods=["GET", "POST"]

)

def edit_asset(asset_id):

    if "user" not in session:

        return redirect("/login")

    asset = Asset.query.filter_by(

        id=asset_id,

        owner=session["user"]

    ).first()

    if not asset:

        flash(

            "Asset not found.",

            "error"

        )

        return redirect("/assets")

    if request.method == "POST":

        asset_name = request.form.get(

            "asset_name",

            ""

        ).strip()

        asset_type = request.form.get(

            "asset_type",

            ""

        ).strip()

        description = request.form.get(

            "description",

            ""

        ).strip()

        if not asset_name or not asset_type or not description:

            flash(

                "All fields are required.",

                "error"

            )

            return redirect(

                url_for(

                    "edit_asset",

                    asset_id=asset.id

                )

            )

        asset.asset_name = asset_name

        asset.asset_type = asset_type

        asset.description = description

        db.session.commit()

        log_activity(

            session["user"],

            f"Asset updated: {asset_name}"

        )

        flash(

            "Asset updated successfully.",

            "success"

        )

        return redirect("/assets")

    return render_template(

        "edit_asset.html",

        asset=asset

    )

# ============================================================

# DELETE ASSET

# ============================================================

# ============================================================

# DELETE ASSET

# ============================================================

@app.route(

    "/delete-asset/<int:asset_id>",

    methods=["POST"]

)

def delete_asset(asset_id):

    if "user" not in session:

        return redirect("/login")

    asset = Asset.query.filter_by(

        id=asset_id,

        owner=session["user"]

    ).first()

    if not asset:

        flash("Asset not found.", "error")

        return redirect("/assets")

    asset_name = asset.asset_name

    db.session.delete(asset)

    db.session.commit()

    log_activity(

        session["user"],

        f"Asset deleted: {asset_name}"

    )

    flash(

        "Asset deleted successfully.",

        "success"

    )

    return redirect("/assets")

# ============================================================

# ADD BENEFICIARY

# ============================================================

@app.route(

    "/add-beneficiary",

    methods=["GET", "POST"]

)

def add_beneficiary():

    if "user" not in session:

        return redirect("/login")

    if request.method == "POST":

        name = request.form.get(

            "name",

            ""

        ).strip()

        email = request.form.get(

            "email",

            ""

        ).strip().lower()

        relation = request.form.get(

            "relation",

            ""

        ).strip()

        if not valid_name(name):

            flash(

                "Please enter a valid beneficiary name.",

                "error"

            )

            return redirect("/add-beneficiary")

        if not valid_email(email):

            flash(

                "Please enter a valid email.",

                "error"

            )

            return redirect("/add-beneficiary")

        if not valid_relation(relation):

            flash(

                "Please enter a valid relation.",

                "error"

            )

            return redirect("/add-beneficiary")

        beneficiary = Beneficiary(

            owner=session["user"],

            name=name,

            email=email,

            relation=relation

        )

        db.session.add(beneficiary)

        db.session.commit()

        log_activity(

            session["user"],

            f"Beneficiary added: {name}"

        )

        flash(

            "Beneficiary added successfully.",

            "success"

        )

        return redirect("/beneficiaries")

    return render_template(

        "add_beneficiary.html"

    )

# ============================================================

# VIEW BENEFICIARIES

# ============================================================

@app.route("/beneficiaries")

def beneficiaries():

    if "user" not in session:

        return redirect("/login")

    beneficiaries_list = (

        Beneficiary.query

        .filter_by(owner=session["user"])

        .order_by(Beneficiary.id.desc())

        .all()

    )

    return render_template(

        "beneficiaries.html",

        beneficiaries=beneficiaries_list

    )

# ============================================================

# EDIT BENEFICIARY

# ============================================================

@app.route(

    "/edit-beneficiary/<int:beneficiary_id>",

    methods=["GET", "POST"]

)

def edit_beneficiary(beneficiary_id):

    if "user" not in session:

        return redirect("/login")

    beneficiary = Beneficiary.query.filter_by(

        id=beneficiary_id,

        owner=session["user"]

    ).first()

    if not beneficiary:

        flash(

            "Beneficiary not found.",

            "error"

        )

        return redirect("/beneficiaries")

    if request.method == "POST":

        name = request.form.get(

            "name",

            ""

        ).strip()

        email = request.form.get(

            "email",

            ""

        ).strip().lower()

        relation = request.form.get(

            "relation",

            ""

        ).strip()

        if not valid_name(name):

            flash(

                "Please enter a valid name.",

                "error"

            )

            return redirect(

                url_for(

                    "edit_beneficiary",

                    beneficiary_id=beneficiary.id

                )

            )

        if not valid_email(email):

            flash(

                "Please enter a valid email.",

                "error"

            )

            return redirect(

                url_for(

                    "edit_beneficiary",

                    beneficiary_id=beneficiary.id

                )

            )

        if not valid_relation(relation):

            flash(

                "Please enter a valid relation.",

                "error"

            )

            return redirect(

                url_for(

                    "edit_beneficiary",

                    beneficiary_id=beneficiary.id

                )

            )

        beneficiary.name = name

        beneficiary.email = email

        beneficiary.relation = relation

        db.session.commit()

        log_activity(

            session["user"],

            f"Beneficiary updated: {name}"

        )

        flash(

            "Beneficiary updated successfully.",

            "success"

        )

        return redirect("/beneficiaries")

    return render_template(

        "edit_beneficiary.html",

        beneficiary=beneficiary

    )

# ============================================================

# DELETE BENEFICIARY

# ============================================================

@app.route(

    "/delete-beneficiary/<int:beneficiary_id>",

    methods=["POST"]

)

def delete_beneficiary(beneficiary_id):

    if "user" not in session:

        return redirect("/login")

    beneficiary = Beneficiary.query.filter_by(

        id=beneficiary_id,

        owner=session["user"]

    ).first()

    if not beneficiary:

        flash(

            "Beneficiary not found.",

            "error"

        )

        return redirect("/beneficiaries")

    beneficiary_name = beneficiary.name

    db.session.delete(beneficiary)

    db.session.commit()

    log_activity(

        session["user"],

        f"Beneficiary deleted: {beneficiary_name}"

    )

    flash(

        "Beneficiary deleted successfully.",

        "success"

    )

    return redirect("/beneficiaries")

# ============================================================

# UPLOAD DOCUMENT

# ============================================================

@app.route(

    "/upload",

    methods=["GET", "POST"]

)

@app.route(

    "/documents/upload",

    methods=["GET", "POST"]

)

def upload_document():

    if "user" not in session:

        return redirect("/login")

    if request.method == "POST":

        if "file" not in request.files:

            flash(

                "Please select a file.",

                "error"

            )

            return redirect("/upload")

        file = request.files["file"]

        if file.filename == "":

            flash(

                "No file selected.",

                "error"

            )

            return redirect("/upload")

        if not allowed_file(file.filename):

            flash(

                "File type is not allowed.",

                "error"

            )

            return redirect("/upload")

        filename = secure_filename(

            file.filename

        )

        # -----------------------------

        # AVOID SAME FILENAME

        # -----------------------------

        base_name, extension = os.path.splitext(

            filename

        )

        counter = 1

        original_filename = filename

        while os.path.exists(

            os.path.join(

                app.config["UPLOAD_FOLDER"],

                filename

            )

        ):

            filename = (

                f"{base_name}_{counter}{extension}"

            )

            counter += 1

        file.save(

            os.path.join(

                app.config["UPLOAD_FOLDER"],

                filename

            )

        )

        document = Document(

            owner=session["user"],

            filename=filename

        )

        db.session.add(document)

        db.session.commit()

        log_activity(

            session["user"],

            f"Document uploaded: {filename}"

        )

        flash(

            "Document uploaded successfully.",

            "success"

        )

        return redirect("/documents")

    return render_template(

        "upload.html"

    )

# ============================================================

# DOCUMENT LIST

# ============================================================

@app.route("/documents")

def documents():

    if "user" not in session:

        return redirect("/login")

    documents_list = (

        Document.query

        .filter_by(owner=session["user"])

        .order_by(Document.date.desc())

        .all()

    )

    return render_template(

        "documents.html",

        documents=documents_list

    )

# ============================================================

# VIEW DOCUMENT

# ============================================================

@app.route(

    "/view-document/<int:document_id>"

)

def view_document(document_id):

    if "user" not in session:

        return redirect("/login")

    document = Document.query.filter_by(

        id=document_id,

        owner=session["user"]

    ).first()

    if not document:

        flash(

            "Document not found.",

            "error"

        )

        return redirect("/documents")

    return render_template(

        "view_document.html",

        document=document

    )

# ============================================================

# DOWNLOAD DOCUMENT

# ============================================================

@app.route("/download-document/<int:document_id>")

def download_document(document_id):

    if "user" not in session:

        return redirect("/login")

    document = Document.query.filter_by(

        id=document_id,

        owner=session["user"]

    ).first()

    if not document:

        flash("Document not found.", "error")

        return redirect("/documents")

    return send_from_directory(

        app.config["UPLOAD_FOLDER"],

        document.filename,

        as_attachment=True

    )

# ============================================================

# PREVIEW DOCUMENT

# ============================================================

@app.route("/preview-document/<int:document_id>")

def preview_document(document_id):

    if "user" not in session:

        return redirect("/login")

    document = Document.query.filter_by(

        id=document_id,

        owner=session["user"]

    ).first()

    if not document:

        return "Document not found", 404

    if not document.filename.lower().endswith(

        (".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf")

    ):

        return "Preview not supported", 415

    response = send_from_directory(

        app.config["UPLOAD_FOLDER"],

        document.filename,

        as_attachment=False

    )

    response.headers["X-Content-Type-Options"] = "nosniff"

    response.headers["Content-Security-Policy"] = (

        "default-src 'none'; style-src 'unsafe-inline'"

    )

    return response

# ============================================================

# DELETE DOCUMENT

# ============================================================

@app.route(

    "/delete-document/<int:document_id>",

    methods=["POST"]

)

def delete_document(document_id):

    if "user" not in session:

        return redirect("/login")

    document = Document.query.filter_by(

        id=document_id,

        owner=session["user"]

    ).first()

    if not document:

        flash(

            "Document not found.",

            "error"

        )

        return redirect("/documents")

    filename = document.filename

    file_path = os.path.join(

        app.config["UPLOAD_FOLDER"],

        filename

    )

    if os.path.exists(file_path):

        os.remove(file_path)

    db.session.delete(document)

    db.session.commit()

    log_activity(

        session["user"],

        f"Document deleted: {filename}"

    )

    flash(

        "Document deleted successfully.",

        "success"

    )

    return redirect("/documents")

# ============================================================

# CREATE LEGACY

# ============================================================

@app.route("/create-legacy", methods=["GET", "POST"])

def create_legacy():

    if "user" not in session:

        return redirect("/login")

    username = session["user"]

    beneficiaries = Beneficiary.query.filter_by(owner=username).all()

    assets = Asset.query.filter_by(owner=username).all()

    documents = Document.query.filter_by(owner=username).all()

    if request.method == "POST":

        beneficiary_id = request.form.get("beneficiary_id")

        asset_id = request.form.get("asset_id")

        document_id = request.form.get("document_id")

        release_date = request.form.get("release_date")

        # --------------------------------

        # CHECK BENEFICIARY

        # --------------------------------

        if not beneficiary_id:

            flash("Please select a beneficiary.", "danger")

            return redirect(url_for("create_legacy"))

        beneficiary = Beneficiary.query.filter_by(

            id=beneficiary_id,

            owner=username

        ).first()

        if not beneficiary:

            flash("Invalid beneficiary.", "danger")

            return redirect(url_for("create_legacy"))

        # --------------------------------

        # CHECK ASSET

        # --------------------------------

        asset = None

        if asset_id:

            asset = Asset.query.filter_by(

                id=asset_id,

                owner=username

            ).first()

            if not asset:

                flash("Invalid asset.", "danger")

                return redirect(url_for("create_legacy"))

        # --------------------------------

        # CHECK DOCUMENT

        # --------------------------------

        document = None

        if document_id:

            document = Document.query.filter_by(

                id=document_id,

                owner=username

            ).first()

            if not document:

                flash("Invalid document.", "danger")

                return redirect(url_for("create_legacy"))

        # --------------------------------

        # CHECK RELEASE DATE

        # --------------------------------

        if not release_date:

            flash("Please select a release date.", "danger")

            return redirect(url_for("create_legacy"))

        release_datetime = None

        # Try normal datetime-local format

        try:

            release_datetime = datetime.strptime(

                release_date,

                "%Y-%m-%dT%H:%M"

            )

        except ValueError:

            # Try format with seconds

            try:

                release_datetime = datetime.strptime(

                    release_date,

                    "%Y-%m-%dT%H:%M:%S"

                )

            except ValueError:

                flash(

                    "Invalid release date. Please select the date and time again.",

                    "danger"

                )

                return redirect(url_for("create_legacy"))

        # --------------------------------

        # RELEASE DATE MUST BE FUTURE

        # --------------------------------

        if release_datetime <= datetime.now():

            flash(

                "Release date must be in the future.",

                "danger"

            )

            return redirect(url_for("create_legacy"))

        # --------------------------------

        # CREATE LEGACY

        # --------------------------------

        legacy = Legacy(

            owner=username,

            beneficiary_id=beneficiary.id,

            asset_id=asset.id if asset else None,

            document_id=document.id if document else None,

            release_date=release_datetime,

            status="Pending"

        )

        db.session.add(legacy)

        db.session.commit()

        # --------------------------------

        # ACTIVITY LOG

        # --------------------------------

        log_activity(

            username,

            f"Legacy assignment created for {beneficiary.name}"

        )

        flash(

            "Legacy assignment created successfully!",

            "success"

        )

        return redirect(url_for("legacies"))

    return render_template(

        "create_legacy.html",

        beneficiaries=beneficiaries,

        assets=assets,

        documents=documents

    )

    # -----------------------------

    # GET USER'S DATA

    # -----------------------------

    beneficiaries_list = (

        Beneficiary.query

        .filter_by(owner=username)

        .order_by(Beneficiary.name.asc())

        .all()

    )

    assets_list = (

        Asset.query

        .filter_by(owner=username)

        .order_by(Asset.asset_name.asc())

        .all()

    )

    documents_list = (

        Document.query

        .filter_by(owner=username)

        .order_by(Document.filename.asc())

        .all()

    )

    if request.method == "POST":

        beneficiary_id = request.form.get(

            "beneficiary_id",

            ""

        ).strip()

        asset_id = request.form.get(

            "asset_id",

            ""

        ).strip()

        document_id = request.form.get(

            "document_id",

            ""

        ).strip()

        release_date_text = request.form.get(

            "release_date",

            ""

        ).strip()

        # -----------------------------

        # BENEFICIARY

        # -----------------------------

        try:

            beneficiary_id = int(

                beneficiary_id

            )

        except (ValueError, TypeError):

            flash(

                "Please select a valid beneficiary.",

                "error"

            )

            return redirect("/create-legacy")

        beneficiary = Beneficiary.query.filter_by(

            id=beneficiary_id,

            owner=username

        ).first()

        if not beneficiary:

            flash(

                "Selected beneficiary is invalid.",

                "error"

            )

            return redirect("/create-legacy")

        # -----------------------------

        # OPTIONAL ASSET

        # -----------------------------

        selected_asset_id = None

        if asset_id:

            try:

                selected_asset_id = int(

                    asset_id

                )

            except (ValueError, TypeError):

                flash(

                    "Invalid asset.",

                    "error"

                )

                return redirect("/create-legacy")

            asset = Asset.query.filter_by(

                id=selected_asset_id,

                owner=username

            ).first()

            if not asset:

                flash(

                    "Selected asset is invalid.",

                    "error"

                )

                return redirect("/create-legacy")

        # -----------------------------

        # OPTIONAL DOCUMENT

        # -----------------------------

        selected_document_id = None

        if document_id:

            try:

                selected_document_id = int(

                    document_id

                )

            except (ValueError, TypeError):

                flash(

                    "Invalid document.",

                    "error"

                )

                return redirect("/create-legacy")

            document = Document.query.filter_by(

                id=selected_document_id,

                owner=username

            ).first()

            if not document:

                flash(

                    "Selected document is invalid.",

                    "error"

                )

                return redirect("/create-legacy")

        # -----------------------------

        # RELEASE DATE

        # -----------------------------

        if not release_date_text:

            flash(

                "Please select a release date.",

                "error"

            )

            return redirect("/create-legacy")

        try:

            release_date = datetime.strptime(

                release_date_text,

                "%Y-%m-%d"

            )

        except ValueError:

            flash(

                "Invalid release date.",

                "error"

            )

            return redirect("/create-legacy")

        # -----------------------------

        # CREATE LEGACY

        # -----------------------------

        legacy = Legacy(

            owner=username,

            beneficiary_id=beneficiary.id,

            asset_id=selected_asset_id,

            document_id=selected_document_id,

            release_date=release_date,

            status="Pending"

        )

        db.session.add(legacy)

        db.session.commit()

        log_activity(

            username,

            "Legacy plan created."

        )

        flash(

            "Legacy plan created successfully.",

            "success"

        )

        return redirect("/legacies")

    return render_template(

        "create_legacy.html",

        beneficiaries=beneficiaries_list,

        assets=assets_list,

        documents=documents_list

    )

# ============================================================

# MY LEGACIES

# ============================================================

@app.route("/legacies")

def legacies():

    if "user" not in session:

        return redirect("/login")

    username = session["user"]

    legacies = (

        Legacy.query

        .filter_by(owner=username)

        .order_by(Legacy.release_date.asc())

        .all()

    )

    # Automatically update status when release date has passed

    current_time = datetime.now()

    for legacy in legacies:

        if legacy.release_date <= current_time:

            legacy.status = "Released"

        else:

            legacy.status = "Pending"

        # Get beneficiary

        legacy.beneficiary = Beneficiary.query.filter_by(

            id=legacy.beneficiary_id,

            owner=username

        ).first()

        # Get asset

        if legacy.asset_id:

            legacy.asset = Asset.query.filter_by(

                id=legacy.asset_id,

                owner=username

            ).first()

        else:

            legacy.asset = None

        # Get document

        if legacy.document_id:

            legacy.document = Document.query.filter_by(

                id=legacy.document_id,

                owner=username

            ).first()

        else:

            legacy.document = None

    db.session.commit()

    return render_template(

        "legacies.html",

        legacies=legacies

    )

    # -----------------------------

    # ADD RELATED OBJECTS

    # -----------------------------

    legacy_details = []

    for legacy in legacies_list:

        beneficiary = Beneficiary.query.filter_by(

            id=legacy.beneficiary_id,

            owner=username

        ).first()

        asset = None

        if legacy.asset_id:

            asset = Asset.query.filter_by(

                id=legacy.asset_id,

                owner=username

            ).first()

        document = None

        if legacy.document_id:

            document = Document.query.filter_by(

                id=legacy.document_id,

                owner=username

            ).first()

        legacy_details.append({

            "legacy": legacy,

            "beneficiary": beneficiary,

            "asset": asset,

            "document": document

        })

    return render_template(

        "legacies.html",

        legacies=legacy_details

    )

# ============================================================

# ACTIVITY LOG

# ============================================================

@app.route("/activity")

def activity():

    if "user" not in session:

        return redirect("/login")

    logs = (

        Activity.query

        .filter_by(username=session["user"])

        .order_by(Activity.date.desc())

        .all()

    )

    return render_template(

        "activity.html",

        logs=logs

    )

# ============================================================

# FORGOT PASSWORD

# ============================================================

@app.route("/forgot-password", methods=["GET", "POST"])

def forgot_password():

    if request.method == "GET":

        return render_template("forgot_password.html")

    username = request.form.get("username", "").strip()

    # Validate username

    if not username:

        flash("Please enter your username.", "danger")

        return redirect(url_for("forgot_password"))

    if not valid_username(username):

        flash("Invalid username format.", "danger")

        return redirect(url_for("forgot_password"))

    # Find user

    user = User.query.filter_by(username=username).first()

    if not user:

        flash("Username not found.", "danger")

        return redirect(url_for("forgot_password"))

    # Generate 6-digit OTP

    otp = str(random.randint(100000, 999999))

    # ========================================================

    # SAVE RESET INFORMATION

    # ========================================================

    session["reset_user_id"] = user.id

    session["reset_username"] = user.username

    session["reset_otp"] = otp

    session["reset_otp_expiry"] = (

        datetime.now() + timedelta(minutes=5)

    ).timestamp()

    # For college-project demo

    session["reset_otp_display"] = otp

    # Log activity

    log_activity(

        username,

        "Password reset OTP requested"

    )

    flash(

        "Reset OTP generated successfully.",

        "success"

    )

    return redirect(url_for("reset_password"))

# ============================================================

# RESET PASSWORD

# ============================================================

@app.route("/reset-password", methods=["GET", "POST"])

def reset_password():

    # Get reset information

    reset_user_id = session.get("reset_user_id")

    saved_otp = session.get("reset_otp")

    expiry = session.get("reset_otp_expiry")

    # Check reset session

    if not reset_user_id or not saved_otp or not expiry:

        flash(

            "Password reset session expired. Please try again.",

            "error"

        )

        return redirect(url_for("forgot_password"))

    # Check OTP expiry

    if datetime.now().timestamp() > expiry:

        session.pop("reset_user_id", None)

        session.pop("reset_username", None)

        session.pop("reset_otp", None)

        session.pop("reset_otp_expiry", None)

        session.pop("reset_otp_display", None)

        flash(

            "OTP expired. Please generate a new OTP.",

            "error"

        )

        return redirect(url_for("forgot_password"))

    # Find user

    user = User.query.get(reset_user_id)

    if not user:

        session.pop("reset_user_id", None)

        session.pop("reset_username", None)

        session.pop("reset_otp", None)

        session.pop("reset_otp_expiry", None)

        session.pop("reset_otp_display", None)

        flash(

            "User not found.",

            "error"

        )

        return redirect(url_for("forgot_password"))

    # ========================================================

    # POST - VERIFY OTP AND CHANGE PASSWORD

    # ========================================================

    if request.method == "POST":

        entered_otp = request.form.get(

            "otp",

            ""

        ).strip()

        new_password = request.form.get(

            "password",

            ""

        )

        confirm_password = request.form.get(

            "confirm_password",

            ""

        )

        # Check OTP again

        if entered_otp != saved_otp:

            flash(

                "Invalid OTP. Please enter the correct OTP.",

                "error"

            )

            return render_template(

                "reset_password.html",

                otp=saved_otp,

                show_otp=True

            )

        # Validate new password

        if not valid_password(new_password):

            flash(

                "Password must contain uppercase, lowercase, number and minimum 8 characters.",

                "error"

            )

            return render_template(

                "reset_password.html",

                otp=saved_otp,

                show_otp=True

            )

        # Confirm password

        if new_password != confirm_password:

            flash(

                "Passwords do not match.",

                "error"

            )

            return render_template(

                "reset_password.html",

                otp=saved_otp,

                show_otp=True

            )

        # ====================================================

        # UPDATE PASSWORD

        # ====================================================

        user.password = generate_password_hash(

            new_password

        )

        db.session.commit()

        # Log activity

        log_activity(

            user.username,

            "Password reset successfully."

        )

        # ====================================================

        # CLEAR RESET SESSION

        # ====================================================

        session.pop("reset_user_id", None)

        session.pop("reset_username", None)

        session.pop("reset_otp", None)

        session.pop("reset_otp_expiry", None)

        session.pop("reset_otp_display", None)

        flash(

            "Password reset successfully. Please login.",

            "success"

        )

        return redirect(url_for("login"))

    # ========================================================

    # GET - SHOW RESET PAGE

    # ========================================================

    return render_template(

        "reset_password.html",

        otp=saved_otp,

        show_otp=True

    )

# ============================================================

# LOGOUT

# ============================================================

@app.route("/logout")

def logout():

    username = session.get(

        "user"

    )

    if username:

        log_activity(

            username,

            "User logged out."

        )

    session.clear()

    flash(

        "You have been logged out successfully.",

        "success"

    )

    return redirect("/login")

# ============================================================

# ERROR HANDLERS

# ============================================================

@app.errorhandler(404)

def page_not_found(error):

    return """

    <h1>404 - Page Not Found</h1>

    <p>The requested page does not exist.</p>

    <a href="/">Go to Home</a>

    """, 404

@app.errorhandler(413)

def file_too_large(error):

    flash(

        "File is too large. Maximum size is 10 MB.",

        "error"

    )

    return redirect("/upload")

# ============================================================

# CREATE DATABASE TABLES

# ============================================================

with app.app_context():

    db.create_all()

# ============================================================

# RUN APPLICATION

# ============================================================

if __name__ == "__main__":

    print()

    print("=" * 60)

    print("       DIGITAL LEGACY SYSTEM")

    print("=" * 60)

    print("Server starting...")

    print("Open: http://127.0.0.1:5000")

    print("=" * 60)

    print()

    app.run(

        debug=False,

        use_reloader=False

    )