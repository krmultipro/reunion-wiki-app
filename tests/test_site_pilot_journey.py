"""Point d'entrée du parcours pilote grandeur nature des sites."""

import unittest


class SitePilotJourneyTestCase(unittest.TestCase):
    """Documente le cas manuel de la fiche de test 8 des sites."""

    @unittest.skip(
        "Parcours réel exécuté et consigné dans "
        "docs/testing/SITE_PILOT_REPORT_2026-09-22.md ; non reproductible automatiquement."
    )
    def test_tc_site_012_01_complete_real_world_journey(self):
        """TC-SITE-012-01 — Le parcours réel est consigné dans le rapport manuel."""


if __name__ == "__main__":
    unittest.main()
