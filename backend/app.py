# app.py - Le serveur Flask (pont entre l'IA Python et l'interface HTML)

from flask import Flask, request, jsonify
from flask_cors import CORS

from game import (
    creer_plateau, verifier_gagnant, determiner_phase,
    est_coup_valide_phase1, est_coup_valide_phase2,
    appliquer_coup_phase1, appliquer_coup_phase2,
    get_mouvements_possibles, obtenir_etat_jeu
)
from ai import ia_choisir_coup

app = Flask(__name__)
CORS(app)

etat = {
    'plateau': creer_plateau(),
    'joueur_actuel': 'X',
    'pions_poses': {'X': 3, 'O': 3},
    'pieces_bougees': {'X': set(), 'O': set()},
    'mode': 'hvh',
    'niveau_ia': 'moyen',
    'statut': 'en_cours'
}


def reset_etat(mode='hvh', niveau='moyen'):
    etat['plateau'] = creer_plateau()
    etat['joueur_actuel'] = 'X'
    etat['pions_poses'] = {'X': 3, 'O': 3}
    etat['pieces_bougees'] = {'X': set(), 'O': set()}
    etat['mode'] = mode
    etat['niveau_ia'] = niveau
    etat['statut'] = 'en_cours'


@app.route('/api/nouvelle_partie', methods=['POST'])
def nouvelle_partie():
    data = request.get_json() or {}
    mode = data.get('mode', 'hvh')
    niveau = data.get('niveau', 'moyen')
    reset_etat(mode, niveau)
    return jsonify(get_reponse())


@app.route('/api/coup', methods=['POST'])
def jouer_coup():
    if etat['statut'] != 'en_cours':
        return jsonify({'erreur': 'La partie est terminée'}), 400

    if etat['mode'] == 'hvia' and etat['joueur_actuel'] == 'O':
        return jsonify({'erreur': "C'est le tour de l'IA"}), 400

    data = request.get_json()
    phase = determiner_phase(etat['plateau'])
    joueur = etat['joueur_actuel']

    if phase == 1:
        position = data.get('position')
        if position is None or not est_coup_valide_phase1(etat['plateau'], position):
            return jsonify({'erreur': 'Coup invalide'}), 400
        if etat['pions_poses'][joueur] >= 3:
            return jsonify({'erreur': 'Vous avez déjà posé vos 3 pions'}), 400
        etat['plateau'] = appliquer_coup_phase1(etat['plateau'], position, joueur)
        etat['pions_poses'][joueur] += 1
    else:
        depart = data.get('depart')
        arrivee = data.get('arrivee')
        if not est_coup_valide_phase2(etat['plateau'], depart, arrivee, joueur):
            return jsonify({'erreur': 'Mouvement invalide'}), 400
        etat['plateau'] = appliquer_coup_phase2(etat['plateau'], depart, arrivee, joueur)
        # Tracker les pièces bougées
        etat['pieces_bougees'][joueur].discard(depart)
        etat['pieces_bougees'][joueur].add(arrivee)

    mettre_a_jour_statut()

    reponse = get_reponse()
    if etat['statut'] == 'en_cours' and etat['mode'] == 'hvia' and etat['joueur_actuel'] == 'O':
        coup_ia = jouer_coup_ia()
        reponse['coup_ia'] = coup_ia

    return jsonify(reponse)


@app.route('/api/coup_ia', methods=['POST'])
def demander_coup_ia():
    if etat['statut'] != 'en_cours':
        return jsonify({'erreur': 'Partie terminée'}), 400
    coup_ia = jouer_coup_ia()
    reponse = get_reponse()
    reponse['coup_ia'] = coup_ia
    return jsonify(reponse)


@app.route('/api/etat', methods=['GET'])
def get_etat():
    return jsonify(get_reponse())


def jouer_coup_ia():
    
    coup = ia_choisir_coup(
    etat['plateau'],
    etat['pions_poses'],
    etat['niveau_ia'],
    etat['pieces_bougees']['X'],
    etat['pieces_bougees']['O']
    )

    if coup is None:
        return None
    if coup['type'] == 'placement':
        etat['plateau'] = appliquer_coup_phase1(etat['plateau'], coup['position'], 'O')
        etat['pions_poses']['O'] += 1
    else:
        etat['plateau'] = appliquer_coup_phase2(
            etat['plateau'], coup['depart'], coup['arrivee'], 'O'
        )
        # Tracker les pièces bougées pour l'IA
        etat['pieces_bougees']['O'].discard(coup['depart'])
        etat['pieces_bougees']['O'].add(coup['arrivee'])

    mettre_a_jour_statut()
    return coup


def mettre_a_jour_statut():
    plateau = etat['plateau']
    joueur = etat['joueur_actuel']
    pieces_bougees = etat['pieces_bougees'][joueur]

    if verifier_gagnant(plateau, joueur, pieces_bougees):
        etat['statut'] = f'{joueur}_gagne'
        return

    etat['joueur_actuel'] = 'O' if joueur == 'X' else 'X'
    prochain = etat['joueur_actuel']
    phase = determiner_phase(plateau)
    if phase == 2 and not get_mouvements_possibles(plateau, prochain):
        etat['statut'] = 'nul'


def get_reponse():
    return {
        'plateau': etat['plateau'],
        'joueur_actuel': etat['joueur_actuel'],
        'phase': determiner_phase(etat['plateau']),
        'statut': etat['statut'],
        'pions_poses': etat['pions_poses'],
        'mode': etat['mode'],
        'pieces_bougees': {
            'X': list(etat['pieces_bougees']['X']),
            'O': list(etat['pieces_bougees']['O'])
        }
    }


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT' , 5000))
    app.run(host='0.0.0.0', port=port)