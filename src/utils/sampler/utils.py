# -*- coding: utf-8 -*-

import random

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def HConsignes():
    """
        Initialize random parameters for setback and hourly variations.
        This method determines random parameters related to heating & cooling schedules.
            1 - self.dev1: AM setback hour (temperature increase)
            2 - self.dev2: AM setback hour (temperature decrease)
            3 - self.dev3: PM setback hour (temperature increase)
            4 - self.dev4: PM setback hour (temperature decrease)
                           ___TM____              ___TS____
                          |         |            |         |
              0h___TN___h1|       h2|____TJ____h3|       h4|___TN_____24h


            Night (temperature)
                           __TM_________TJ___________TS____
                          |                                |
              0h___TN __h1|       h2           h3        h4|___TN______24h

    """

    # Random hourly variations
    dev1 = random.uniform(-3, 3)  # randnb(3)
    dev2 = random.uniform(-3, 3)
    dev3 = random.uniform(-3, 3)
    dev4 = random.uniform(-3, 3)
    dev5 = random.uniform(-1, 1)
    dev6 = random.uniform(-1, 1)

    # Compute schedule change hours
    h1 = 6 + 6 / 60 + (dev1 * 0.75 - dev2 * 0.25)
    h2 = 8 + (dev1 * 0.75 + dev2 * 0.25)
    h3 = 16 + 20 / 60 + (dev3 * 0.5 - dev4 * 0.5)
    h4 = min(22 + 17 / 60 + (dev3 * 0.5 + dev4 * 0.5), 23 + 59 / 60)
    return [h1, h2, h3, h4]
