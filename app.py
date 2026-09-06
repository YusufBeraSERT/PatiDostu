# -*- coding: utf-8 -*-
import os
import uuid
import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "patidostu_gercek_sosyal_medya_key"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'patidostu.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    points = db.Column(db.Integer, default=0)

class Feeding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    note = db.Column(db.Text, nullable=True)
    image_filename = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.String(50), nullable=False)

class LostPet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    pet_type = db.Column(db.String(50), nullable=False)
    last_seen = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    image_filename = db.Column(db.String(200), nullable=False)

class Adoption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    breed = db.Column(db.String(50), nullable=False)
    age = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    image_filename = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

# DİL SÖZLÜĞÜ (TR, EN, DE, ES)
TRANSLATIONS = {
    'tr': {
        'nav_feed': 'Besleme Akışı',
        'nav_adopt': 'Yuva Arıyorum',
        'nav_lost': 'Kayıp İlanları',
        'login': 'Giriş Yap',
        'logout': 'Çıkış',
        'feed_title': 'Bugün hangi canı doyurdun? 🍖',
        'feed_btn': 'Akışa Gönder 🐾',
        'adopt_title': 'Yeni bir dost edin 🏡',
        'adopt_btn': 'İlan Oluştur',
        'lost_title': 'Kayıp İlanı Ver 🚨',
        'lost_btn': 'Acil İlan Ekle',
        'upload_label': 'Fotoğraf Seç:',
        'empty_feed': 'Henüz paylaşım yapılmadı, ilk fotoğrafı sen gönder!',
        'pts_tag': 'Puan'
    },
    'en': {
        'nav_feed': 'Feeding Activity',
        'nav_adopt': 'Adopt a Pet',
        'nav_lost': 'Lost Pets',
        'login': 'Sign In',
        'logout': 'Logout',
        'feed_title': 'Who did you feed today? 🍖',
        'feed_btn': 'Post to Feed 🐾',
        'adopt_title': 'Find a new furry friend 🏡',
        'adopt_btn': 'Create Listing',
        'lost_title': 'Report Lost Pet 🚨',
        'lost_btn': 'Post Urgent Alert',
        'upload_label': 'Select Photo:',
        'empty_feed': 'No posts yet. Be the first to share!',
        'pts_tag': 'Pts'
    },
    'de': {
        'nav_feed': 'Fütterungen',
        'nav_adopt': 'Adoptionen',
        'nav_lost': 'Vermisst',
        'login': 'Anmelden',
        'logout': 'Abmelden',
        'feed_title': 'Wen hast du heute gefüttert? 🍖',
        'feed_btn': 'Beitrag Teilen 🐾',
        'adopt_title': 'Finde einen Freund 🏡',
        'adopt_btn': 'Anzeige Erstellen',
        'lost_title': 'Haustier Vermisst 🚨',
        'lost_btn': 'Meldung Erstellen',
        'upload_label': 'Foto Auswählen:',
        'empty_feed': 'Noch keine Beiträge vorhanden.',
        'pts_tag': 'Pkt'
    },
    'es': {
        'nav_feed': 'Alimentación',
        'nav_adopt': 'Adopción',
        'nav_lost': 'Mascotas Perdidas',
        'login': 'Iniciar Sesión',
        'logout': 'Salir',
        'feed_title': '¿A quién alimentaste hoy? 🍖',
        'feed_btn': 'Publicar 🐾',
        'adopt_title': 'Encuentra un amigo 🏡',
        'adopt_btn': 'Crear Anuncio',
        'lost_title': 'Mascota Perdida 🚨',
        'lost_btn': 'Alerta Urgente',
        'upload_label': 'Seleccionar Foto:',
        'empty_feed': '¡Aún no hay publicaciones!',
        'pts_tag': 'Pts'
    }
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return filename
    return None

@app.route("/")
def index():
    page = request.args.get("page", "feed")
    lang = request.args.get("lang", "tr")

    if lang not in TRANSLATIONS:
        lang = "tr"

    feedings = Feeding.query.order_by(Feeding.id.desc()).all()
    lost_pets = LostPet.query.order_by(LostPet.id.desc()).all()
    adoptions = Adoption.query.order_by(Adoption.id.desc()).all()

    current_user = session.get("user")

    return render_template(
        "index.html",
        page=page,
        lang=lang,
        t=TRANSLATIONS[lang],
        feedings=feedings,
        lost_pets=lost_pets,
        adoptions=adoptions,
        current_user=current_user
    )

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "Dostumuz")
    email = request.form.get("email", "user@patidostu.com")
    
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(username=username, email=email)
        db.session.add(user)
        db.session.commit()
    
    session["user"] = {"id": user.id, "username": user.username, "email": user.email, "points": user.points}
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))

@app.route("/add_feeding", methods=["POST"])
def add_feeding():
    lang = request.args.get("lang", "tr")
    username = request.form.get("username") or (session["user"]["username"] if "user" in session else "Pati Dostu")
    location = request.form.get("location")
    note = request.form.get("note")
    file = request.files.get("file")

    if location and file:
        filename = save_uploaded_file(file)
        if filename:
            now_str = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
            new_feed = Feeding(
                username=username,
                location=location,
                note=note,
                image_filename=filename,
                created_at=now_str
            )
            db.session.add(new_feed)

            if "user" in session:
                user = User.query.get(session["user"]["id"])
                if user:
                    user.points += 50
                    db.session.commit()
                    session["user"]["points"] = user.points
                    session.modified = True
            else:
                db.session.commit()

    return redirect(url_for("index", page="feed", lang=lang))

@app.route("/add_lost", methods=["POST"])
def add_lost():
    lang = request.args.get("lang", "tr")
    title = request.form.get("title")
    pet_type = request.form.get("pet_type")
    last_seen = request.form.get("last_seen")
    phone = request.form.get("phone")
    file = request.files.get("file")

    if file and title and phone:
        filename = save_uploaded_file(file)
        if filename:
            new_lost = LostPet(
                title=title,
                pet_type=pet_type,
                last_seen=last_seen,
                phone=phone,
                image_filename=filename
            )
            db.session.add(new_lost)
            db.session.commit()

    return redirect(url_for("index", page="lost", lang=lang))

@app.route("/add_adopt", methods=["POST"])
def add_adopt():
    lang = request.args.get("lang", "tr")
    name = request.form.get("name")
    breed = request.form.get("breed")
    age = request.form.get("age")
    location = request.form.get("location")
    contact = request.form.get("contact")
    file = request.files.get("file")

    if file and name and contact:
        filename = save_uploaded_file(file)
        if filename:
            new_adopt = Adoption(
                name=name,
                breed=breed,
                age=age,
                location=location,
                contact=contact,
                image_filename=filename
            )
            db.session.add(new_adopt)
            db.session.commit()

    return redirect(url_for("index", page="adopt", lang=lang))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
