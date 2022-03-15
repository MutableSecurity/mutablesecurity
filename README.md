<div align="center">
    <img src="others/cover.png" width="600px" alt="Cover">
</div>

<br>

---

- [Description 🖼️](#description-️)
  - [Background 👴🏼](#background-)
  - [Vision 📜](#vision-)
  - [Terminology 💬](#terminology-)
  - [Functionalities 🚀](#functionalities-)
  - [Supported Cybersecurity Solutions 📦](#supported-cybersecurity-solutions-)
- [Installation 🥡](#installation-)
  - [Requirements 🥢](#requirements-)
- [Usage and Demos 🪜](#usage-and-demos-)
- [Support 🆘](#support-)
- [Contributing 🤝](#contributing-)

---

# Description 🖼️

## Background 👴🏼

In today's fast-paced society, most people are unaware of the potential consequences of cyberattacks on their organizations. Furthermore, they do not invest in cybersecurity solutions due to the costs of setup, licensing, and maintenance.

## Vision 📜

**MutableSecurity** 🏗️ building construction is a solution for making cybersecurity solution management easier and more accessible, from deployment and configuration to monitoring.

Despite the current lack of complex functionalities, we have a vision in mind that we hope to achieve in the near future. As we must begin somewhere, the first step in our progress is this command line interface for automatic management of cybersecurity solutions.

Come join the MutableSecurity journey!

## Terminology 💬

- *Target host* (or *target machine*): A computer where the actions will be performed
- *Solution*: A cybersecurity solution that needs to be set up on a target machine.
- *Configuration*: A set of parameters (in pairs of aspect and value) specific to the solution.
- *Operation*: A manipulation of a solution that is installed or needs to be installed. Could vary from effective installation to configuration setting.
- *Deployment*: The process of installing a solution on a target host.
- *Stats*: Metrics offered by the installed solution, relevant to measure the protection provided to the machine.

## Functionalities 🚀

- Local or remote (via password-based SSH) deployment
- One solution supported so far (and more under development)
- Command line interface

## Supported Cybersecurity Solutions 📦

<table>
    <thead>
        <tr>
            <th>Supported Solution</th>
            <th>Short Description</th>
            <th>Supported Operating Systems</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><a href="https://suricata.io/"><img src="others/solutions_logos/suricata.png" width="200px"></a></td>
            <td>Open source network intrusion detection and prevention system</td>
            <td>Ubuntu 20.04 LTS or above</td>
        </tr>
        <tr>
            <td colspan=3><center>More coming soon...</center></td>
        </tr>
    </tbody>
</table>

# Installation 🥡

The easiest way to install MutableSecurity is from PyPI. Just run `pip install mutablesecurity` and you'll have everything set!

## Requirements 🥢

The only requirements are [Python 3.9](https://www.python.org/downloads/) and [pip](https://pip.pypa.io/en/stable/installation/).

# Usage and Demos 🪜

<details>
    <summary>1️⃣ Install a cybersecurity solution.</summary>

**Syntax**

`mutablesecurity --solution <solution> --operation INSTALL`

**Example**

```
➜ mutablesecurity --solution SURICATA --operation INSTALL  
🔐 Password for localhost: 
✅ Suricata is now installed on this machine.
```

*Optional*: To connect to a remote host, just add the `--remote` flag.

```
➜ mutablesecurity --remote admin@192.168.1.1:22 --solution SURICATA --operation INSTALL  
🔐 Password for admin@192.168.1.1:22:
✅ Suricata is now installed on this machine.
```

</details>

<details>
    <summary>2️⃣ Test the installed solution.</summary>

**Syntax**

`mutablesecurity --solution <solution> --operation TEST`

**Example**

```
➜ mutablesecurity --solution SURICATA --operation TEST             
🔐 Password for localhost: 
✅ Suricata works as expected.
```
</details>

<details>
    <summary>3️⃣ Get the solution configuration.</summary>

**Syntax**

`mutablesecurity --solution <solution> --operation GET_CONFIGURATION`

**Example**

```
➜ mutablesecurity --solution SURICATA --operation GET_CONFIGURATION
🔐 Password for localhost: 
✅ The configuration of Suricata was retrieved.

┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Attribute         ┃ Value    ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ mode              │ IDS      │
│ interface         │ enp3s0f1 │
│ automatic_updates │ DISABLED │
└───────────────────┴──────────┘
```
</details>

<details>
    <summary>4️⃣ Modify the configuration.</summary>

**Syntax**

`mutablesecurity --solution <solution> --operation SET_CONFIGURATION --aspect <aspect> --value <value>`

**Example**

```
➜ mutablesecurity --solution SURICATA --operation SET_CONFIGURATION --aspect mode --value IPS    
🔐 Password for localhost: 
✅ The configuration of Suricata was set.
```

*Optional*: To test the modifications, run the configuration retrieval and testing operations.

```
➜ mutablesecurity --solution SURICATA --operation GET_CONFIGURATION               
🔐 Password for localhost: 
✅ The configuration of Suricata was retrieved.

┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Attribute         ┃ Value    ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ mode              │ IPS      │
│ interface         │ enp3s0f1 │
│ automatic_updates │ DISABLED │
└───────────────────┴──────────┘
➜ mutablesecurity --solution SURICATA --operation TEST                                             
🔐 Password for localhost: 
✅ Suricata works as expected.
```
</details>

<details>
    <summary>5️⃣ Retrieve the solution statistics.</summary>

**Syntax**

`mutablesecurity --solution <solution> --operation GET_STATS`

**Example**

```
➜ mutablesecurity --solution SURICATA --operation GET_STATS
🔐 Password for localhost: 
✅ The stats of Suricata were retrieved.

┏━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Attribute    ┃ Value ┃
┡━━━━━━━━━━━━━━╇━━━━━━━┩
│ alerts_count │ 314   │
└──────────────┴───────┘
```
</details>

<details>
    <summary>6️⃣ Get help.</summary>

**Syntax**

`mutablesecurity --help` or `mutablesecurity --solution <solution> --help`

**Example**

```
➜ mutablesecurity --help

              _        _     _      __                      _ _         
  /\/\  _   _| |_ __ _| |__ | | ___/ _\ ___  ___ _   _ _ __(_| |_ _   _ 
 /    \| | | | __/ _` | '_ \| |/ _ \ \ / _ \/ __| | | | '__| | __| | | |
/ /\/\ | |_| | || (_| | |_) | |  ___\ |  __| (__| |_| | |  | | |_| |_| |
\/    \/\__,_|\__\__,_|_.__/|_|\___\__/\___|\___|\__,_|_|  |_|\__|\__, |
                  Seamlessly management of cybersecurity solutions |___/ 

Usage: cli.py [OPTIONS]

Options:
  -r, --remote TEXT               Connect to remote in the
                                  USERNAME@HOSTNAME:PORT format. If ommited,
                                  the operations are executed locally.
  -s, --solution [SURICATA]       Solution to manage
  -o, --operation [GET_CONFIGURATION|GET_STATS|INSTALL|SET_CONFIGURATION|TEST|UNINSTALL]
                                  Operation to perform
  -a, --aspect TEXT               Configuration's aspect to modify. Available
                                  only with a value (--value)
  -v, --value TEXT                New value of the configuration's aspect.
                                  Available only with an aspect (--aspect).
  --verbose
  -h, --help                      Useful information for using MutableSecurity
                                  or about a solution
```

```
➜ mutablesecurity --solution SURICATA --help

              _        _     _      __                      _ _         
  /\/\  _   _| |_ __ _| |__ | | ___/ _\ ___  ___ _   _ _ __(_| |_ _   _ 
 /    \| | | | __/ _` | '_ \| |/ _ \ \ / _ \/ __| | | | '__| | __| | | |
/ /\/\ | |_| | || (_| | |_) | |  ___\ |  __| (__| |_| | |  | | |_| |_| |
\/    \/\__,_|\__\__,_|_.__/|_|\___\__/\___|\___|\__,_|_|  |_|\__|\__, |
                  Seamlessly management of cybersecurity solutions |___/ 

Full name: Suricata Intrusion Detection and Prevention System

Description:
Suricata is the leading independent open source threat detection engine. By combining intrusion detection (IDS), intrusion prevention (IPS), network 
security monitoring (NSM) and PCAP processing, Suricata can quickly identify, stop, and assess even the most sophisticated attacks.

References:
- https://suricata.io
- https://github.com/OISF/suricata

Configuration:
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Aspect            ┃ Type ┃  Possible Values  ┃ Description                          ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ mode              │ str  │     IDS, IPS      │ Mode in which Suricata works         │
│ interface         │ str  │         *         │ Interface on which Suricata listens  │
│ automatic_updates │ str  │ ENABLED, DISABLED │ State of the automatic daily updates │
└───────────────────┴──────┴───────────────────┴──────────────────────────────────────┘
```
</details>

<details>
    <summary>7️⃣ Uninstall the solution.</summary>

**Syntax**

`mutablesecurity --solution <solution> --operation UNINSTALL`

**Example**

```
➜ mutablesecurity --solution SURICATA --operation UNINSTALL        
🔐 Password for localhost: 
✅ Suricata is no longer installed on this machine.
```
</details>

# Support 🆘

If you have any type of suggestion (for example, proposals for new functionalities or support for other security solutions), please open an issue or drop us a line at [hello@mutablesecurity.ro](mailto:hello@mutablesecurity.ro).

# Contributing 🤝

To find out how you can contribute to this project, check out our [contribution guide](CONTRIBUTING.md).