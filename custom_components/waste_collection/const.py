"""Constants for Waste Collection."""

from pathlib import Path

DOMAIN = "waste_collection"
PLATFORMS = ["sensor"]

CONF_YEAR = "year"
CONF_SCHEDULE = "schedule"

DATA_DIRECTORY = Path(__file__).parent / "data"

FRACTION_NAMES = {
    "zmieszane": "Zmieszane",
    "bio": "Bio",
    "plastik_metal": "Plastik i metal",
    "makulatura": "Papier",
    "szklo": "Szkło",
    "popiol": "Popiół",
    "zielone": "Odpady zielone",
    "wielkogabarytowe": "Wielkogabarytowe",
    "choinki": "Choinki",
}

FRACTION_ICONS = {
    "zmieszane": "mdi:trash-can",
    "bio": "mdi:leaf",
    "plastik_metal": "mdi:recycle",
    "makulatura": "mdi:newspaper",
    "szklo": "mdi:bottle-soda",
    "popiol": "mdi:fire",
    "zielone": "mdi:grass",
    "wielkogabarytowe": "mdi:sofa",
    "choinki": "mdi:pine-tree",
}
