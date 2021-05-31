# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 15:04:26 2021

@author: Mohamed-iadh BANI
"""
from random import shuffle

from joueur import Joueur
from carte import *

class MilleBornes:

    def __init__(self):
        self.__fin = False
        self.__nbrJoueurs, self.__tour = 0, -1,
        self.pioche = []
        self.__joueurs = []

    def __str__(self):
        # Copie liste joueurs et classement
        temp = self.joueurs[:]
        temp.sort(key=lambda j: j.score, reverse=True)

        # Rendu lisible du classement
        n, txt = 1, f'#1 | {temp[0].score:4} km | {temp[0].nom}'

        for i in range(1, self.__nbrJoueurs):
            if temp[i].score != temp[i-1].score:
                n = i+1
            txt += f'\n#{n} | {temp[i].score:4} km | {temp[i].nom}'

        return txt

# getters ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| #

    @property
    def fin(self):
        return self.__fin

    @property
    def joueurs(self):
        return self.__joueurs

    @property
    def nbrJoueurs(self):
        return self.__nbrJoueurs

    @property
    def tour(self):
        return self.__tour

# méthodes de classe |||||||||||||||||||||||||||||||||||||||||||||||||||||||| #

    @classmethod
    def nouveau(cls, noms):
        partie = cls()
        partie.__nbrJoueurs = len(noms)

        # les Distances
        partie.pioche += ([Distance(25)]*10
                        + [Distance(50)]*10
                        + [Distance(75)]*10
                        + [Distance(100)]*12
                        + [Distance(200)]*4)

        # les Attaques
        partie.pioche += ([Attaque('accident')]*3
                        + [Attaque('essence')]*3
                        + [Attaque('pneu')]*3
                        + [Attaque('vitesse')]*4
                        + [Attaque('feu')]*5)

        # les Parades
        partie.pioche += ([Parade('accident')]*6
                        + [Parade('essence')]*6
                        + [Parade('pneu')]*6
                        + [Parade('vitesse')]*6
                        + [Parade('feu')]*14)

        # Les Bottes
        partie.pioche += [Botte('accident'),
                        Botte('essence'),
                        Botte('pneu'),
                        Botte('feu')]  # surtout pas 'vitesse'

        # On melange la pioche 2 fois (question d'homogénéité)
        shuffle(partie.pioche)
        shuffle(partie.pioche)

        # On intègre les joueurs à la partie
        partie.__joueurs = [Joueur(j) for j in noms]

        # tout le monde pioche 6 cartes
        for j in partie.__joueurs:
            j.piocher(partie, 6)

        return partie

    @classmethod
    def chargement(cls):
        partie = cls()

        # extraction des donnees : pioche, donnees auxiliaires, joueurs
        with open('data.txt', 'r') as f:
            pio, tou, *jou = f.readlines()

        pio = pio[:-1]  # suppression du caractère d'échappement '\n'.

        # construction de la pioche
        partie.pioche = [Carte.traduction(mot) for mot in pio.split(',')]

        # construction des joueurs
        partie.__joueurs = [Joueur.rappel(sequence) for sequence in jou]

        # réglage des données auxiliaires
        partie.__nbrJoueurs = len(jou)
        partie.__tour = int(tou)

        return partie

# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| #

    def checkFin(self):
        # La partie est terminée si :
        # 1. un joueur atteint les mille bornes ;
        # 2. la pioche ne contient aucune carte distance ;
        # 3. un joueur quitte la partie.

        self.__fin = (any(j.score == 1000 for j in self.joueurs) or     # 1
                      all(type(c) != Distance for c in self.pioche) or  # 2
                      self.fin)                                         # 3

    def enregistrement(self):
        with open('data.txt', 'w') as f:
            # sauvegarde de la pioche
            if self.pioche:
                f.write(','.join([c.abreviation() for c in self.pioche])+'\n')
            else:
                f.write('[]\n')

            # sauvegarde tour actuel
            f.write(f"{self.tour-1}\n")

            # sauvegarde des joueurs
            for j in self.joueurs:
                # sauvegarde main
                f.write(','.join([c.abreviation() for c in j.main])+';')
                # sauvegarde table : piles bataille et vitesse
                f.write(','.join([c.abreviation() for c in j.table])+';')
                # sauvegarde nom et score
                f.write(f"{j.nom};{j.score}\n")

        self.__fin = True
        print("Partie enregistrée dans data.txt")

    def joueurSuivant(self):
        # si l'action précédente a mené à l'utilisation d'une botte, cette
        # boucle trouve le joueur qui l'a posé.
        for i, j in enumerate(self.joueurs):
            if j.priorite:
                self.__tour = i
                return j

        # Si pas de botte, on prend le joueur suivant dans la liste.
        self.__tour += 1
        self.__tour %= self.nbrJoueurs

        return self.joueurs[self.tour]

# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| #
