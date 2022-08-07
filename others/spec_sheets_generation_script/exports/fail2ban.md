# Fail2ban

## Metadata

- **Identifier**: `fail2ban`
- **Maturity**: Production

### Categories

- Host Intrusion Prevention System

## Description

Fail2ban is an intrusion prevention software framework that protects Unix-like servers from brute-force attacks. It scans log files and bans IP addresses conducting too many failed operations (for example, login attempts). This module targets Debian-based operating systems and has already set a SSH jail.

## Actions

<table>
    <thead>
        <tr>
            <th>Identifier</th>
            <th>Description</th>
            <th>Expected Parameters Keys and Types</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><code>reload_jails</code></td>
            <td>Reload the jail.</td>
            <td></td>
        </tr>
        <tr>
            <td><code>restart_service</code></td>
            <td>Restarts the Fail2ban service.</td>
            <td></td>
        </tr>
        <tr>
            <td><code>start_service</code></td>
            <td>Starts the Fail2ban service.</td>
            <td></td>
        </tr>
        <tr>
            <td><code>stop_service</code></td>
            <td>Stops the Fail2ban service.</td>
            <td></td>
        </tr>
        <tr>
            <td><code>unban</code></td>
            <td>Unbans an IP address from a jail.</td>
            <td><code>jail_name</code> (<code>STRING</code>), <code>ip</code> (<code>STRING</code>)</td>
        </tr>
    </tbody>
</table>

## Information

<table>
    <thead>
        <tr>
            <th>Identifier</th>
            <th>Description</th>
            <th>Type</th>
            <th>Properties</th>
            <th>Default Value</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><code>active_jails</code></td>
            <td>Active jails</td>
            <td><code>LIST_OF_STRINGS</code></td>
            <td><code>METRIC</code>, <code>READ_ONLY</code></td>
            <td></td>
        </tr>
        <tr>
            <td><code>ban_seconds</code></td>
            <td>Ban duration in seconds</td>
            <td><code>INTEGER</code></td>
            <td><code>CONFIGURATION</code>, <code>MANDATORY</code>, <code>WITH_DEFAULT_VALUE</code>, <code>NON_DEDUCTIBLE</code>, <code>WRITABLE</code></td>
            <td><code>3600</code></td>
        </tr>
        <tr>
            <td><code>banned_ips</code></td>
            <td>Banned IPs from all jails</td>
            <td><code>LIST_OF_STRINGS</code></td>
            <td><code>METRIC</code>, <code>READ_ONLY</code></td>
            <td></td>
        </tr>
        <tr>
            <td><code>ignored_ips</code></td>
            <td>IPs to ignore. Can identify machines like the pentest-related one or controlled strictly by your cloud provider.</td>
            <td><code>LIST_OF_STRINGS</code></td>
            <td><code>CONFIGURATION</code>, <code>OPTIONAL</code>, <code>WITH_DEFAULT_VALUE</code>, <code>NON_DEDUCTIBLE</code>, <code>WRITABLE</code></td>
            <td><code>127.0.0.1</code></td>
        </tr>
        <tr>
            <td><code>jails_count</code></td>
            <td>Number of set jails</td>
            <td><code>INTEGER</code></td>
            <td><code>METRIC</code>, <code>READ_ONLY</code></td>
            <td></td>
        </tr>
        <tr>
            <td><code>max_retries</code></td>
            <td>Login attempts limit above which a user is banned</td>
            <td><code>INTEGER</code></td>
            <td><code>CONFIGURATION</code>, <code>MANDATORY</code>, <code>WITH_DEFAULT_VALUE</code>, <code>NON_DEDUCTIBLE</code>, <code>WRITABLE</code></td>
            <td><code>3</code></td>
        </tr>
        <tr>
            <td><code>ssh_port</code></td>
            <td>Port on which the SSH server runs</td>
            <td><code>INTEGER</code></td>
            <td><code>CONFIGURATION</code>, <code>MANDATORY</code>, <code>WITH_DEFAULT_VALUE</code>, <code>NON_DEDUCTIBLE</code>, <code>WRITABLE</code></td>
            <td><code>22</code></td>
        </tr>
    </tbody>
</table>

## Logs

<table>
    <thead>
        <tr>
            <th>Identifier</th>
            <th>Description</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><code>logs</code></td>
            <td>Default log location</td>
        </tr>
    </tbody>
</table>

## Tests

<table>
    <thead>
        <tr>
            <th>Identifier</th>
            <th>Description</th>
            <th>Type</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><code>active_service</code></td>
            <td>Checks if the Fail2ban service is active.</td>
            <td><code>OPERATIONAL</code></td>
        </tr>
        <tr>
            <td><code>command</code></td>
            <td>Checks if the Fail2ban client is registered as a command.</td>
            <td><code>PRESENCE</code></td>
        </tr>
        <tr>
            <td><code>healthcheck</code></td>
            <td>Checks if Fail2ban blocks an IP when identifying multiple logs generated by it.</td>
            <td><code>SECURITY</code></td>
        </tr>
        <tr>
            <td><code>ubuntu</code></td>
            <td>Checks if the operating system is Ubuntu.</td>
            <td><code>REQUIREMENT</code></td>
        </tr>
    </tbody>
</table>

## References

- [https://www.fail2ban.org](https://www.fail2ban.org)
- [https://github.com/fail2ban/fail2ban](https://github.com/fail2ban/fail2ban)
