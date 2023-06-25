# README

Le module `FTMOLeverageOptimazation` est une classe Python conçue pour optimiser le levier financier dans le cadre du test FTMO (Funding for Serious Traders). Le test FTMO est un défi de trading qui, s'il est réussi, permet aux traders de gérer un compte de trading financé.

La classe `FTMOLeverageOptimazation` contient plusieurs méthodes pour simuler des scénarios de trading, calculer les probabilités de réussite du test FTMO et optimiser le levier financier pour maximiser ces probabilités.

Voici une description des principales méthodes de la classe :

- `__init__(self, sigma, mu, n_sim, S0)`: Le constructeur de la classe. Il initialise les paramètres du modèle, y compris la volatilité (`sigma`), le rendement attendu (`mu`), le nombre de simulations à effectuer (`n_sim`) et le prix initial de l'actif (`S0`).

- `get_gbms(self, time_in_month, leverage)`: Cette méthode génère des trajectoires de mouvement brownien géométrique, qui sont utilisées pour simuler les variations de prix de l'actif. Le paramètre `time_in_month` spécifie la durée de la simulation en mois, et `leverage` est le levier financier utilisé.

- `get_probas(self, leverage, time_in_month, target, dd_max)`: Cette méthode calcule la probabilité de réussir le test FTMO en fonction du levier financier, de la durée du test, de l'objectif de rendement et du drawdown maximum autorisé.

- `objective(self, leverage, time_in_month, target, dd_max)`: Cette méthode est la fonction objectif qui est minimisée lors de l'optimisation du levier financier. Elle renvoie la négation de la probabilité de réussite du test FTMO.

- `optimize_leverage(self)`: Cette méthode effectue l'optimisation du levier financier. Elle utilise la méthode de minimisation de Powell pour trouver le levier qui maximise la probabilité de réussite du test FTMO.

Après avoir exécuté la méthode `optimize_leverage`, les attributs `first_best_leverage`, `first_best_proba`, `second_best_leverage`, `second_best_proba` et `total_proba` de l'objet `FTMOLeverageOptimazation` contiennent respectivement le meilleur levier pour le premier et le second mois du test, les probabilités de réussite correspondantes et la probabilité totale de réussite du test.