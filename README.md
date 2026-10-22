# Vigil

Un agente que aprende cómo es cada residente y avisa al cuidador cuando algo va mal, aunque la persona no pueda decirlo.

## Repos
- `vigil` (este): backend, datos, benchmark y documentación. Se despliega en Aiven Runtime.
- `vigil-frontend`: panel del cuidador, hecho en Lovable y sincronizado con GitHub.

## Estructura
| Carpeta | Dueño | Contenido |
| --- | --- | --- |
| `backend/` | Pedro | FastAPI + agente (Claude) + Postgres/Valkey |
| `data/` | María | WESAD → ClickHouse, features, línea base |
| `benchmark/` | María | ingenua vs. personal vs. con feedback |
| `db/` | todos (con cuidado) | esquemas SQL |
| `docs/` | todos | contrato de API y texto de entrega |

## Arrancar
```bash
cp .env.example .env        # rellenar claves
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```
Sin claves, la API devuelve datos de ejemplo (`MOCK=1`), para que el frontend pueda avanzar.

## Reglas
1. Cada uno en su carpeta y su rama. Merge a `main` cada hora; `main` se despliega.
2. Claves solo en `.env`. Datos de WESAD fuera del repo.
3. Si cambias la API, actualiza primero `docs/api.md` y avisa.
4. 13:30 congelamos código. 14:45 entregamos.
