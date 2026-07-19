from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db, init_db

app = Flask(__name__)
app.secret_key = "unisignal_secret_2025"
 
CODE_ADMIN = "ADMIN2025"

#Route 1 : GET/  afficher la landing page
@app.route("/")
def landing():
    return render_template("landing.html")

#Route 2 : GET/Signaler  afficher le formulaire
@app.route("/signaler")
def signaler():
    return render_template("signaler.html")

#Route 3 : POST/Signaler  traiter le formulaire
@app.route("/signaler", methods=["POST"])
#Etape 1 : Récupérer les données du formulaire
def signaler_post():
    categorie = request.form.get("categorie", "")
    description = request.form.get("description", "")
    lieu = request.form.get("lieu", "")
    solution_proposee = request.form.get("solution_proposee", "")

#Etape 2 : Vérifier que les champs obligatoires sont remplis
    if categorie.strip() == "" or description.strip() == "" or lieu.strip() == "":
        error = "Veuillez remplir tous les champs obligatoires."
        return render_template(
            "signaler.html",
            error=error,
            categorie=categorie,
            description=description,
            lieu=lieu,
            solution_proposee=solution_proposee,
        )

#Etape 3 : Insérer les données dans la base de données
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO signalements (categorie, description, lieu, solution_proposee)
            VALUES (?, ?, ?, ?)
            """,
            (categorie, description, lieu, solution_proposee),
        )
        conn.commit()

    return redirect(url_for("confirmation"))


#Route 4 : GET/Confirmation  afficher la page de confirmation
@app.route("/confirmation")
def confirmation():
    return render_template("confirmation.html")

#Route 5 : GET/liste  afficher la liste des signalements
@app.route("/liste")
def liste():
    with get_db() as conn:
        signalements = conn.execute(
            "SELECT * FROM signalements ORDER BY date_creation DESC"
        ).fetchall()
    return render_template("liste.html", signalements=signalements)

#Route 6 : GET/admin/inscription  afficher le formulaire d'inscription
@app.route("/admin/inscription")
def admin_inscription():
    return render_template("admin/inscription.html")

#Route 7 : POST/admin/inscription  creer un compte administrateur
@app.route("/admin/inscription", methods=["POST"])
#Etape 1 : Récupérer les données du formulaire
def admin_inscription_post():
    nom = request.form.get("nom", "")
    mot_de_passe = request.form.get("mot_de_passe", "")
    confirmation = request.form.get("confirmation", "")
    code_secret = request.form.get("code_secret", "")

#Etape 2 : Vérifier que les champs obligatoires sont remplis
    if nom.strip() == "" or mot_de_passe.strip() == "" or confirmation.strip() == "" or code_secret.strip() == "":
        error = "Veuillez remplir tous les champs obligatoires."
        return render_template(
            "admin/inscription.html",
            error=error,
            nom=nom,
            mot_de_passe=mot_de_passe,
            confirmation=confirmation,
            code_secret=code_secret,
        )
    
#Etape 3 : Vérifier que le code secret est correct
    if code_secret != CODE_ADMIN:
        error = "Code secret incorrect."
        return render_template(
            "admin/inscription.html",
            error=error,
            nom=nom,
            mot_de_passe=mot_de_passe,
            confirmation=confirmation,
            code_secret=code_secret,
        )

#Etape 4 : Vérifier que les mots de passe correspondent
    if mot_de_passe != confirmation:
        error = "Les mots de passe ne correspondent pas."
        return render_template(
            "admin/inscription.html",
            error=error,
            nom=nom,
            mot_de_passe=mot_de_passe,
            confirmation=confirmation,
            code_secret=code_secret,
        )
    
#Etape 5 : Vérifier que le nom d'utilisateur n'existe pas déjà
    with get_db() as conn:
        existant= conn.execute(
            "SELECT id FROM admins WHERE nom = ?", (nom,)
        ).fetchone()
    if existant:
        error = "Ce nom d'utilisateur existe déjà."
        return render_template(
            "admin/inscription.html",
            error=error,
            nom=nom,
            mot_de_passe=mot_de_passe,
            confirmation=confirmation,
            code_secret=code_secret,
        )
    
    #Etape 6 : Hasher le mot de passe et l'insérer dans la base de données
    mot_de_passe_hache = generate_password_hash(mot_de_passe)
    with get_db() as conn:
        conn.execute(
            "INSERT INTO admins (nom, mot_de_passe) VALUES (?, ?)",
            (nom, mot_de_passe_hache),
        )
        conn.commit()

    #Etape 7 : Rediriger vers la page de connexion
    return redirect(url_for("admin_connexion"))

#Route 8 : GET/admin/connexion  afficher le formulaire de connexion
@app.route("/admin/connexion")
def admin_connexion():
    return render_template("admin/connexion.html")

#Route 9 : POST/admin/connexion  verifier et ouvrir la session de l'administrateur
@app.route("/admin/connexion", methods=["POST"])
#Etape 1 : Lire nom et mot de passe
def admin_connexion_post():
    nom = request.form.get("nom", "")
    mot_de_passe = request.form.get("mot_de_passe", "")

#Etape 2 : Vérifier que les champs obligatoires sont remplis
    if nom.strip() == "" or mot_de_passe.strip() == "":
        error = "Veuillez remplir tous les champs obligatoires."
        return render_template(
            "admin/connexion.html",
            error=error,
            nom=nom,
            mot_de_passe=mot_de_passe,
        )
#Etape 3 : Vérifier que le nom d'utilisateur existe et que le mot de passe est correct
    with get_db() as conn:
        admin = conn.execute(
            "SELECT * FROM admins WHERE nom = ?", (nom,)
        ).fetchone()

    if not admin or not check_password_hash(admin["mot_de_passe"], mot_de_passe):
        error = "Nom ou mot de passe incorrect."
        return render_template("admin/connexion.html", error=error, nom=nom)
    
#Etape 4 : Ouvrir la session de l'administrateur
    session["connecte"] = True
    session["admin_nom"] = admin["nom"]
    return redirect(url_for("admin_dashboard"))

# Route 10 : GET /admin/dashboard — afficher le tableau de bord de l'administrateur
@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("connecte"):
        return redirect(url_for("admin_connexion"))

    with get_db() as conn:
        signalements = conn.execute(
            "SELECT * FROM signalements ORDER BY date_creation DESC"
        ).fetchall()

    return render_template(
        "admin/dashboard.html",
        nom=session.get("admin_nom"),
        signalements=signalements,
    )
# Route 11 : POST /admin/statut  modifier le statut d'un signalement
@app.route("/admin/statut", methods=["POST"])
def admin_statut():
    if not session.get("connecte"):
        return redirect(url_for("admin_connexion"))

    id_signalement = request.form.get("id")
    nouveau_statut = request.form.get("statut")

    with get_db() as conn:
        conn.execute(
            "UPDATE signalements SET statut = ? WHERE id = ?",
            (nouveau_statut, id_signalement),
        )
        conn.commit()

    return redirect(url_for("admin_dashboard"))

# Route 12 : GET /admin/deconnexion — déconnecter l'admin
@app.route("/admin/deconnexion")
def admin_deconnexion():
    session.clear()
    return redirect(url_for("landing"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)