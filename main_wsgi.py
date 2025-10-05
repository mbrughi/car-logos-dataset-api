import os
import sys
from pathlib import Path

# 1) Imposta la root del progetto (cartella che contiene "app/")
PROJECT_ROOT = Path(__file__).resolve().parent
os.chdir(PROJECT_ROOT)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 2) Import dell'adapter ASGI->WSGI in modo compatibile tra versioni
#    asgiref ha usato nomi diversi nel tempo (AsgiToWsgi, ASGItoWSGI, ecc.)
import importlib

aw = importlib.import_module("asgiref.wsgi")
Adapter = (
    getattr(aw, "ASGItoWSGI", None)
    or getattr(aw, "AsgiToWsgi", None)
    or getattr(aw, "asgi_to_wsgi", None)  # in alcune versioni è funzione
)
if Adapter is None:
    # fallback: messaggio chiaro se in futuro cambiano ancora il nome
    raise ImportError(
        f"Impossibile trovare l'adapter ASGI->WSGI in asgiref.wsgi. Attributi disponibili: {dir(aw)}"
    )

# 3) Importa l'app FastAPI (ASGI)
from app.main import app as asgi_app  # NOQA

# 4) uWSGI per default cerca "application" come callable WSGI
application = Adapter(asgi_app)
