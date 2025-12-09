"""
Script de test pour vérifier que les agents des squads peuvent être importés.
"""

import sys
from pathlib import Path

# Ajouter le chemin racine au PYTHONPATH
root_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_path))

def test_accessibility_squad():
    """Test import des agents Accessibility Squad."""
    try:
        from orchestration.agents.accessibility_squad import (
            AccessibilityExpertAgent,
            I18nSpecialistAgent
        )
        print("✅ Accessibility Squad - Imports réussis")
        print(f"   - AccessibilityExpertAgent: {AccessibilityExpertAgent}")
        print(f"   - I18nSpecialistAgent: {I18nSpecialistAgent}")
        return True
    except Exception as e:
        print(f"❌ Accessibility Squad - Erreur d'import: {e}")
        return False

def test_ai_ml_squad():
    """Test import des agents AI/ML Squad."""
    try:
        from orchestration.agents.ai_ml_squad import (
            AIEngineer,
            MLOpsEngineer
        )
        print("✅ AI/ML Squad - Imports réussis")
        print(f"   - AIEngineer: {AIEngineer}")
        print(f"   - MLOpsEngineer: {MLOpsEngineer}")
        return True
    except Exception as e:
        print(f"❌ AI/ML Squad - Erreur d'import: {e}")
        return False

def main():
    """Exécute tous les tests."""
    print("=" * 60)
    print("TEST DES AGENTS - ACCESSIBILITY & AI/ML SQUADS")
    print("=" * 60)
    print()

    results = []

    print("1. Test Accessibility Squad")
    print("-" * 60)
    results.append(test_accessibility_squad())
    print()

    print("2. Test AI/ML Squad")
    print("-" * 60)
    results.append(test_ai_ml_squad())
    print()

    print("=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    success_count = sum(results)
    total_count = len(results)
    print(f"Tests réussis: {success_count}/{total_count}")

    if success_count == total_count:
        print("✅ TOUS LES TESTS SONT PASSÉS")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")

    return success_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
