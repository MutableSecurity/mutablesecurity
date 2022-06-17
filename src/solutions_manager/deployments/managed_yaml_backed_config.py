from enum import Enum
from io import StringIO

import yaml
from pyinfra.api import FactBase
from pyinfra.api.deploy import deploy
from pyinfra.api.helpers.exceptions import PyinfraError
from pyinfra.operations import files, python

from ...helpers.exceptions import (
    MandatoryAspectLeftUnsetException,
    SameSetConfigurationValue,
)


class ManagedYAMLBackedConfig:
    def _get_configuration_filename(solution_class):
        solution_id = solution_class.meta["id"]

        return f"/opt/mutablesecurity/{solution_id}/{solution_id}.conf"

    @deploy
    def _check_installation_config(state, host, solution_class):
        # Check each key in the coniguration
        configuration_meta = solution_class.meta["configuration"]
        for key, _ in configuration_meta.items():
            # Check the default aspects to be set
            if not solution_class._configuration[key]:
                raise MandatoryAspectLeftUnsetException()

        return True

    @deploy
    def _set_default_configuration(state, host, solution_class):
        configuration_meta = solution_class.meta["configuration"]

        initial_config = {}
        for key, value in configuration_meta.items():
            initial_config[key] = value["default"]

        solution_class._configuration = initial_config

    @deploy
    def get_configuration(state, host, solution_class):
        class ConfigurationState(FactBase):
            solution_class = None

            def command(self, solution_class):
                self.solution_class = solution_class

                solution_class_name = solution_class.__name__.lower()

                return (
                    f"cat {ManagedYAMLBackedConfig._get_configuration_filename(solution_class)} ||"
                    " echo ''"
                )

            def process(self, output):
                if not output[0]:
                    return None

                output = "\n".join(output)
                config = yaml.safe_load(output)

                configuration_meta = self.solution_class.meta["configuration"]
                for key, value in configuration_meta.items():
                    if config[key] == "None":
                        config[key] = None
                        continue

                    # Convert to the real type
                    real_type = value["type"]
                    try:
                        config[key] = real_type(config[key])
                    except:
                        config[key] = real_type[config[key]]

                return config

        solution_class._configuration = host.get_fact(
            ConfigurationState, solution_class=solution_class
        )

        if not solution_class._configuration:
            ManagedYAMLBackedConfig._set_default_configuration(
                state=state, host=host, solution_class=solution_class
            )
            ManagedYAMLBackedConfig._put_configuration(
                state=state, host=host, solution_class=solution_class
            )

        solution_class.result[host.name] = solution_class._configuration

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

        solution_class.result[host.name] = real_value is not None

    @deploy
    def set_configuration(state, host, solution_class, aspect, value):
        # Verify the new configuration
        solution_class._verify_new_configuration(
            state=state, host=host, aspect=aspect, value=value
        )
        if not solution_class.result:
            solution_class.result[host.name] = False

            return

        # Get the actual configuration
        solution_class.get_configuration(state=state, host=host)

        # Convert the configuration aspect to its real value
        configuration_meta = solution_class.meta["configuration"]
        real_type = configuration_meta[aspect]["type"]
        try:
            real_value = real_type(value)
        except:
            real_value = real_type[value]
        old_value = solution_class._configuration[aspect]

        # Check if the values are the same
        if real_value == old_value:
            raise SameSetConfigurationValue()

        # Set the configuration to its new state
        solution_class._configuration[aspect] = real_value

        # Upload the new configuration on the server
        solution_class._put_configuration(state=state, host=host)

        # Callback
        if solution_class._set_configuration_callback:
            solution_class._set_configuration_callback(
                state=state,
                host=host,
                aspect=aspect,
                old_value=old_value,
                new_value=value,
            )

        solution_class.result[host.name] = True

    @deploy
    def _put_configuration(state, host, solution_class):
        class FullDumper(yaml.SafeDumper):
            def represent_data(self, data):
                if isinstance(data, Enum):
                    return self.represent_data(data.value)
                return super().represent_data(data)

        files.put(
            state=state,
            host=host,
            sudo=True,
            name="Dumps the solution configuration file",
            src=StringIO(
                yaml.dump(solution_class._configuration, Dumper=FullDumper)
            ),
            dest=ManagedYAMLBackedConfig._get_configuration_filename(
                solution_class
            ),
        )

        solution_class.result[host.name] = True
