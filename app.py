"""Point d'entrée simplifié pour l'application Réunion Wiki."""

from app import app


if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", False))
