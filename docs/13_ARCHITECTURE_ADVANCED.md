Voici la version mise à jour du document `docs/13_ARCHITECTURE_ADVANCED.md`.

J'ai actualisé le statut pour refléter que l'architecture est désormais implémentée (v3.0) et j'ai aligné les définitions de classes avec le code que nous venons de générer (notamment l'utilisation explicite de `chromadb` et la structure des dossiers).

### `docs/13_ARCHITECTURE_ADVANCED.md`

````markdown
# Architecture Avancée : Multi-Projet & RAG (v3.0)

**Statut :** Implémenté / Actif
**Version :** 3.0.0
**Objectif :** Gestion d'Univers Narratifs Multiples et Mémoire Long Terme (RAG).

---

## 1. Vue d'ensemble

Cette architecture transforme TextCraft d'un simple générateur de texte en un **Système de Gestion d'Univers Narratifs**. Elle introduit une isolation stricte des données par projet et une mémoire vectorielle pour maintenir la cohérence sur des romans longs.



### Les Deux Piliers v3.0 :
1.  **Le Gestionnaire de Projets (`ProjectManager`) :** Agit comme un hyperviseur qui charge et décharge des contextes narratifs entiers (fichiers, configurations, états).
2.  **Le Magasin de Mémoire (`MemoryStore`) :** Utilise une base de données vectorielle (ChromaDB) pour indexer sémantiquement chaque paragraphe écrit, permettant aux agents de "se souvenir" d'événements passés.

---

## 2. Module : Gestionnaire de Projets (`core/project_manager.py`)

Ce module remplace les chemins statiques (`data/`) par une résolution dynamique.

### A. Structure de Fichiers (File System)

L'architecture repose sur une hiérarchie stricte où chaque projet contient son propre "cerveau" (Matrix + Bible + Mémoire).

```text
root/
├── core/                      # Logique immuable (Le Moteur)
├── ui/                        # Interface (Le Tableau de Bord)
└── projects/                  # Données Utilisateur (Les Univers)
    ├── default_project/       # Projet par défaut
    │   └── data/
    │       ├── manuscripts/   # Fichiers .md
    │       ├── story_bible/   # Personas, Lieux, etc.
    │       ├── memory_db/     # Base Vectorielle (ChromaDB)
    │       └── matrix.json    # État du projet
    └── cyberpunk_trilogy/     # Autre projet isolé
        └── data/
            └── ...
````

### B. Interface & Responsabilités

Le `ProjectManager` est responsable du **Scaffolding** (création de la structure) et du **Context Switching** (changement de projet à chaud).

```python
class ProjectManager:
    def __init__(self):
        self.root = Path("projects")

    def create_project(self, project_id: str, title: str) -> bool:
        """Crée l'arborescence, la matrice par défaut et la bible."""
        pass

    def load_project(self, project_id: str) -> Path:
        """
        Retourne le chemin racine du projet.
        L'Orchestrator utilise ce chemin pour initialiser ses sous-systèmes.
        """
        pass
```

-----

## 3\. Module : Mémoire Vectorielle RAG (`core/memory_store.py`)

Le RAG (Retrieval Augmented Generation) permet de dépasser la limite de contexte des LLM (fenêtre d'attention).

### A. Flux de Données (The Loop)

1.  **Ingestion (Scanner) :**

      * Le `ProjectScanner` détecte qu'un fichier `.md` a changé.
      * Il appelle `MemoryStore.ingest_manuscript()`.
      * Le texte est découpé en "chunks" (paragraphes).
      * Chaque chunk est converti en vecteur (embeddings OpenAI) et stocké dans ChromaDB.

2.  **Récupération (Narrator/Editor) :**

      * Avant d'écrire, le Narrateur envoie ses instructions au `MemoryStore`.
      * Le système cherche les 5 chunks les plus *sémantiquement proches* dans tout le roman.
      * Ces chunks sont injectés dans le Prompt Système via la variable `{{rag_context}}`.

### B. Implémentation Technique

Nous utilisons **ChromaDB** en mode persistant (stockage local, pas de serveur requis).

```python
class MemoryStore:
    def __init__(self, project_root: Path):
        self.db_path = project_root / "data" / "memory_db"
        self.client = chromadb.PersistentClient(path=str(self.db_path))

    def ingest_manuscript(self, file_path: Path, content: str):
        """
        Vectorise et indexe le contenu.
        Gère la suppression des anciennes versions du fichier pour éviter les doublons.
        """
        pass

    def query(self, query_text: str) -> str:
        """
        Retourne un contexte textuel formaté basé sur la similarité cosinus.
        Ex: "[ch01]: Kael a ramassé l'épée brisée."
        """
        pass
```

-----

## 4\. Workflow de Migration et Utilisation

### Initialisation

Au premier lancement (`python main.py`), le système :

1.  Vérifie l'existence de `projects/`.
2.  Si vide, crée `projects/default_project`.
3.  Initialise l'Orchestrator sur ce projet.

### Commandes (Futur)

Le Dashboard permettra de changer de projet via des commandes (actuellement géré par redémarrage ou modification manuelle de `.last_project`).

### Dépendances Requises

  * `chromadb>=0.4.0`
  * `openai>=1.0.0` (Pour les embeddings `text-embedding-3-small`)
  * `tiktoken` (Recommandé pour le chunking avancé à l'avenir)

<!-- end list -->

```
```