# Rayonnement_TH-BCE
Ce répertoire contient les codes python permettant de réaliser une mesure d'irradiance sur une surface suivant la méthode de calcul de rayonnement présenté dans l'annexe III de la RE2020, méthode de calcul TH-BCE.
Réalisé dans le cadre d'un projet d'étude, j'ai utilisé ces codes afin de calculer les irradiances de différentes scènes urbaines.
Sont volontairement exclu du code : 
- le calcul différencié pour les baies vitrés
- la gestions des arbres à feuilles caduques
- la gestion des masques lointain dont on fait l'hypothèse qu'ils sont supplantés par les masques proches en conditions urbaines

La géométrie est extraite de SketchUp sous forme de fichier .csv dont vous trouverez les exemples dans ce répertoire.
Les données météorologiques d'entrée nécessaire sont : 
- le rayonnement diffus DHI
- Le rayonnement direct horizontal DNI
- l'azimut du soleil psi
- l'angle du soleil gamma
- l'heure de l'année
Un exemple de fichier météo correspondant à un TMY de Trappes est donné 
