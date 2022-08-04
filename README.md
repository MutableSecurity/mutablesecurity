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
- [Installation](#installation)
  - [Requirements](#requirements)
- [Demo](#demo)
- [Support](#support)
- [Contributing](#contributing)

---

# Description

**MutableSecurity** is a software product for making cybersecurity solution management easier and more accessible, from deployment and configuration to monitoring.

Despite the current lack of complex functionalities, we have a vision in mind that we hope to achieve in the near future. As we must begin somewhere, the first step in our progress is this command line interface for automatic management of cybersecurity solutions.

Come join the MutableSecurity journey!

## Functionalities

- Multiple solution supported so far (and more under development)
- Multiple authentication methods
    - Password-based for the host on which the tool is installed
    - Password-based or key-based SSH for remote hosts
- Deployments to multiple hosts with the same command
- Intuitive command line interface

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
                <a href="https://www.fail2ban.org">
                    <img src="others/readme_images/solutions/fail2ban.webp">
                </a>
            </td>
            <td>Fail2ban is an intrusion prevention software framework that protects Unix-like servers from brute-force attacks. It scans log files and bans IP addresses conducting too many failed operations (for example, login attempts). This module targets Debian-based operating systems and has already set a SSH jail.</td>
            <td>
                <img alt="Status: Production" src="https://img.shields.io/badge/Status-Production-blightgreen?style=flat-square">
            </td>
        </tr>
        <tr>
            <td>
                <a href="https://teler.app">
                    <img src="others/readme_images/solutions/teler.webp">
                </a>
            </td>
            <td>teler is a real-time intrusion detection and threat alert based on web log. Targets only nginx installed on Ubuntu.</td>
            <td>
                <img alt="Status: Production" src="https://img.shields.io/badge/Status-Production-blightgreen?style=flat-square">
            </td>
        </tr>
        <tr>
            <td>
                <a href="https://letsencrypt.org">
                    <img src="others/readme_images/solutions/lets_encrypt.webp">
                </a>
            </td>
            <td>Let's Encrypt is a free, automated, and open certificate authority brought to you by the nonprofit Internet Security Research Group (ISRG). Certbot is a free, open source software tool for automatically using Let's Encrypt certificates on manually-administrated websites to enable HTTPS.</td>
            <td>
                <img alt="Status: Under refactoring" src="https://img.shields.io/badge/Status-Under%20refactoring-yellowgreen?style=flat-square">
            </td>
        </tr>
        <tr>
            <td>
                <a href="https://suricata.io">
                    <img src="others/readme_images/solutions/suricata.webp">
                </a>
            </td>
            <td>Suricata is the leading independent open source threat detection engine. By combining intrusion detection (IDS), intrusion prevention (IPS), network security monitoring (NSM) and PCAP processing, Suricata can quickly identify, stop, and assess even the most sophisticated attacks.</td>
            <td>
                <img alt="Status: Under refactoring" src="https://img.shields.io/badge/Status-Under%20refactoring-yellowgreen?style=flat-square">
            </td>
        </tr>
        <tr>
            <td colspan=3><center>More coming soon...</center></td>
        </tr>
    </tbody>
</table>

# Installation

The easiest way to install MutableSecurity is from PyPI. Just run `pip install mutablesecurity` and you'll have everything set!

## Requirements

The only requirements are [Python 3.9](https://www.python.org/downloads/) and [pip](https://pip.pypa.io/en/stable/installation/).

To avoid warnings when using pip to install Python scripts, add `/home/<username>/.local/bin` (where `<username>` identifies the current user) to your `$PATH` variable.

# Demo

<div align="center">
    <img src="others/readme_images/demo.webp" width="100%" alt="Demo">
</div>

# Support

If you have any type of suggestion (for example, proposals for new functionalities or support for other security solutions), please open an issue or drop us a line at [hello@mutablesecurity.io](mailto:hello@mutablesecurity.io).

# Contributing

To find out how you can contribute to this project, check out our [contribution guide](.github/CONTRIBUTING.md).