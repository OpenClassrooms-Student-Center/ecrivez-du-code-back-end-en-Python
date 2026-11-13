# Hamac

API interne de gestion des congés : les salariés consultent leur solde
et déposent leurs demandes, les managers les approuvent ou les refusent.
L'écran est développé par l'équipe front, dans un autre dépôt.

## Démarrer

Prérequis : uv (il installe lui-même la version de Python du projet).

    uv sync
    uv run python manage.py migrate
    uv run python manage.py reset_demo   # charge le jeu de démonstration
    uv run python manage.py runserver    # API sur http://localhost:8000

La base SQLite (db.sqlite3) n'est pas versionnée. Relancez reset_demo pour
retrouver l'état initial des données de démonstration.

## Configuration

| Réglage | Où | Rôle |
| --- | --- | --- |
| HAMAC_FIXED_TERM_DAYS_PER_FULL_MONTH | Variable d'environnement (défaut : 2.08) | Taux d'acquisition des CDD |
| DEBUG, DATABASES | config/settings.py | Mode de développement, base de données |

## Architecture

Projet Django config, application unique leave :

- models.py : Employee, LeaveRequest, LeaveStatus
- policies.py : une politique de calcul des droits par type de contrat
- services.py : LeaveService, qui porte les règles métier
- composition.py : seul module qui assemble les objets
- serializers.py, views.py, urls.py : l'API (DRF), sans règle métier

Ajouter un type de contrat : une valeur dans ContractType, une classe de
politique dans policies.py, une ligne dans composition.py, des tests.
Le service ne change pas.

## API

Documentation interactive : http://localhost:8000/api/docs (en développement).
Contrat versionné : schema.yml (régénérer avec
uv run python manage.py spectacular --file schema.yml).

| Verbe | Route | Rôle |
| --- | --- | --- |
| GET | api/employees/{id}/balance | Solde d'un salarié |
| GET | api/leave-requests?status= | Liste des demandes, filtrable par statut |
| GET | api/leave-requests/{id} | Détail d'une demande |
| POST | api/leave-requests | Dépôt d'une demande (201) |
| POST | api/leave-requests/{id}/approval | Approbation (409 si déjà traitée) |
| POST | api/leave-requests/{id}/refusal | Refus (409 si déjà traitée) |

Les clés JSON sont en camelCase : elles font partie du contrat.

## Tests et qualité

    uv run pytest
    uv run ruff check .
    uv run ruff format --check .

## Règles métier et limites connues

Les règles de calcul des droits sont validées par Samuel Okafor (RH) :
ne modifiez pas une règle sans son accord.

- Les jours fériés ne sont pas déduits du nombre de jours ouvrés.
- L'API n'a pas d'authentification : n'importe quel client peut approuver une demande.
- CORS n'est pas configuré : à ajouter (django-cors-headers) quand l'origine de l'écran sera connue.
- Les messages d'erreur mélangent l'anglais (DRF) et le français (Hamac).
- La politique des CDD renvoie un droit négatif pour une date d'entrée future (à confirmer avec Samuel).
- Configuration de développement uniquement : DEBUG, SECRET_KEY et SQLite sont à revoir avant une mise en production.
