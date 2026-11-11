"""Exécute la suite applicative et refuse une découverte vide."""

from pathlib import Path
import sys
import unittest


def main():
    """Retourne un échec si aucun test n'est découvert ou si la suite échoue."""
    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root))
    if not (root / "tests").is_dir():
        print("Aucun test applicatif découvert : dossier tests absent.", file=sys.stderr)
        return 1
    suite = unittest.defaultTestLoader.discover(str(root / "tests"))
    if suite.countTestCases() == 0:
        print("Aucun test applicatif découvert : déploiement refusé.", file=sys.stderr)
        return 1
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
