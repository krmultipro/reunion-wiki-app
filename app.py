# -*- coding: utf-8 -*-

"""Point d'entrée compatible pour lancer l'application depuis la racine."""

from reunion_wiki.app import *  # noqa: F401,F403
from reunion_wiki.app import app


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
