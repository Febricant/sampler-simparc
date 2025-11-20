# -*- coding: utf-8 -*-

import random

def HConsignes():
    """
        Initialise les paramètres aléatoires pour le setback et les variations horaires.
        Méthode permettant de déterminer les paramètres aléatoires liés au chauffage & à la climatisation.
            1 - self.dev1 : heure setback AM montee température
            2 - self.dev2 : heure setback AM descente température
            3 - self.dev3 : heure setback PM montee température
            4 - self.dev4 : heure setback PM descente température
                           ___TM____              ___TS____
                          |         |            |         |
              0h___TN___h1|       h2|____TJ____h3|       h4|___TN_____24h


            Nuit (temperature)
                           __TM_________TJ___________TS____
                          |                                |
              0h___TN __h1|       h2           h3        h4|___TN______24h

    """

    # Variations horaires aléatoires
    dev1 = random.uniform(-3, 3)  # randnb(3)
    dev2 = random.uniform(-3, 3)
    dev3 = random.uniform(-3, 3)
    dev4 = random.uniform(-3, 3)
    dev5 = random.uniform(-1, 1)
    dev6 = random.uniform(-1, 1)

    # Calcul des heures de changement de consigne
    h1 = 6 + 6 / 60 + (dev1 * 0.75 - dev2 * 0.25)
    h2 = 8 + (dev1 * 0.75 + dev2 * 0.25)
    h3 = 16 + 20 / 60 + (dev3 * 0.5 - dev4 * 0.5)
    h4 = min(22 + 17 / 60 + (dev3 * 0.5 + dev4 * 0.5), 23 + 59 / 60)
    return [h1, h2, h3, h4]
