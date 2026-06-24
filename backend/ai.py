# ai.py - L'Intelligence Artificielle (Minimax + Alpha-Beta)

from game import (
    verifier_gagnant, get_cases_vides, get_mouvements_possibles,
    determiner_phase, appliquer_coup_phase1, appliquer_coup_phase2,
    compter_pions, COMBINAISONS_GAGNANTES
)


def evaluer(plateau):
    if verifier_gagnant(plateau, 'O', set(range(9))):
        return 1000
    if verifier_gagnant(plateau, 'X', set(range(9))):
        return -1000

    score = 0
    for combo in COMBINAISONS_GAGNANTES:
        valeurs = [plateau[i] for i in combo]
        o_count = valeurs.count('O')
        x_count = valeurs.count('X')
        vide_count = valeurs.count(None)

        if o_count == 2 and vide_count == 1:
            score += 10
        if x_count == 2 and vide_count == 1:
            score -= 10
        if o_count == 1 and vide_count == 2:
            score += 1
        if x_count == 1 and vide_count == 2:
            score -= 1

    if plateau[4] == 'O':
        score += 5
    elif plateau[4] == 'X':
        score -= 5

    return score


def minimax(plateau, profondeur, alpha, beta, est_maximiseur,
            pions_poses_x, pions_poses_o,
            pieces_bougees_x=None, pieces_bougees_o=None):

    if pieces_bougees_x is None:
        pieces_bougees_x = set(range(9))
    if pieces_bougees_o is None:
        pieces_bougees_o = set(range(9))

    if verifier_gagnant(plateau, 'O', pieces_bougees_o):
        return 1000 + profondeur
    if verifier_gagnant(plateau, 'X', pieces_bougees_x):
        return -1000 - profondeur
    if profondeur == 0:
        return evaluer(plateau)

    phase = determiner_phase(plateau)
    joueur = 'O' if est_maximiseur else 'X'

    if phase == 1:
        cases_vides = get_cases_vides(plateau)
        if not cases_vides:
            return evaluer(plateau)

        if est_maximiseur:
            meilleur = -float('inf')
            for pos in cases_vides:
                if pions_poses_o < 3:
                    nouveau = appliquer_coup_phase1(plateau, pos, 'O')
                    val = minimax(nouveau, profondeur - 1, alpha, beta, False,
                                  pions_poses_x, pions_poses_o + 1,
                                  pieces_bougees_x, pieces_bougees_o)
                    meilleur = max(meilleur, val)
                    alpha = max(alpha, val)
                    if beta <= alpha:
                        break
            return meilleur if meilleur != -float('inf') else evaluer(plateau)
        else:
            meilleur = float('inf')
            for pos in cases_vides:
                if pions_poses_x < 3:
                    nouveau = appliquer_coup_phase1(plateau, pos, 'X')
                    val = minimax(nouveau, profondeur - 1, alpha, beta, True,
                                  pions_poses_x + 1, pions_poses_o,
                                  pieces_bougees_x, pieces_bougees_o)
                    meilleur = min(meilleur, val)
                    beta = min(beta, val)
                    if beta <= alpha:
                        break
            return meilleur if meilleur != float('inf') else evaluer(plateau)

    else:
        mouvements = get_mouvements_possibles(plateau, joueur)
        if not mouvements:
            return 0

        if est_maximiseur:
            meilleur = -float('inf')
            for depart, arrivee in mouvements:
                nouveau = appliquer_coup_phase2(plateau, depart, arrivee, 'O')
                # Mettre à jour les pièces bougées pour l'IA
                nouvelles_bougees_o = set(pieces_bougees_o)
                nouvelles_bougees_o.discard(depart)
                nouvelles_bougees_o.add(arrivee)
                val = minimax(nouveau, profondeur - 1, alpha, beta, False,
                              pions_poses_x, pions_poses_o,
                              pieces_bougees_x, nouvelles_bougees_o)
                meilleur = max(meilleur, val)
                alpha = max(alpha, val)
                if beta <= alpha:
                    break
            return meilleur
        else:
            meilleur = float('inf')
            for depart, arrivee in mouvements:
                nouveau = appliquer_coup_phase2(plateau, depart, arrivee, 'X')
                # Mettre à jour les pièces bougées pour le joueur
                nouvelles_bougees_x = set(pieces_bougees_x)
                nouvelles_bougees_x.discard(depart)
                nouvelles_bougees_x.add(arrivee)
                val = minimax(nouveau, profondeur - 1, alpha, beta, True,
                              pions_poses_x, pions_poses_o,
                              nouvelles_bougees_x, pieces_bougees_o)
                meilleur = min(meilleur, val)
                beta = min(beta, val)
                if beta <= alpha:
                    break
            return meilleur


def ia_choisir_coup(plateau, pions_poses, niveau='moyen',
                    pieces_bougees_x=None, pieces_bougees_o=None):

    if pieces_bougees_x is None:
        pieces_bougees_x = set()
    if pieces_bougees_o is None:
        pieces_bougees_o = set()

    profondeurs = {
        'facile': 2,
        'moyen': 4,
        'difficile': 9
    }
    profondeur_max = profondeurs.get(niveau, 4)
    phase = determiner_phase(plateau)
    pions_x = pions_poses.get('X', 0)
    pions_o = pions_poses.get('O', 0)

    meilleur_score = -float('inf')
    meilleur_coup = None

    if phase == 1:
        cases_vides = get_cases_vides(plateau)
        for pos in cases_vides:
            if pions_o >= 3:
                break
            nouveau = appliquer_coup_phase1(plateau, pos, 'O')
            score = minimax(nouveau, profondeur_max - 1, -float('inf'), float('inf'),
                            False, pions_x, pions_o + 1,
                            pieces_bougees_x, pieces_bougees_o)
            if score > meilleur_score:
                meilleur_score = score
                meilleur_coup = {'type': 'placement', 'position': pos}
    else:
        mouvements = get_mouvements_possibles(plateau, 'O')
        for depart, arrivee in mouvements:
            nouveau = appliquer_coup_phase2(plateau, depart, arrivee, 'O')
            nouvelles_bougees_o = set(pieces_bougees_o)
            nouvelles_bougees_o.discard(depart)
            nouvelles_bougees_o.add(arrivee)
            score = minimax(nouveau, profondeur_max - 1, -float('inf'), float('inf'),
                            False, pions_x, pions_o,
                            pieces_bougees_x, nouvelles_bougees_o)
            if score > meilleur_score:
                meilleur_score = score
                meilleur_coup = {'type': 'deplacement', 'depart': depart, 'arrivee': arrivee}

    return meilleur_coup