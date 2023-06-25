# Projet de trading automatisé

Ce projet de trading automatisé utilise plusieurs modèles prédictifs pour générer des signaux de trading. Le script principal, `trading_logic.py`, exécute le flux de travail complet en intégrant les différentes parties du système. 

## Structure du projet

### Fichiers principaux

- `trading_logic.py` : Il contient la logique de trading principale. Il entraîne les modèles, génère les prédictions et crée ou ferme les positions en fonction de ces prédictions.
- `broker.py` : Il définit la classe PyRobot qui gère la connexion au broker, la création et la fermeture des positions de trading.
- `datasets.py` : Il contient plusieurs classes pour la préparation des données pour les différents modèles.
- `models.py` : Il contient plusieurs classes pour les modèles d'apprentissage automatique utilisés pour générer les prédictions.

### Modules

1. **RNN (Réseau de neurones récurrent)**: Utilisé pour prédire les mouvements de prix sur plusieurs paires de devises. Les variables d'entrainement et de test sont définies dans le script principal.

2. **Régression multivariée**: Un autre modèle utilisé pour prédire les mouvements de prix. Il utilise plusieurs variables explicatives pour prédire chaque paire de devises.

3. **MA (Moving Average) Ridge**: Ce modèle utilise une régression ridge sur des données de moyenne mobile pour prédire les mouvements de prix.

4. **RSI (Relative Strength Index)**: Il s'agit d'un indicateur technique utilisé pour générer des signaux de trading.

5. **Interest Rates**: Utilise les taux d'intérêt de différents pays pour générer des signaux de trading.

## Flux de travail

1. Le script principal commence par initialiser les variables nécessaires et créer une instance de PyRobot pour gérer la connexion au broker.

2. Il vérifie ensuite si le marché est ouvert et si l'heure actuelle est différente de la dernière heure connue.

3. Si le marché est ouvert, il entraîne chaque modèle si le nombre de prédictions effectuées jusqu'à présent est supérieur à un certain seuil.

4. Il génère ensuite des prédictions pour chaque modèle et les combine en utilisant des poids prédéfinis pour générer un signal de trading final.

5. En fonction de ce signal, il ferme les positions existantes et crée de nouvelles positions.

6. Enfin, il met à jour l'heure de la dernière prédiction et recommence le processus.

## Comment utiliser

Pour exécuter le script principal, assurez-vous que tous les fichiers requis sont présents dans le même répertoire et exécutez la commande suivante dans votre terminal :

```
python trading_logic.py
```

Assurez-vous d'avoir installé tous les packages nécessaires.

**Note:** Vous devrez également remplacer les variables `login_mt5`, `mdp_mt5` et `server` par vos propres identifiants de connexion pour votre broker.



Le module `broker.py` contient la classe `PyRobot`, qui est conçue pour interagir avec la plateforme de trading MetaTrader 5. Cette classe permet de créer une session de trading, de vérifier si le marché est ouvert, de gérer le portefeuille de positions, de créer des ordres d'entrée et de sortie, et d'annuler des ordres.

Voici une description des principales méthodes de la classe :

- `__init__(self, client_id: int, client_mdp: str, trading_serveur: str, leverage: float, tickers: list)`: Le constructeur de la classe. Il initialise les paramètres du robot, y compris l'identifiant du client, le mot de passe du client, le serveur de trading, le levier financier et la liste des tickers à trader.

- `_create_session(self)`: Cette méthode initialise une session de trading avec MetaTrader 5 en utilisant les identifiants du client et le serveur de trading.

- `market_open(self) -> bool`: Cette méthode vérifie si le marché est ouvert. Elle renvoie `True` si le marché est ouvert et `False` sinon.

- `liquidity_hours(self) -> bool`: Cette méthode vérifie si le marché est dans les heures de liquidité. Elle renvoie `True` si c'est le cas et `False` sinon.

- `get_portfolio_pos_time(self)`: Cette méthode renvoie un dictionnaire contenant les positions actuelles du portefeuille et le temps depuis l'ouverture de chaque position.

- `create_entry_trades(self, dict_pos: dict)`: Cette méthode crée des ordres d'entrée sur le marché en fonction d'un dictionnaire de positions souhaitées.

- `create_close_trades(self, all_preds)`: Cette méthode crée des ordres de clôture pour les positions actuelles qui ne correspondent pas aux prédictions fournies.

- `cancel_order(self)`: Cette méthode annule tous les ordres en attente.

- `leverage_to_volume(self, ticker)`: Cette méthode convertit le levier financier en volume de trading pour un ticker donné.

La classe `PyRobot` est un outil puissant pour automatiser le trading sur MetaTrader 5. Elle peut être utilisée pour créer des stratégies de trading algorithmique et exécuter des ordres de trading en fonction de signaux de trading générés par un modèle de prédiction.




Le module `datasets.py` contient plusieurs classes qui sont utilisées pour récupérer et préparer les données pour le trading algorithmique. Ces classes interagissent avec les plateformes de trading MetaTrader 5 et TradingView pour récupérer les données historiques des prix des actifs financiers.

Voici une description des principales classes et méthodes du module :

- `GetCleanDatas`: Cette classe de base est utilisée pour récupérer les données historiques des prix à partir de MetaTrader 5 et TradingView. Elle définit les méthodes `get_clean_mt5_data` et `get_clean_tv_data` qui prennent en entrée une liste de tickers et un nombre de barres de prix, et renvoient un DataFrame pandas contenant les données de prix nettoyées.

- `RNNDatas`: Cette classe hérite de `GetCleanDatas` et est utilisée pour préparer les données pour les réseaux de neurones récurrents (RNN). Elle définit les méthodes `get_returns`, `create_multivariate_rnn_data`, `get_train_data` et `get_predict_data` qui sont utilisées pour calculer les rendements des actifs, créer des données multivariées pour les RNN, obtenir les données d'entraînement et obtenir les données de prédiction, respectivement.

- `GetMultivariateDatas`: Cette classe hérite également de `GetCleanDatas` et est utilisée pour préparer les données pour les modèles multivariés. Elle définit les méthodes `get_multivariate_data`, `get_train_data` et `get_predict_data` qui sont utilisées pour obtenir les données multivariées, obtenir les données d'entraînement et obtenir les données de prédiction, respectivement.

- `GetMAData`: Cette classe hérite de `GetCleanDatas` et est utilisée pour préparer les données pour les modèles basés sur les moyennes mobiles. Elle définit les méthodes `get_ma_datas`, `get_train_data` et `get_predict_data` qui sont utilisées pour obtenir les données des moyennes mobiles, obtenir les données d'entraînement et obtenir les données de prédiction, respectivement.

Ces classes sont conçues pour être flexibles et peuvent être utilisées avec différents types de modèles de trading algorithmique. Elles permettent de récupérer et de préparer les données de manière efficace et structurée, ce qui facilite le développement et le déploiement de stratégies de trading algorithmique.





Le module `models.py` contient plusieurs classes qui définissent les modèles de trading algorithmique utilisés par le bot de trading. Ces modèles sont utilisés pour prédire les mouvements futurs des prix des actifs financiers et pour générer des signaux de trading.

Voici une description des principales classes et méthodes du module :

- `MultivariateLSTM`: Cette classe définit un modèle de réseau de neurones récurrents (RNN) à long terme (LSTM) pour la prédiction multivariée. Le modèle est entraîné avec la méthode `train_model` et utilisé pour faire des prédictions avec la méthode `predict`.

- `MultivariateLinearRegression`: Cette classe définit un modèle de régression linéaire multivariée. Le modèle est entraîné avec la méthode `train_model` et utilisé pour faire des prédictions avec la méthode `predict`.

- `MaRidge`: Cette classe définit un modèle de régression Ridge pour les moyennes mobiles. Le modèle est entraîné avec la méthode `train_model` et utilisé pour faire des prédictions avec la méthode `predict`.

- `rsi_signal`: Cette fonction calcule l'indice de force relative (RSI) pour un ensemble de données de prix et génère un signal de trading basé sur le RSI.

- `interest_rates_signal`: Cette fonction calcule les écarts de taux d'intérêt pour un ensemble de paires de devises et génère un signal de trading basé sur ces écarts.

Ces modèles et fonctions sont conçus pour être flexibles et peuvent être utilisés avec différents types de données de marché. Ils permettent de générer des signaux de trading précis et opportuns, ce qui facilite le développement et le déploiement de stratégies de trading algorithmique.



