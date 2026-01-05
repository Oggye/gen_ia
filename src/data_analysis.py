# Importation des bibliothèques
import pandas as pd

# Chargement des données
df = pd.read_csv('./Data/sessions_dataset_320.csv')

# Aperçu des 5 premières lignes
print(df.head())

# Affichage de la taille
print(f"\nTaille du dataset: {df.shape[0]} lignes, {df.shape[1]} colonnes\n")

# Affichage des types
print("Les types du dataset:")
print(df.dtypes, "\n")

# Vérification des doublons
print(f"Doublons complets: {df.duplicated().sum()}\n")
# Supprimer les doublons
df = df.drop_duplicates()

# Vérification des valeurs manquantes
print("Les valeurs manquantes au total sont de :", df.isnull().sum().sum(), "\n")
# Supprimer les lignes avec valeurs manquantes
df = df.dropna()

# Convertir date en datetime
df['date'] = pd.to_datetime(df['date'])

# Vérifier les types finaux
print("\nLes types du dataset après nettoyage:")
print(df.dtypes)

#Vérification finale
print(f"\nDataset nettoyé final: {df.shape[0]} lignes, {df.shape[1]} colonnes")
print(f"Doublons restants: {df.duplicated().sum()}")
print(f"Valeurs manquantes restantes: {df.isnull().sum().sum()}")

# Moyenne de la durée par service
print(df.groupby('service')[['duree_minutes', 'note_praticien', 'qualite_score']].mean())

# Durée moyenne
print("\nDurée moyenne de toutes les sessions :", df['duree_minutes'].mean())

# Evaluation du nombre de sessions par jour
sessions_par_jour = df.groupby(df['date'].dt.date).size()
print("\nEvolution du nombre de sessions par jour :")
print(sessions_par_jour)
 
# Interactions patient/praticien
print("\nNombre de sessions par patient :")
print(df[['interactions_patient', 'interactions_praticien']].mean())

# Indicateurs qualité
print("\nIndicateurs qualité moyens :")
print(df[['note_praticien', 'qualite_score', 'segments_non_reconnus']].mean())


