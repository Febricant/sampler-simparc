# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 08:37:11 2019

@author: cv1751 - Brice Le Lostec
@description: Master class for generating Bayesian Networks (BN) using pyAgrum.
@note: This class provides methods to save, load, plot Bayesian Networks and load CSV files.
@version: 1.0

"""

import os
current_path = os.environ.get("PATH")
os.environ["PATH"] = current_path + ";C:\\Brice\\Graphviz2.38\\bin"


import pandas as pd

import pyAgrum as gum
try:
    import pyAgrum.lib.ipython as gnb
except:
    import pyAgrum.lib.notebook as gnb


FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(FILE_DIR+ "/../")  # répertoire supérieur

class Master_genereBN(object):

    def __init__(self):
        pass

    def Save_BN(self, pathfile):
        gum.saveBN(self.bn,pathfile)
        
    def Load_BN(self, pathfile):
        self.bn = gum.loadBN(pathfile)

    def Plot_BN(self):
        gnb.showInference(self.bn,evs={},size = '30')
        #gnb.showBN(self.bn,size='10')
    
    def Load_csv(self, stFileName, sep = ','):
        self.dfcsv = pd.read_csv(stFileName, sep = sep, dtype=str)
        
    def Load_excel(self, stFileName, sheet_name=None):
        self.dfcsv = pd.read_excel(stFileName, sheet_name=sheet_name)

    def Gum_Sampling(self, number, Multiplicateur = 1, evs={}):
        g=gum.BNDatabaseGenerator(self.bn)
        g.setTopologicalVarOrder()#setRandomVarOrder()
        #g.setDiscretizedLabelModeRandom()
        if int(number * Multiplicateur) == 0:
            number = 1
        else:
            number = int(number * Multiplicateur)
        g.drawSamples(number, evs)
        return g.to_pandas()
    
    def do_Sampling(self, numberOfSamples, evs = {}):

        dfSampling = pd.DataFrame()
        #{'ModeOccupation':'Proprietaire'}
        #numberOfSamples = 1000
        boSampling = False#not finish
        dfTemp = self.Gum_Sampling(numberOfSamples, 1, evs=evs)

        if len(dfTemp)>= numberOfSamples:
            dfSampling = dfTemp.sample(n=numberOfSamples, random_state=42)
            boSampling = True    
        else:
            dfSampling = pd.concat([dfSampling, dfTemp])
            numberOfSamples_restant = numberOfSamples - len(dfSampling)
            if len(dfSampling)>0:
                Fact = len(dfSampling)/numberOfSamples
            else:
                Fact = 5

        while not boSampling:
            dfTemp = self.Gum_Sampling(numberOfSamples_restant, min(1, max(5, Fact)), evs=evs)
            if len(dfTemp)>= numberOfSamples_restant:
                dfSampling = pd.concat([dfSampling, dfTemp.sample(numberOfSamples_restant, random_state=42)])
                boSampling = True

            else:
                dfSampling = pd.concat([dfSampling, dfTemp])
                numberOfSamples_restant = numberOfSamples - len(dfSampling)
        return dfSampling.reset_index(drop=True)

if __name__ == "__main__":
    # Example usage
    #run in interactive windows
    
    bnM = Master_genereBN()
    import pyAgrum as gum
    import matplotlib
    matplotlib.use('TkAgg')


    bnM.bn = gum.BayesNet("WaterSprinkler")
    id_c = bnM.bn.add(gum.LabelizedVariable("c", "cloudy ?", 2))
    id_s, id_r, id_w = [
    bnM.bn.add(name, 2) for name in "srw"
    ]  # bn.add(name, 2) === bn.add(gum.LabelizedVariable(name, name, 2))

    bnM.bn.addArc("c", "s")
    for link in [(id_c, id_r), ("s", "w"), ("r", "w")]:
        bnM.bn.addArc(*link)
    bnM.bn.cpt("c").fillWith([0.4, 0.6])

    bnM.bn.cpt("s")[0, :] = 0.5  # equivalent to [0.5,0.5]
    bnM.bn.cpt("s")[1, :] = [0.9, 0.1]
    bnM.bn.cpt("w")[0, 0, :] = [1, 0]  # r=0,s=0
    bnM.bn.cpt("w")[0, 1, :] = [0.1, 0.9]  # r=0,s=1
    bnM.bn.cpt("w")[1, 0, :] = [0.1, 0.9]  # r=1,s=0
    bnM.bn.cpt("w")[1, 1, :] = [0.01, 0.99]  # r=1,s=1
    bnM.bn.cpt("r")[{"c": 0}] = [0.8, 0.2]
    bnM.bn.cpt("r")[{"c": 1}] = [0.2, 0.8]
    #bnM.bn

    #gnb.showInference(bnM.bn,evs={},size = '30')
    gnb.showBN(bnM.bn,size='10')
    #bnM.Plot_BN()
