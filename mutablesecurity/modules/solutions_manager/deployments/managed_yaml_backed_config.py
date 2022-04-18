from enum import Enum
from io import StringIO

import yaml
from pyinfra.api import FactBase
from pyinfra.api.deploy import deploy
from pyinfra.operations import files


class ManagedYAMLBackedConfig:
    @deploy
    def _set_default_configuration(state, host, solution_class):
        configuration_meta = solution_class.meta["configuration"]

        initial_config = {}
        for key, value in configuration_meta.items():
            initial_config[key] = str(value["default"])

        solution_class._configuration = initial_config

    @deploy
    def get_configuration(state, host, solution_class):
        class ConfigurationState(FactBase):
            solution_class = None

            def command(self, solution_class):
                self.solution_class = solution_class

                solution_class_name = solution_class.__name__.lower()

                return f"cat /opt/mutablesecurity/{solution_class_name}/{solution_class_name}.conf"

            def process(self, output):
                output = "\n".join(output)
                config = yaml.safe_load(output)

                configuration_meta = self.solution_class.meta["configuration"]
                for key, value in configuration_meta.items():
                    real_type = value["type"]
                    try:
                        config[key] = real_type(config[key])
                    except:
                        config[key] = real_type[config[key]]

                return config

        solution_class._configuration = host.get_fact(
            ConfigurationState, solution_class=solution_class
        )

        solution_class.result = solution_class._configuration

    @deploy
    def _verify_new_configuration(state, host, solution_class, aspect, value):
        configuration_meta = solution_class.meta["configuration"]

        real_value = None
        try:
            real_type = configuration_meta[aspect]["type"]

            try:
                real_value = real_type(value)
            except ValueError:
                try:
                    real_value = real_type[value]
                except KeyError:
                    pass
        except KeyError:
            pass

        solution_class.result = real_value is not None

    @deploy
    def set_configuration(state, host, solution_class, aspect, value):
        # Verify the new configuration
        solution_class._verify_new_configuration(
            state=state, host=host, aspect=aspect, value=value
        )
        if not solution_class.result:
            solution_class.result = False

            return

        # Get the actual configuration
        solution_class.get_configuration(state=state, host=host)

        # Set the configuration to its new state
        configuration_meta = solution_class.meta["configuration"]
        real_type = configuration_meta[aspect]["type"]
        try:
            real_value = real_type(value)
        except:
            real_value = real_type[value]
        solution_class._configuration[aspect] = real_value

        # Upload the new configuration on the server
        solution_class._put_configuration(state=state, host=host)

        # Callback
        if solution_class._set_configuration_callback:
            solution_class._set_configuration_callback(
                state=state, host=host, aspect=aspect, value=value
            )

        solution_class.result = True

    @deploy
    def _put_configuration(state, host, solution_class):
        class FullDumper(yaml.SafeDumper):
            def represent_data(self, data):
                if isinstance(data, Enum):
                    return self.represent_data(data.value)
                return super().represent_data(data)

        solution_id = solution_class.meta["id"]

        location = f"/opt/mutablesecurity/{solution_id}/{solution_id}.conf"
        files.put(
            state=state,
            host=host,
            sudo=True,
            name="Dumps the solution configuration file",
            src=StringIO(yaml.dump(solution_class._configuration, Dumper=FullDumper)),
            dest=location,
        )

        solution_class.result = True
