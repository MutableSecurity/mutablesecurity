from pyinfra.api.deploy import deploy
from pyinfra.operations import server


class Crontab:
    @deploy
    def remove_crontabs(state, host, unique_identifier):
        server.shell(
            state=state,
            host=host,
            sudo=True,
            name="Removes a group of crontabs by an unique identifier",
            commands=[f"crontab -l | grep -v '{unique_identifier}' | sudo crontab -"],
        )
