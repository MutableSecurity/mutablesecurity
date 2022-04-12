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

After installing the [main requirements](README.md#requirements-) of the project, set up the development environment by following the [official Poetry installation guide](https://github.com/python-poetry/poetry#installation) and running `poetry install`.

After installing the main requirements of the project, set up the development environment by following the official installation guide of Poetry. Run `poetry install` to download the required Python packages and `poetry shell` to enter the environment. By running `mutablesecurity`, you will be able to see the tool's banner and guide.

### Creating a New Module

#### Reasearch

Before you begin implementing a module, we recommend that you answer the following questions. They will help you understand what you need to automate and will make the development process easier:
- What is the purpose of this security solution in an organization's infrastructure?
- What are the solution's configurable features?
- What is the current installation process like, and how can it be automated?
- How can I check to see if the solution works as expected?
- What statistics does the solution generate that are useful to the administrator (or a security analyst)?
- Where does the solution generate its logs?

<details>
    <summary><b>Example of answers for Suricata</b></summary>

- **Q**: What role does Suricata play in an organization's infrastructure?
- **A**: Suricata is a system for detecting and preventing network intrusions. Essentially, you configure a middleware device or endpoint to generate alerts for (or directly block) suspicious traffic.
- **Q**: What are the features that can be customized?
- **A**: You can configure Suricata to generate alerts, block malicious traffic, and automatically update its rules.
- **Q**: How does the current installation procedure work, and how can it be automated?
- **A**: The [official installation guide](https://suricata.readthedocs.io/en/latest/install.html) must be followed.
- **Q**: How can I tell if Suricata is working properly?
- **A**: A request to a malicious endpoint will be detected and either alerted or completely blocked.
- **Q**: What statistics does the solution generate that the administrator (or a security analyst) can use?
- **A**: The logs contain useful information (for example, the number of generated alerts in the last day).
- **Q**: Where does Suricata generates its logs?
- **A**: `/var/log/suricata/fast.log`

</details>

#### Implementation

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