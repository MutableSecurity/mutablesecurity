from enum import Enum

from ._abstract import AbstractSolution


class AvailableSolution(Enum):
    SURICATA = ("suricata", "Suricata")
    TELER = ("teler", "Teler")
    LETS_ENCRYPT = ("lets_encrypt", "LetsEncrypt")
