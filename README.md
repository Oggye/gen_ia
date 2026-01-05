# gen_ia

Dashboard Streamlit pour visualiser les sessions : top des langues, évolution du nombre de sessions, durée moyenne, répartition par service, indicateurs qualité, interactions patient/praticien et notes praticiens.

## Lancer l'application

1. Installer les dépendances :

```bash
pip install -r requirements.txt
```

2. Lancer l'application Streamlit :

```bash
streamlit run app.py
```

Le fichier `sessions_dataset_320.csv` doit être présent à la racine du projet.


## Remarques
- Si votre dataset possède une colonne contenant des `notes` textuelles des praticiens, ajoutez-la et nommez-la en incluant le mot `note` dans le nom (ex: `note_praticien_text`) pour qu'elle apparaisse dans la section "Notes praticiens" de l'interface.
