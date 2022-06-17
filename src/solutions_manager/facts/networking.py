import json

from pyinfra.api import FactBase


class DefaultInterface(FactBase):
    command = "ip -p -j route show default"

    def process(self, output):
        interfaces = json.loads("\n".join(output))

        return interfaces[0]["dev"]
