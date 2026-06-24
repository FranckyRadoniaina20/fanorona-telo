const API = 'https://fanorona-telo-2.onrender.com';

const ADJACENCES = {
  0:[1,3,4], 1:[0,2,4], 2:[1,4,5],
  3:[0,4,6], 4:[0,1,2,3,5,6,7,8],
  5:[2,4,8], 6:[3,4,7], 7:[4,6,8], 8:[4,5,7]
};

// X démarre en BAS (cases 6,7,8) — O / IA démarre en HAUT (cases 0,1,2)
const POSITIONS = [
  {x:60,y:60},{x:180,y:60},{x:300,y:60},
  {x:60,y:180},{x:180,y:180},{x:300,y:180},
  {x:60,y:300},{x:180,y:300},{x:300,y:300}
];

let etat = null;
let caseSelectionnee = null;
let modeActuel = 'hvh';
let niveauActuel = 'moyen';
let scores = { X: 0, O: 0 };

/* ---- CONFIG ---- */
function setMode(mode) {
  modeActuel = mode;
  document.querySelectorAll('#btn-hvh,#btn-hvia').forEach(b => b.classList.remove('active'));
  document.getElementById(`btn-${mode}`).classList.add('active');

  const niveauDiv = document.getElementById('config-niveau');
  niveauDiv.style.display = mode === 'hvia' ? 'flex' : 'none';

  const tagO = document.getElementById('tag-o-label');
  tagO.textContent = mode === 'hvia' ? 'IA (O)' : 'JOUEUR O';

  nouvellePartie();
}

function setNiveau(niveau) {
  niveauActuel = niveau;
  document.querySelectorAll('#btn-facile,#btn-moyen,#btn-difficile')
    .forEach(b => b.classList.remove('active'));
  document.getElementById(`btn-${niveau}`).classList.add('active');
}

/* ---- DESSIN LIGNES ---- */
function dessinerLignes() {
  const canvas = document.getElementById('lignes-plateau');
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, 360, 360);

  const tracees = new Set();
  for (let i = 0; i <= 8; i++) {
    for (const j of ADJACENCES[i]) {
      const cle = [Math.min(i,j), Math.max(i,j)].join('-');
      if (!tracees.has(cle)) {
        tracees.add(cle);
        ctx.strokeStyle = 'rgba(255,255,255,0.25)';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(POSITIONS[i].x, POSITIONS[i].y);
        ctx.lineTo(POSITIONS[j].x, POSITIONS[j].y);
        ctx.stroke();
      }
    }
  }
}

/* ---- AFFICHAGE ---- */
function afficherPlateau() {
  if (!etat) return;

  const conteneur = document.getElementById('plateau');
  conteneur.innerHTML = '';

  const joueur = etat.joueur_actuel;
  const statut = etat.statut;
  const estFini = statut !== 'en_cours';
  const estTourIA = (etat.mode === 'hvia' && joueur === 'O');

  // Tags actifs
  document.getElementById('tag-x').classList.toggle('active', joueur === 'X' && !estFini);
  document.getElementById('tag-o').classList.toggle('active', joueur === 'O' && !estFini);

  // Destinations possibles en Phase 2
  let destinationsPossibles = [];
  if (etat.phase === 2 && caseSelectionnee !== null) {
    destinationsPossibles = ADJACENCES[caseSelectionnee].filter(v => etat.plateau[v] === null);
  }

  for (let i = 0; i < 9; i++) {
    const div = document.createElement('div');
    div.className = 'case';
    div.dataset.index = i;

    const valeur = etat.plateau[i];
    if (valeur) {
      const pion = document.createElement('div');
      pion.className = `pion pion-${valeur.toLowerCase()}-piece`;
      div.appendChild(pion);
    }

    if (i === caseSelectionnee) div.classList.add('selectionnee');
    if (destinationsPossibles.includes(i)) div.classList.add('destination-possible');

    if (!estFini && !estTourIA) {
      div.addEventListener('click', () => handleClic(i));
    } else {
      div.classList.add('non-cliquable');
    }

    conteneur.appendChild(div);
  }

  // Infos status
  document.getElementById('info-phase').textContent =
    `Phase ${etat.phase === 1 ? '1·Place' : '2·Move'}`;
  document.getElementById('info-joueur').textContent =
    estFini ? '—' : `Joueur ${joueur}`;
  document.getElementById('info-score').textContent =
    `X:${scores.X} — O:${scores.O}`;

  // Message fin
  const msg = document.getElementById('message-statut');
  if (statut === 'X_gagne') {
    msg.textContent = ' JOUEUR X GAGNE !';
    msg.classList.remove('hidden');
    scores.X++;
    document.getElementById('info-score').textContent = `X:${scores.X} — O:${scores.O}`;
  } else if (statut === 'O_gagne') {
    msg.textContent = etat.mode === 'hvia' ? ' IA GAGNE !' : '👥 JOUEUR O GAGNE !';
    msg.classList.remove('hidden');
    scores.O++;
    document.getElementById('info-score').textContent = `X:${scores.X} — O:${scores.O}`;
  } else if (statut === 'nul') {
    msg.textContent = ' MATCH NUL !';
    msg.classList.remove('hidden');
  } else {
    msg.classList.add('hidden');
  }
}

/* ---- CLICS ---- */
async function handleClic(index) {
  if (!etat || etat.statut !== 'en_cours') return;

  const phase = etat.phase;
  const joueur = etat.joueur_actuel;

  if (phase === 1) {
    if (etat.plateau[index] !== null) return;
    if (etat.pions_poses[joueur] >= 3) return;
    await envoyerCoup({ position: index });
  } else {
    if (caseSelectionnee === null) {
      if (etat.plateau[index] === joueur) {
        caseSelectionnee = index;
        afficherPlateau();
      }
    } else {
      if (index === caseSelectionnee) {
        caseSelectionnee = null;
        afficherPlateau();
      } else if (etat.plateau[index] === null && ADJACENCES[caseSelectionnee].includes(index)) {
        await envoyerCoup({ depart: caseSelectionnee, arrivee: index });
        caseSelectionnee = null;
      } else if (etat.plateau[index] === joueur) {
        caseSelectionnee = index;
        afficherPlateau();
      }
    }
  }
}

/* ---- API ---- */
async function envoyerCoup(data) {
  try {
    const rep = await fetch(`${API}/coup`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data)
    });
    const json = await rep.json();
    if (json.erreur) { console.warn(json.erreur); return; }
    etat = json;
    afficherPlateau();
    if (json.coup_ia) {
      setTimeout(fetchEtat, 600);
    }
  } catch(e) {
    alert(' Serveur Flask non disponible sur le port 5000 !');
  }
}

async function fetchEtat() {
  const rep = await fetch(`${API}/etat`);
  etat = await rep.json();
  afficherPlateau();
}

async function nouvellePartie() {
  caseSelectionnee = null;
  try {
    const rep = await fetch(`${API}/nouvelle_partie`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ mode: modeActuel, niveau: niveauActuel })
    });
    etat = await rep.json();
    dessinerLignes();
    afficherPlateau();
  } catch(e) {
    alert(' Lance app.py d\'abord !');
  }
}

window.onload = () => {
  setMode('hvh');
};

window.addEventListener('resize', () => {
  dessinerLignes();
  afficherPlateau();
});