import inspect

from pyinfra.api.deploy import deploy


class ManagedStats:
    @deploy
    def get_stats(state, host, solution_class):
        solution_class.get_configuration(state=state, host=host)

        result = {}
        metrics_config = solution_class.meta["metrics"]
        for _, value in metrics_config.items():
            fact = value["fact"]
            kwargs = {}

            # Check if the stat requires paramets
            command = fact.command
            if callable(command):
                parameters = inspect.signature(command).parameters
                if len(parameters) > 1:
                    # Get the parameters from class' configuration
                    kwargs = {
                        key: solution_class._configuration[key]
                        for key in parameters
                        if key != "self"
                    }

            result[value["description"]] = host.get_fact(fact, **kwargs)

        solution_class.result[host.name] = result
