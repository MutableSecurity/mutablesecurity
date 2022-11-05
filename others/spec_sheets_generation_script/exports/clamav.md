# ClamAV

## Metadata

- **Identifier**: `clamav`
- **Maturity**: Production

### Categories

- Antimalware
- Host Protection

## Description

Clam AntiVirus (ClamAV) is a free software, cross-platfom antimalware toolkit able to detect many types of malware, including viruses. ClamAV includes a command-line scanner, automatic database updater, and a scalable multi-threaded daemon running on an anti-virus engine from a shared library. FreshClam is a virus database update tool for ClamAV. ClamAV Daemon checks periodically for virus database definition updates, downloads, installs them, and notifies clamd to refresh it's in-memory virus database cache.

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
            <td><code>start_scan</code></td>
            <td>Starts the scan containing the predifined scan options: Quarantine Location and Scan Log Location. Also, it requires the input of Scan Location.</td>
            <td><code>scan_location</code> (<code>STRING</code>)</td>
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
            <td><code>daily_infected_files_detected</code></td>
            <td>Total number of infected files detected today</td>
            <td><code>INTEGER</code></td>
            <td><code>METRIC</code>, <code>READ_ONLY</code></td>
            <td></td>
        </tr>
        <tr>
            <td><code>quarantine_location</code></td>
            <td>The location where the infected files will be moved to after the on-demand/crontab scans. Select a directory in which the quarantine will take place if you would like to change.</td>
            <td><code>STRING</code></td>
            <td><code>MANDATORY</code>, <code>WITH_DEFAULT_VALUE</code>, <code>CONFIGURATION</code>, <code>NON_DEDUCTIBLE</code>, <code>WRITABLE</code></td>
            <td>/<code>opt</code>/<code>mutablesecurity</code>/<code>clamav</code>/<code>quarantine</code>/</td>
        </tr>
        <tr>
            <td><code>scan_day_of_month</code></td>
            <td>The day (1-31, or * for any) of the month when the crontab scan will take place</td>
            <td><code>STRING</code></td>
            <td><code>OPTIONAL</code>, <code>WITH_DEFAULT_VALUE</code>, <code>CONFIGURATION</code>, <code>NON_DEDUCTIBLE</code>, <code>WRITABLE</code></td>
            <td>*</td>
        </tr>
        <tr>
            <td><code>scan_day_of_week</code></td>
            <td>The day (0-6, SUN-SAT, 7 for Sunday or * for any) of the week when the crontab scan will take place</td>
            <td><code>STRING</code></td>
            <td><code>OPTIONAL</code>, <code>WITH_DEFAULT_VALUE</code>, <code>CONFIGURATION</code>, <code>NON_DEDUCTIBLE</code>, <code>WRITABLE</code></td>
            <td><code>MON</code></td>
        </tr>
        <tr>
            <td><code>scan_hour</code></td>
            <td>The hour (0-23, or * for any) when the crontab scan will take place</td>
            <td><code>STRING</code></td>
            <td><code>OPTIONAL</code>, <code>WITH_DEFAULT_VALUE</code>, <code>CONFIGURATION</code>, <code>NON_DEDUCTIBLE</code>, <code>WRITABLE</code></td>
            <td><code>0</code></td>
        </tr>
        <tr>
            <td><code>scan_location</code></td>
            <td>The location where the on-demand/crontab scans will take place.Select a different directory if you would like to change.</td>
            <td><code>STRING</code></td>
            <td><code>MANDATORY</code>, <code>WITH_DEFAULT_VALUE</code>, <code>CONFIGURATION</code>, <code>NON_DEDUCTIBLE</code>, <code>WRITABLE</code></td>
            <td>/</td>
        </tr>
        <tr>
            <td><code>scan_log_location</code></td>
            <td>The location of the generated logs after the on-demand/crontab scans.Chose a file in which the logs will be stored if you would like to change.</td>
            <td><code>STRING</code></td>
            <td><code>MANDATORY</code>, <code>WITH_DEFAULT_VALUE</code>, <code>CONFIGURATION</code>, <code>NON_DEDUCTIBLE</code>, <code>WRITABLE</code></td>
            <td>/<code>opt</code>/<code>mutablesecurity</code>/<code>clamav</code>/<code>logs</code>/<code>logs.txt</code></td>
        </tr>
        <tr>
            <td><code>scan_minute</code></td>
            <td>The minute (0-59, or * for any) when the crontab scan will take place</td>
            <td><code>STRING</code></td>
            <td><code>OPTIONAL</code>, <code>WITH_DEFAULT_VALUE</code>, <code>CONFIGURATION</code>, <code>NON_DEDUCTIBLE</code>, <code>WRITABLE</code></td>
            <td><code>0</code></td>
        </tr>
        <tr>
            <td><code>scan_month</code></td>
            <td>The month (1-12, JAN-DEC, or * for any) when the crontab scan will take place</td>
            <td><code>STRING</code></td>
            <td><code>OPTIONAL</code>, <code>WITH_DEFAULT_VALUE</code>, <code>CONFIGURATION</code>, <code>NON_DEDUCTIBLE</code>, <code>WRITABLE</code></td>
            <td>*</td>
        </tr>
        <tr>
            <td><code>total_infected_files_detected</code></td>
            <td>Total number of infected files detected overall</td>
            <td><code>INTEGER</code></td>
            <td><code>METRIC</code>, <code>READ_ONLY</code></td>
            <td></td>
        </tr>
        <tr>
            <td><code>version</code></td>
            <td>Installed version</td>
            <td><code>STRING</code></td>
            <td><code>METRIC</code>, <code>READ_ONLY</code></td>
            <td></td>
        </tr>
    </tbody>
</table>

## Logs

<table>
    <thead>
        <tr>
            <th>Identifier</th>
            <th>Description</th>
            <th>Location</th>
            <th>Format</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><code>clamav_logs</code></td>
            <td>The logs generated by ClamAV</td>
            <td>/<code>var</code>/<code>log</code>/<code>clamav</code>/<code>clamav.log</code></td>
            <td><code>TEXT</code></td>
        </tr>
        <tr>
            <td><code>freshclam_logs</code></td>
            <td>The logs generated by FreshClam</td>
            <td>/<code>var</code>/<code>log</code>/<code>clamav</code>/<code>freshclam.log</code></td>
            <td><code>TEXT</code></td>
        </tr>
        <tr>
            <td><code>scan_logs</code></td>
            <td>The logs generated during ClamAV scanning</td>
            <td><code>ScanLogLocation</code>-<code>dependent</code></td>
            <td><code>TEXT</code></td>
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
            <td><code>active_database</code></td>
            <td>Checks if the ClamAV virus database service is active.</td>
            <td><code>OPERATIONAL</code></td>
        </tr>
        <tr>
            <td><code>eicar_detection</code></td>
            <td>Creates a EICAR-STANDARD-ANTIVIRUS-TEST-FILE and checks if ClamAV is able to detect it.</td>
            <td><code>SECURITY</code></td>
        </tr>
        <tr>
            <td><code>internet_access</code></td>
            <td>Checks if host has Internet access.</td>
            <td><code>REQUIREMENT</code></td>
        </tr>
        <tr>
            <td><code>ubuntu</code></td>
            <td>Checks if the operating system is Ubuntu.</td>
            <td><code>REQUIREMENT</code></td>
        </tr>
    </tbody>
</table>

## References

- [https://www.clamav.net/](https://www.clamav.net/)
- [https://github.com/Cisco-Talos/clamav](https://github.com/Cisco-Talos/clamav)
- [https://docs.clamav.net/Introduction.html](https://docs.clamav.net/Introduction.html)
