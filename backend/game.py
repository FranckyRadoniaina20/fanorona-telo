# game.py - La logique du jeu Fanorona-Telo

ADJACENCES = {
    0: [1, 3, 4],
    1: [0, 2, 4],
    2: [1, 4, 5],
    3: [0, 4, 6],
    4: [0, 1, 2, 3, 5, 6, 7, 8],
    5: [2, 4, 8],
    6: [3, 4, 7],
    7: [4, 6, 8],
    8: [4, 5, 7],
}

COMBINAISONS_GAGNANTES = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6],
]


def creer_plateau():
    return ['O', 'O', 'O', None, None, None, 'X', 'X', 'X']


def verifier_gagnant(plateau, joueur, pieces_bougees):
    """
    On ne peut gagner que si les 3 pièces ont bougé au moins une fois.
    pieces_bougees = set des positions ACTUELLES des pièces qui ont déjà bougé
    """
    # Vérifier que les 3 pièces du joueur ont toutes bougé
    positions_joueur = [i for i, case in enumerate(plateau) if case == joueur]
    
    # Si pas toutes les pièces ont bougé → pas de victoire possible
    if not all(pos in pieces_bougees for pos in positions_joueur):
        return False

    # Vérifier l'alignement normal
    for combo in COMBINAISONS_GAGNANTES:
        if all(plateau[i] == joueur for i in combo):
            return True
    return False


def plateau_plein(plateau):
    return all(case is not None for case in plateau)


def compter_pions(plateau, joueur):
    return sum(1 for case in plateau if case == joueur)


def get_cases_vides(plateau):
    return [i for i, case in enumerate(plateau) if case is None]


def get_mouvements_possibles(plateau, joueur):
    mouvements = []
    for i, case in enumerate(plateau):
        if case == joueur:
            for voisin in ADJACENCES[i]:
                if plateau[voisin] is None:
                    mouvements.append((i, voisin))
    return mouvements


def determiner_phase(plateau):
    total_pions = sum(1 for case in plateau if case is not None)
    if total_pions < 6:
        return 1
    return 2


def est_coup_valide_phase1(plateau, position):
    return plateau[position] is None


def est_coup_valide_phase2(plateau, depart, arrivee, joueur):
    if plateau[depart] != joueur:
        return False
    if plateau[arrivee] is not None:
        return False
    if arrivee not in ADJACENCES[depart]:
        return False
    return True


def appliquer_coup_phase1(plateau, position, joueur):
    nouveau_plateau = plateau[:]
    nouveau_plateau[position] = joueur
    return nouveau_plateau


def appliquer_coup_phase2(plateau, depart, arrivee, joueur):
    nouveau_plateau = plateau[:]
    nouveau_plateau[arrivee] = nouveau_plateau[depart]
    nouveau_plateau[depart] = None
    return nouveau_plateau


def obtenir_etat_jeu(plateau, joueur_actuel, pions_poses):
    phase = determiner_phase(plateau)
    if verifier_gagnant(plateau, 'X'):
        statut = 'X_gagne'
    elif verifier_gagnant(plateau, 'O'):
        statut = 'O_gagne'
    elif phase == 2 and not get_mouvements_possibles(plateau, joueur_actuel):
        statut = 'nul'
    else:
        statut = 'en_cours'
    return {
        'plateau': plateau,
        'joueur_actuel': joueur_actuel,
        'phase': phase,
        'statut': statut,
        'pions_poses': pions_poses
    }