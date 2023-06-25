# Tableau de bord des enregistrements de lancement SpaceX

Ce projet est un tableau de bord interactif utilisant la bibliothèque Dash pour afficher des informations sur les lancements de SpaceX. Les données sont lues à partir d'un fichier CSV et présentées sous forme de diagrammes circulaires et de graphiques de dispersion interactifs.

## Structure du projet

- `spacex_launch_dash.csv` : Il s'agit du fichier de données qui contient des informations sur les lancements de SpaceX. 

- `main.py` : C'est le script principal qui crée l'application Dash et définit les callbacks pour les interactions de l'utilisateur.

## Flux de travail

1. L'application Dash commence par lire les données de lancement de SpaceX à partir du fichier CSV.

2. Une interface utilisateur est créée avec un en-tête, une liste déroulante pour sélectionner le site de lancement, un diagramme circulaire pour afficher le nombre total de lancements réussis par site, un curseur pour sélectionner une plage de valeurs de charge utile, et un graphique de dispersion pour montrer la corrélation entre la charge utile et le succès.

3. Deux callbacks sont définis pour mettre à jour les diagrammes en fonction des interactions de l'utilisateur avec la liste déroulante et le curseur.

## Comment utiliser

Pour exécuter l'application, assurez-vous que tous les fichiers requis sont présents dans le même répertoire et exécutez la commande suivante dans votre terminal :

```
python main.py
```

L'application sera accessible dans votre navigateur à l'adresse `localhost:8050`.

**Note :** Ce tableau de bord suppose que vous avez déjà installé les packages Python nécessaires, y compris pandas, dash, dash_core_components, dash_html_components et plotly.
