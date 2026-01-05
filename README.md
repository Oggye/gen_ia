# gen_ia

**Dashboard Streamlit** pour analyser les sessions médicales (top langues, évolution des sessions, durée moyenne, répartition par service, indicateurs qualité, interactions patient/praticien, notes praticiens).

---

## 🚀 Prérequis
- Python 3.10+ (ou version récente compatible)
- Avoir `pip` installé
- Le fichier de données `sessions_dataset_320.csv` présent à la racine du projet

## 🧰 Installation
1. (Optionnel mais recommandé) Créez et activez un environnement virtuel :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # PowerShell
# ou .\.venv\Scripts\activate  # CMD
```

2. Installez les dépendances :

```bash
pip install -r requirements.txt
```

> Si vous avez déjà installé `streamlit` séparément, assurez-vous qu'il est installé dans l'environnement actif.

## ▶️ Lancer l'application

```bash
streamlit run app.py
```

puis ouvrez dans votre navigateur : `http://localhost:8501` (ou l'URL affichée par Streamlit).

---

## 🔧 Dépannage rapide
- Erreur `ModuleNotFoundError: No module named 'streamlit'` : activez l'environnement virtuel puis `pip install -r requirements.txt`.
- `streamlit: The term 'streamlit' is not recognized` : lancez avec `python -m streamlit run app.py` ou activez l'env.
- PowerShell bloque l'exécution d'un script `.ps1` :

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
```

- Si la date affichée dans le filtre semble incorrecte, vérifiez l'horloge et fuseau horaire du système.

---

## ✅ Fonctionnalités
- Filtres : période (avec interdiction des dates futures), service(s), langue(s), device, note minimale, qualité minimale, recherche dans les notes praticiens
- Visualisations : top langues, évolution temporelle (Jour/Semaine/Mois), durée moyenne par service, répartition par service, distribution qualité, interactions (boxplot)
- Section `Notes praticiens` : tableau des colonnes numériques contenant `note` (session_id, service, date)
- Export : téléchargement CSV des données filtrées (dates exportées au format date seulement)

---

## 💡 Conseils
- Pour que les notes textuelles s'affichent, ajoutez une colonne contenant du texte et contenant `note` dans son nom (ex: `note_praticien_text`).
- Vous pouvez modifier/étendre `app.py` pour ajouter d'autres KPI ou filtres selon vos besoins.

---

## 📬 Contact
Pour toute question sur les données ou pour ajouter des métriques, contactez l'équipe données.

