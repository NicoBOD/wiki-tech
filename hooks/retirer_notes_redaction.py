"""Retire du site publié les notes de rédaction (commentaires HTML <!-- NOTE DE RÉDACTION ... -->).

Elles restent lisibles dans les fichiers Markdown du dépôt, mais n'apparaissent pas dans le code
source des pages générées.
"""
import re

_NOTE = re.compile(r"<!--\s*NOTE DE RÉDACTION.*?-->\n?", re.S)


def on_page_markdown(markdown, **kwargs):
    return _NOTE.sub("", markdown)
