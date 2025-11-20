Module LTE-Sampler-Residential.src.utils.sampler.utils
======================================================

Functions
---------

`HConsignes()`
:   Initialise les paramètres aléatoires pour le setback et les variations horaires.
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