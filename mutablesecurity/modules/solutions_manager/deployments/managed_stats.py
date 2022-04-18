from pyinfra.api.deploy import deploy


class ManagedStats:
    @deploy
    def get_stats(state, host, solution_class):
        solution_class.get_configuration(state=state, host=host)

        result = {}
        metrics_config = solution_class.meta["metrics"]
        for _, value in metrics_config.items():
            result[value["description"]] = host.get_fact(value["fact"])

        solution_class.result = result
