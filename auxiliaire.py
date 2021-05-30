# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 13:14:23 2021

@author: Mohamed-iadh BANI
"""

from PIL import Image
from time import sleep
import click
from typing import List, Optional

# Les dictionnaires qui servent à traduire les mots en carte
# (Carte.tarduction())

dicoF = {'10': 100, '20': 200, '25': 25, '50': 50, '75': 75,
         'ac': "'accident'", 'es': "'essence'",
         'fe': "'feu'", 'pn': "'pneu'", 'vi': "'vitesse'"}

dicoC = {'A': 'Attaque', 'B': 'Botte', 'D': 'Distance', 'P': 'Parade'}

err = '\x1B[31m'
coup_fourre = '\x1B[32m'


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #

def saisir(menu: List[str], msg_err: Optional[str] = None) -> str:
    '''Invite de saisie d'un choix parmi une liste de caractères.'''

    c = click.getchar()
    while c not in menu:
        if msg_err is not None:
            print(err, msg_err, sep='', end='\x1B[m\r')

        c = click.getchar()

    print('\x1B[2K')
    return c


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #

# Les expressions du 1000 Bornes
dico = {'A': {'ac': 'Accident', 'es': 'Panne d\'essence', 'fe': 'Feu rouge',
              'pn': 'Crevaison', 'vi': 'yes limit'},
        'B': {'ac': 'As du volant', 'es': 'Citerne d\'essence',
              'fe': 'Véhicule prioritaire', 'pn': 'Increvable'},
        'D': {'25': 'Escargot', '50': 'Canard', '75': 'Papillon',
              '10': 'Lièvre', '20': 'Hirondelle'},
        'P': {'ac': 'Réparations', 'es': 'Essence', 'fe': 'Feu vert',
              'pn': 'Roue de secours', 'vi': 'no limit'}}

def beauMot(mot):
    c, f1, f2 = mot
    return dico[c][f1+f2]


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #

def choix(ensemble):
    """Utilitaire de choix d'action. Pas de sortie tant qu'une des touches de
    `ensemble` n'a pas été pressée."""
    touche = ''

    while touche not in ensemble:
        touche = click.getchar(echo=True)

    print(touche)

    return touche


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #

def animation(joueur):
    """Animation en Voiture."""

    # voiture1 = " _.-.___\\__"
    # voiture2 =  "|  _      _`-."
    # voiture3 = "'-(_)----(_)--`"

    # divise = 20

    # voiture_score = int(joueur.score/divise)

    # flag1 = "o______\n"
    # flag2 = "| 1000 |\n"
    # flag3 = "|  Km  |\n"
    # flag4 = "|______|\n"

    # voiture1 = " "*voiture_score + voiture1 + " "*(1000//divise-voiture_score+4) + "|\n"
    # voiture2 = " "*voiture_score + voiture2 + " "*(1000//divise-voiture_score+1) + "|\n"
    # voiture3 = "-"*voiture_score + voiture3 + "-"*(1000//divise-voiture_score)   + "|\n"

    # flag1 = " "*(len(voiture1)-2) + flag1
    # flag2 = " "*(len(voiture1)-2) + flag2
    # flag31 = " "*voiture_score + str(joueur.score) + " km"
    # flag3 = flag31 + " "*(len(voiture1)-len(flag31)-2) + flag3
    # flag4 = " "*(len(voiture1)-2) + flag4

    # Finaltxt = flag1 + flag2 + flag3 + flag4 + voiture1 + voiture2 + voiture3

    # print(Finaltxt)
    
    dist = joueur.score//25
    
    print('🏁', (40-dist)*'_', '🚙', dist*'_', sep='')

    # Fin Animation

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #


def win():
    # img = Image.open('Win.jpg')
    # img.show()

    # iadh@parsa : mon message sert à rien s'ils testent notre code sur le
    # terminal mais je le garde quand même..
    print('\
     __        _____ _   _ _ _\n \
    \ \      / |_ _| \ | | | |\n \
     \ \ /\ / / | ||  \| | | |\n \
      \ V  V /  | || |\  |_|_|\n \
       \_/\_/  |___|_| \_(_(_)')

    sleep(5)
