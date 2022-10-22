<div align="center">
    <img src="others/readme_images/cover.webp" width="600px" alt="Cover">
    <br/><br/>
    <img src="https://img.shields.io/github/workflow/status/mutablesecurity/mutablesecurity/Executes%20unit%20testing%20and%20coverage%20reporting?color=brightgreen&label=unit%20tests&logo=github&logoColor=white&style=flat-square" alt="Unit Tests">
    <a href='https://coveralls.io/github/MutableSecurity/mutablesecurity?branch=main'>
        <img src="https://img.shields.io/coveralls/github/MutableSecurity/mutablesecurity?color=brightgreen&label=coverage&logo=coveralls&logoColor=white" alt="Coveralls Coverage">
    </a>
    <br/>
    <img src="https://snyk-widget.herokuapp.com/badge/pip/mutablesecurity/badge.svg" alt="Snyk Security Score">
    <img src="https://deepsource.io/gh/MutableSecurity/mutablesecurity.svg/?label=active+issues&show_trend=true&token=p678jq0qtDRJaOXo_Whya-un" alt="Deepsource active issues">
    <img src="https://img.shields.io/badge/dependencies%20bumping-enabled-brightgreen?logo=dependabot&style=flat-square&logoColor=white" alt="Dependencies Bumping via Dependabot">
    <br/>
    <img src="https://img.shields.io/pypi/dm/mutablesecurity?color=blue&logoColor=white&label=downloads&logo=pypi&style=flat-square" alt="Monthly Downloads on PyPi">
    <img src="https://img.shields.io/pypi/v/mutablesecurity?color=blue&label=version&logo=pypi&logoColor=white&style=flat-square" alt="Stable Version of PyPi">
    <img src="https://img.shields.io/github/stars/mutablesecurity/mutablesecurity?color=blue&logoColor=white&label=stars&logo=github&style=flat-square" alt="GitHub Stars">
    <img src="https://img.shields.io/github/issues-closed/mutablesecurity/mutablesecurity?color=blue&logoColor=white&label=issues&logo=github&style=flat-square" alt="GitHub closed issues">
    <img src="https://img.shields.io/github/license/mutablesecurity/mutablesecurity?color=lightgray&logoColor=white&label=license&logo=opensourceinitiative&style=flat-square" alt="License">
    <br/>
</div>

---

- [Description](#description)
  - [Functionalities](#functionalities)
  - [Supported Cybersecurity Solutions](#supported-cybersecurity-solutions)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Via Debian Repository](#via-debian-repository)
  - [Via PyPi](#via-pypi)
  - [Debian Package](#debian-package)
  - [Executable](#executable)
- [Demo](#demo)
- [Support](#support)
- [Contributing](#contributing)

---

# Description

**MutableSecurity** is a CLI program for making cybersecurity solution management easier and more accessible, from deployment and configuration to monitoring.

## Functionalities

- [**Multiple solution** supported](#supported-cybersecurity-solutions) so far (and more under development)
- **Operations** managing the solution lifecycle
    - Initially configuring the solution via YAML files
    - Installing the solution
    - Retrieving and changing the solution configuration
    - Retrieving metrics about the solution functioning
    - Updating the solution to its newest version
    - Uninstalling the solution
- **Multiple authentication methods**
    - Password-based when deploying to the local host
    - Password-based or key-based SSH for remote hosts
- **Deployments to multiple hosts** with the same command
- **Intuitive CLI**
- **Extensive [usage](https://mutablesecurity.io/docs/users) and [contribution](https://mutablesecurity.io/docs/developers) documentations**

## Supported Cybersecurity Solutions

<table>
    <thead>
        <tr>
            <th>Solution</th>
            <th>Description</th>
            <th>Others</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>
                <a href="https://teler.app">
                    <img src="others/readme_images/solutions/teler.webp">
                </a>
            </td>
            <td>teler is a real-time intrusion detection and threat alert based on web log. Targets only nginx installed on Ubuntu.</td>
            <td>
                <img alt='Maturity: Production' src='https://img.shields.io/badge/Maturity-Production-blightgreen?style=flat-square'>
            </td>
        </tr>        <tr>
            <td>
                <a href="https://www.fail2ban.org">
                    <img src="others/readme_images/solutions/fail2ban.webp">
                </a>
            </td>
            <td>Fail2ban is an intrusion prevention software framework that protects Unix-like servers from brute-force attacks. It scans log files and bans IP addresses conducting too many failed operations (for example, login attempts). This module targets Debian-based operating systems and has already set a SSH jail.</td>
            <td>
                <img alt='Maturity: Production' src='https://img.shields.io/badge/Maturity-Production-blightgreen?style=flat-square'>
            </td>
        </tr>        <tr>
            <td>
                <a href="https://letsencrypt.org">
                    <img src="others/readme_images/solutions/lets_encrypt.webp">
                </a>
            </td>
            <td>Let's Encrypt is a free, automated, and open certificate authority brought to you by the nonprofit Internet Security Research Group (ISRG). Certbot is a free, open source software tool for automatically using Let's Encrypt certificates on manually-administrated websites to enable HTTPS.</td>
            <td>
                <img alt='Maturity: Production' src='https://img.shields.io/badge/Maturity-Production-blightgreen?style=flat-square'>
            </td>
        </tr>        <tr>
            <td>
                <a href="https://www.clamav.net/">
                    <img src="others/readme_images/solutions/clamav.webp">
                </a>
            </td>
            <td>Clam AntiVirus (ClamAV) is a free software, cross-platfom antimalware toolkit able to detect many types of malware, including viruses. ClamAV includes a command-line scanner, automatic database updater, and a scalable multi-threaded daemon running on an anti-virus engine from a shared library. FreshClam is a virus database update tool for ClamAV. ClamAV Daemon checks periodically for virus database definition updates, downloads, installs them, and notifies clamd to refresh it's in-memory virus database cache.</td>
            <td>
                <img alt='Maturity: Production' src='https://img.shields.io/badge/Maturity-Production-blightgreen?style=flat-square'>
            </td>
        </tr>        <tr>
            <td>
                <a href="https://suricata.io">
                    <img src="others/readme_images/solutions/suricata.webp">
                </a>
            </td>
            <td>Suricata is the leading independent open source threat detection engine. By combining intrusion detection (IDS), intrusion prevention (IPS), network security monitoring (NSM) and PCAP processing, Suricata can quickly identify, stop, and assess even the most sophisticated attacks.</td>
            <td>
                <img alt='Maturity: Under refactoring' src='https://img.shields.io/badge/Maturity-Under%20refactoring-yellowgreen?style=flat-square'>
            </td>
        </tr>
        <tr>
            <td colspan=3><center>More coming soon...</center></td>
        </tr>
    </tbody>
</table>

# Requirements

MutableSecurity requires only [Python 3.9 or above](https://www.python.org/downloads/).

# Installation

## Via Debian Repository

```bash
# 1. Add the GPG keyring
wget -O- https://debian.mutablesecurity.io/pubkey.gpg | \
    gpg --dearmor | \
    sudo tee /usr/share/keyrings/mutablesecurity.gpg > /dev/null

# 2. Add the Debian repository
echo "deb [signed-by=/usr/share/keyrings/mutablesecurity.gpg] https://debian.mutablesecurity.io bullseye main" |\
    sudo tee /etc/apt/sources.list.d/mutablesecurity.list

# 3. Fetch the details by apt-updating
sudo apt update

# 4. Install the package
sudo apt install mutablesecurity
```

## Via PyPi

Just run `pip install mutablesecurity`. Ensure that `/home/<username>/.local/bin` is added into your `$PATH` variable.

## Debian Package

From the [Releases](https://github.com/MutableSecurity/mutablesecurity/releases) section in this repository, download the latest Debian package. After that, install it using `dpkg -i mutablesecurity.deb`.

## Executable

In the same [Releases](https://github.com/MutableSecurity/mutablesecurity/releases) section, you can find executables that wrap up the whole project. Only download the latest version and place it into a convenient location (for example, `/usr/bin` or `/home/<username>/.local/bin`).

# Demo

<div align="center">
    <img src="others/readme_images/demo.webp" width="100%" alt="Demo">
</div>

# Support

If you have any type of suggestion (for example, proposals for new functionalities or support for other security solutions), please open an issue or drop us a line at [hello@mutablesecurity.io](mailto:hello@mutablesecurity.io).

# Contributing

To find out how you can contribute to this project, check out our [contribution guide](.github/CONTRIBUTING.md).