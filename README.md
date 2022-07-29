<div align="center">
    <img src="others/readme_images/cover.webp" width="600px" alt="Cover">
    <br/><br/>
    <img alt="Monthly Downloads on PyPi" src="https://img.shields.io/pypi/dm/mutablesecurity?color=blue&logoColor=white&label=PyPi%20Downloads&logo=pypi&style=flat-square">
    <img alt="Stable Version of PyPi" src="https://img.shields.io/pypi/v/mutablesecurity?color=blue&label=PyPi%20Stable%20Version&logo=pypi&logoColor=white&style=flat-square">
    <img alt="GitHub Stars" src="https://img.shields.io/github/stars/mutablesecurity/mutablesecurity?color=blue&logoColor=white&label=GitHub%20Stars&logo=github&style=flat-square">
    <img alt="GitHub closed issues" src="https://img.shields.io/github/issues-closed/mutablesecurity/mutablesecurity?color=blue&logoColor=white&label=GitHub%20Issues&logo=github&style=flat-square">
    <img alt="License" src="https://img.shields.io/github/license/mutablesecurity/mutablesecurity?color=lightgray&logoColor=white&label=License&logo=opensourceinitiative&style=flat-square">
    <br/>
    <img alt="Snyk Vulnerabilities" src="https://img.shields.io/snyk/vulnerabilities/github/mutablesecurity/mutablesecurity?label=Snyk%20Vulnerabilities&logo=snyk&logoColor=white&style=flat-square">
    <img alt="Deepsource active issues" src="https://deepsource.io/gh/MutableSecurity/mutablesecurity.svg/?label=active+issues&show_trend=true&token=p678jq0qtDRJaOXo_Whya-un)](https://deepsource.io/gh/MutableSecurity/mutablesecurity/?ref=repository-badge">
    <img alt="Coveralls Coverage" src="https://img.shields.io/coveralls/github/mutablesecurity/mutablesecurity?color=brightgreen&logoColor=white&label=Coveralls%20Coverage&logo=coveralls&style=flat-square">
    <img alt="Dependabot" src="https://img.shields.io/badge/Dependabot-enabled-brightgreen?logo=dependabot&style=flat-square&logoColor=white">
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
            <th>Short Description</th>
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
            <td>teler is an real-time intrusion detection and threat alert based on web log. Targets only nginx installed on Ubuntu.</td>
            <td>
                <img alt="Status: Production" src="https://img.shields.io/badge/Status-Production-blightgreen?style=flat-square">
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
            <td>
                <a href="https://letsencrypt.org/">
                    <img src="others/readme_images/solutions/lets_encrypt.webp">
                </a>
            </td>
            <td>Let's Encrypt is a free, automated, and open certificate authority brought to you by the nonprofit Internet Security Research Group (ISRG). Certbot is a free, open source software tool for automatically using Let's Encrypt certificates on manually-administrated websites to enable HTTPS.</td>
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