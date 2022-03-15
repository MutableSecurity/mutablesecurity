# Contributing

Thank you for taking the time to contribute to this project 🎊!

## Guides

We've created workflows to help you through the contribution process:
- [Understanding the Infrastructure](#understanding-the-infrastructure);
- [Configuring the Development Environment](#configuring-the-development-environment); and
- [Creating a New Module](#creating-a-new-module).

If you believe there are any missing ones, create an issue and the core team will create a draft to be discussed with the entire community.

### Understanding the Infrastructure

The current architecture can be seen as composed of multiple parts, each dealing with a different aspect of MutableSecurity:
- A leader module for connecting to target machines (local or remote);
- Multiple security solutions submodules, administered by a dedicated manager which executes their instruction on a given connection;
- A main module for coordinating all the modules; and
- CLI for interacting with the user.

The most important resources we use are [pyinfra](https://pyinfra.com/), for connecting to hosts and executing commands, and [Click](https://github.com/pallets/click) and [Rich](https://github.com/Textualize/rich), for creating our beautiful command line interface.

### Configuring the Development Environment

The development environment consists in:
- [Visual Studio Code](https://github.com/Microsoft/vscode) or [VSCodium](https://github.com/VSCodium/vscodium) as an IDE;
- [Black](https://github.com/psf/black) for code formatting (automated via `.vscode/settings.json`);
- [isort](https://github.com/PyCQA/isort) for import sorting (automated via `.vscode/settings.json`); and
- Git for version controlling.

To set up the environment, only install Poetry as in its [documentation](https://python-poetry.org/docs/) and initialize the environment by running `poetry init`.

### Creating a New Module

A security solution is represented as a module in the MutableSecurity infrastructure.

Each module inherits a base class called `AbstractSolution` and overwrites multiple abstract methods that deal with security solution management, from installation to configuration settings.

The process of creating a new module is divided into three major steps:
1. If the solution requires some kind of files for proper management (for example, custom scripts to be run on a regular basis via crontab), create a new folder in `modules/solution_manager/solutions`.
2. In the same folder, create a properly named Python 3 script (noted with `<script>`) containing a class (noted with `<class>`) that wraps up the solution management functionality. A [dummy module](mutablesecurity/modules/solutions_manager/solutions/dummy.py) can be used as a starting point because it contains many comments that will help you understand the internals better.
3. In `modules/solution_manager/solution_manager.py`, create a new member in the `AvailableSolution` enumeration with a tuple `(<script>, <class>)`. For convenience, put the member's name be the uppercase transformation of `<class>`.

## Useful Resources

- [pyinfra's Documentation](https://docs.pyinfra.com/en/1.x)
- [Click's Documentation](https://click.palletsprojects.com/en/8.0.x/)
- [Rich's Documentation](https://rich.readthedocs.io/en/latest/index.html)