from flask import Blueprint, render_template, request
from math import ceil

# Créer un blueprint pour gérer les routes
main = Blueprint("main", __name__)


# Fonction pour calculer le BAC
def calcul_bac(volume, taux_alcool, poids, sexe, heures):
    # Calcul de l'alcool pur consommé en grammes
    alcool_pur = volume * (taux_alcool / 100) * 0.8
    # Calcul du BAC
    r = 0.7 if sexe == "Homme" else 0.6
    bac = (alcool_pur * 10) / (poids * r) - (heures * 0.015)
    return bac


# Fonction pour calculer le temps avant de pouvoir conduire
def temps_aptitude(bac):
    if bac <= 0:
        return 0
    return ceil(bac / 0.015)


# Route principale pour l'interface utilisateur
@main.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Récupérer les données du formulaire
        volume = float(request.form["volume"])
        taux_alcool = float(request.form["taux_alcool"])
        poids = float(request.form["poids"])
        sexe = request.form["sexe"]
        heures = float(request.form["heures"])

        # Calcul du BAC
        bac = calcul_bac(volume, taux_alcool, poids, sexe, heures)

        # Calcul du temps avant d'être apte à conduire
        temps = temps_aptitude(bac)

        return render_template("bac_calc.html", bac=bac, temps=temps)

    return render_template("bac_calc.html", bac=None, temps=None)
