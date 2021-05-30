# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
import auxiliaire as aux


class Carte(ABC):
    def __init__(self, famille):
        self._valide = False
        self._famille = famille
        self._is_speed = (famille == 'vitesse')
        # est_vitesse permet de savoir sur quelle pile jouer

    def __eq__(self, other):
        if self is other:
            return True
        return type(self) == type(other) and self._famille == other.famille

    def __str__(self):
        return f'{self.__class__.__name__:8} - {self._famille}'

# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| #

    @property
    def famille(self):
        return self._famille

    @property
    def valide(self):
        return self._valide

# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| #

    @classmethod
    def traduction(cls, mot):
        cla, fam = mot[0], mot[1:]
        return eval("{}({})".format(aux.dicoC[cla], aux.dicoF[fam]))

# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| #

    @abstractmethod
    def interagir():
        pass

# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| #

    def abreviation(self):
        cla, fam = self.__class__.__name__[0], self._famille[:2]
        return cla+fam


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #

class Attaque(Carte):

    def __init__(self, famille):
        super().__init__(famille)

    def interagir(self, table, main):
        # les cartes ne sont pas réellement distinctes mais des copies d'une
        # même instance. Il faut réinitialiser à False à chaque interaction.
        self._valide = False

        # cas classique, attaque sans coup fourré. Attaque bloquée si
        # 1. attaque dans la même pile (booléen is_speed)
        bloque = isinstance(table[self._is_speed], Attaque)
        # 2. OU botte même famille
        bloque |= Botte(self._famille) in table[2:]
        # 3. OU attaque vitesse et botte feu
        bloque |= self._is_speed and Botte('feu') in table[2:]

        if not bloque:
            table[self._is_speed] = self    # on pose l'attaque
            self._valide = True              # l'attaque est valide

        # cas spécial, coup fourré
        if self._valide:
            for i, c in enumerate(main):

                # coup fourré si
                # 1. botte ET
                # 2. de même famille OU 3. attaque et botte de type is_speed

                if (isinstance(c, Botte) and            # 1
                    (self._famille == c._famille or     # 2
                     self._is_speed and c._is_speed)):  # 3

                    print('', '%'*16, '% Coup fourré. %', '%'*16, '', sep='\n')
                    botte = main.pop(i)
                    return botte.interagir(table)

        return False    # la cible n'a pas la priorité au prochain tour.


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #

class Parade(Carte):
    def __init__(self, famille):
        super().__init__(famille)

    def interagir(self, table):
        # les cartes ne sont pas réellement distinctes mais des copies d'une
        # même instance. Il faut réinitialiser à False à chaque interaction.
        self._valide = False

        c = table[self._is_speed]

        # Parade si
        # pile avec attaque ET
        # attaque de même famille

        self._valide = isinstance(c, Attaque) and self._famille == c._famille
        if self._valide:
            table[self._is_speed] = self

        return False  # le joueur ne continue plus de jouer.


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #

class Botte(Carte):
    def __init__(self, famille):
        super().__init__(famille)
        self._is_speed = (famille == 'feu')

    def interagir(self, table):
        # les cartes ne sont pas réellement distinctes mais des copies d'une
        # même instance. Il faut réinitialiser à False à chaque interaction.
        self._valide = False

        # cas de la botte véhicule prioritaire
        if self._is_speed:
            # on convertit la pile de vitesse en parade
            table[1] = Parade('vitesse')

        if table[0]._famille == self.famille:
            table[0] = Parade(self._famille)

        table.append(self)

        self._valide = True    # poser une botte est toujours possible

        return True  # le joueur continue de jouer


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #

class Distance(Carte):

    def __init__(self, famille):
        self._famille = famille

    def __str__(self):
        return f'{self.__class__.__name__:8} - {self._famille} km'

# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| #

    def abreviation(self):
        cla, fam = self.__class__.__name__[0], str(self._famille)[:2]
        return cla+fam

    def interagir(self, table):
        # les cartes ne sont pas réellement distinctes mais des copies d'une
        # même instance. Il faut réinitialiser à False à chaque interaction.
        self._valide = False

        # Les cartes n'interagissent qu'avec la table du joueur. La méthode
        # Joueur.jouerCarte() s'occupe de vérifier les stats du joueur.

        # on peut avancer si
        # 1. la limitation de vitesse est respectée
        # 2. la pile de bataille est sans attaque

        self._valide = ((self._famille <= 50 or
                         not isinstance(table[1], Attaque))         # 1
                         and not isinstance(table[0], Attaque))     # 2

        return False    # le joueur ne recommence pas son tour
