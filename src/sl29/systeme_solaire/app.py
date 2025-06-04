"""Un module pour l'application"""

import json
import os
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename



app = Flask(__name__)


# Chargement des données
with open('data/planets.json', 'r', encoding='utf-8') as f:
    planets = json.load(f)
    print(planets)

with open('data/satellites.json', 'r', encoding='utf-8') as f:
    satellites = json.load(f)

@app.route('/')
def index():
    """Page d'accueil montrant comment les paramètres fonctionnent"""
    return render_template('index.html', planets=planets)

@app.route('/planete')
def show_planet():
    """Démontre l'utilisation de request.args.get()"""
    # Récupération du paramètre 'id' de la requête
    planet_id = request.args.get('id', type=int)

    # Vérification si le paramètre existe et est valide
    if planet_id is None:
        return "Erreur: Le paramètre 'id' est requis. Exemple: /planete?id=3", 400

    # Recherche de la planète
    planet_data = get_planet_by_id(planet_id)
    if not planet_data:
        return f"Erreur: Aucune planète trouvée avec l'ID {planet_id}", 404

    # Récupération des satellites
    planet_satellites = [s for s in satellites if s['planetId'] == planet_id]

    return render_template('planet.html',
                         planet=planet_data,
                         satellites=planet_satellites,
                         request_args=dict(request.args))  # Pour démo pédagogique

@app.route('/satellite')
def show_satellite():
    """Montre comment gérer plusieurs paramètres"""

    # A FAIRE

    # récupérer l'id du sattelite depuis la requete
    satellite_id = request.args.get('id', type=int)
    # Si l'id n'est pas trouvé, retourner un message d'erreur et un status 404
    if satellite_id is None:
        return "Erreur: Le paramètre 'id' est requis. Exemple: /planete?id=3", 404

    # Récuperer les données du satellite
    satellite_data = get_satellite_by_id(satellite_id)
    # Si aucune donnée trouvée, retourner un message d'erreur et un status 404
    if not satellite_data:
        return f"Erreur: Aucun satellite trouvé avec l'ID {satellite_id}", 404


    # récupérer les données de la planète associée.
    planet_satellite = get_planet_by_id(satellites[satellite_id]["planetId"])
    
    # retourner le template 'satellite.html' avec les variables:
    # - satellite
    # - planet

    return render_template('satellite.html',
                         satellite=satellite_data,
                         planet=planet_satellite,
                         request_args=dict(request.args))


def get_planet_by_id(planet_id:int)->dict|None:
    """Retourne la planète sous forme de dictionnaire

    :param planet_id: l'id de la planète
    :type planet_id: int
    :return:la planète ou None
    :rtype: dict|None
    """
    for planet in planets:
        if planet['id'] == planet_id:
            return planet
    return None  # Si aucune planète trouvée

def get_satellite_by_id(satellite_id:int)->dict|None:
    """Retourne le satellite sous forme de dictionnaire

    :param satellite_id: l'id deu satellite
    :type satellite_id: int
    :return:le satellite ou None
    :rtype: dict|None
    """
    for satellite in satellites:
        if satellite['id'] == satellite_id:
            return satellite
    return None  # Si aucun satellite trouvée

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

class PhotoForm(FlaskForm):
    photo = FileField(validators=[FileRequired()])

@app.route('/planete/upload', methods=['GET', 'POST'])
def upload():
    form = PhotoForm()

    planet_id = request.args.get('id', type=int)
    print(planet_id)

    if form.validate_on_submit():
        print("ok")
        f = form.photo.data
        filename = secure_filename(f.filename)
        name, extension = filename.split(".")
        planete_filename = f"planete_{planet_id}.{extension}"
        print(f"filname = {planete_filename}")
        new_path = os.path.join('static/img/', planete_filename)
        print(f"new path = {new_path}")
        f.save(new_path)
        print(f"extension = {extension}")
        planet_id = request.args.get('id', type=int)
        planet_data = get_planet_by_id(planet_id)
        if "picture_name" not in planet_data:
            planet_data["pictureName"]=""
        planet_data["pictureName"]=planete_filename
        with open('data/planets.json', 'r', encoding='utf-8') as f:
            planets = json.load(f)
            planets[planet_id]=planet_data
        with open('data/planets.json', 'w', encoding='utf-8') as f:
            json.dump(planets, f)

        return redirect(f"/planete?id={planet_id}")

    return render_template('upload.html', form=form)



if __name__ == '__main__':
    app.run(debug=True)
