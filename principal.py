# -*- coding: utf-8 -*-

import auxiliaire as aux
from mille_bornes import MilleBornes
import click

print("+---------------------------------------------------+")
print("|       Bienvenue dans le jeu du 1000 bornes !      |")
print("+---------------------------------------------------+")
print('')
print("            Idée originale de E. Dujardin            ")
print("Pythonisation de P. Farsi & M.-I. Bani & M. Ben Ftima")

# %% Chargement de partie

print("\nReprendre la dernière partie [[O]ui, [N]on] ? ", end=' ')
chrgmt = aux.choisir_action('OoNn')

if chrgmt in 'Oo':
    partie = MilleBornes.chargement()

# %% Nouvelle partie
else:
    print("\vCombien de joueurs [2-6] ? ", end='', flush=True)
    nJoueurs = int(aux.choisir_action('23456'))

    nomsJoueurs = []
    for i in range(nJoueurs):
        nomsJoueurs.append(input(f"Joueur {i} : ")[:8])

    partie = MilleBornes.nouveau(nomsJoueurs)
# partie = MilleBornes.nouveau(['a', 'b']) # pour débuguer


# %% La partie est lancée
while not partie.fin:
    joueurActuel = partie.joueurSuivant()

    # Le joueur actuel pioche autant de cartes qu'il lui faut.
    joueurActuel.piocher(partie)

    while True:
        print('\033[2J')  # nettoyage écran
        # affichage des joueurs
        for j in partie.joueurs:
            print(j)

        # Normalement le joueur mène son action jusqu'au bout sans encombre.
        actionValide = True

        # on affiche le classement
        # print(partie)

        # choix d'une action (renvoie int)
        choix = joueurActuel.choisir()

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #

        # options du menu qui ne correspondent pas à une carte

        if choix == 7:
            joueurActuel.defausser()
        elif choix == 8:
            partie.enregistrement()

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #

        # options du menu qui correspondent à une carte

        else:
            actionValide = joueurActuel.jouerCarte(partie.joueurs)

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #

    # Vérifications globales

        # Petit message si l'action est invalide sinon on sort du while.
        if actionValide:
            break
        else:
            print('', '#'*20, '# Action invalide. #', '#'*20, '', sep='\n')

    # On vérifie si c'est la fin de la partie.
    partie.checkFin()

# %% La partie est terminee

# fioritures
if any(j.score == 1000 for j in partie.joueurs):
    auxiliaire.win()

# Classement
print("\nFin de partie. Classement :", partie, "Merci d'avoir joué.", sep='\n')
