"""Point d'entrée simplifié pour l'application Réunion Wiki."""

from app import app


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",  # Permet l'accès depuis le réseau local
        port=5000,
        debug=app.config.get("DEBUG", False)
    )
