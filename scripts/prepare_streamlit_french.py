"""Declare the Streamlit shell as French to avoid partial browser translation."""

from __future__ import annotations

import argparse
import importlib.util
import re
from pathlib import Path


def streamlit_html_path() -> Path:
    """Locate the installed Streamlit document without hard-coding the venv."""
    spec = importlib.util.find_spec("streamlit")
    if spec is None or spec.origin is None:
        raise RuntimeError("Streamlit n'est pas installé dans cet environnement.")
    return Path(spec.origin).parent / "static" / "index.html"


def set_document_language(path: Path, *, restore: bool = False) -> bool:
    """Set or restore the language metadata in Streamlit's served HTML document."""
    html = path.read_text(encoding="utf-8")

    if restore:
        updated = html.replace(
            '<html lang="fr" translate="no">',
            '<html lang="en">',
            1,
        )
        updated = re.sub(
            r'\s*<meta name="google" content="notranslate"\s*/>\n?',
            "",
            updated,
            count=1,
        )
    else:
        updated = re.sub(
            r'<html\s+lang="[^"]*"[^>]*>',
            '<html lang="fr" translate="no">',
            html,
            count=1,
        )
        if '<meta name="google" content="notranslate"' not in updated:
            updated = updated.replace(
                '<meta charset="UTF-8" />',
                '<meta charset="UTF-8" />\n    <meta name="google" content="notranslate" />',
                1,
            )

    if updated == html:
        return False
    if '<html lang="fr" translate="no">' not in updated and not restore:
        raise RuntimeError("Impossible de repérer la balise HTML principale de Streamlit.")
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--restore",
        action="store_true",
        help="Rétablir la déclaration HTML d'origine de Streamlit.",
    )
    args = parser.parse_args()

    target = streamlit_html_path()
    changed = set_document_language(target, restore=args.restore)
    status = "mis à jour" if changed else "déjà configuré"
    if args.restore:
        status = "restauré" if changed else "déjà à l'origine"
    print(f"Document Streamlit {status} : {target}")


if __name__ == "__main__":
    main()
