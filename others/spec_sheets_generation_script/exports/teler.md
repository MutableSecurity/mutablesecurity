# teler

## Metadata

- **Identifier**: `teler`
- **Maturity**: Production

### Categories

- Web Intrusion Detection System

## Description

teler is a real-time intrusion detection and threat alert based on web log. Targets only nginx installed on Ubuntu.

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
            <td><code>start_process</code></td>
            <td>Start teler's process</td>
            <td></td>
        </tr>
        <tr>
            <td><code>stop_process</code></td>
            <td>Stop teler's process</td>
            <td></td>
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
            <td><code>alerts_count</code></td>
            <td>Total number of generated alerts</td>
            <td><code>INTEGER</code></td>
            <td><code>METRIC</code>, <code>READ_ONLY</code></td>
            <td></td>
        </tr>
        <tr>
            <td><code>architecture</code></td>
            <td>Binary's architecture</td>
            <td><code>STRING</code></td>
            <td><code>CONFIGURATION</code>, <code>READ_ONLY</code>, <code>AUTO_GENERATED_BEFORE_INSTALL</code></td>
            <td></td>
        </tr>
        <tr>
            <td><code>command</code></td>
            <td>Command used to create teler's process and crontab</td>
            <td><code>STRING</code></td>
            <td><code>CONFIGURATION</code>, <code>READ_ONLY</code>, <code>AUTO_GENERATED_BEFORE_INSTALL</code></td>
            <td></td>
        </tr>
        <tr>
            <td><code>daily_alerts_count</code></td>
            <td>Total number of alerts generated today</td>
            <td><code>INTEGER</code></td>
            <td><code>METRIC</code>, <code>READ_ONLY</code></td>
            <td></td>
        </tr>
        <tr>
            <td><code>fail2ban_integration</code></td>
            <td>Whether the integration with Fail2ban is activated</td>
            <td><code>BOOLEAN</code></td>
            <td><code>CONFIGURATION</code>, <code>MANDATORY</code>, <code>WITH_DEFAULT_VALUE</code>, <code>NON_DEDUCTIBLE</code>, <code>WRITABLE</code></td>
            <td><code>False</code></td>
        </tr>
        <tr>
            <td><code>log_format</code></td>
            <td>Format in which the messages are logged</td>
            <td><code>STRING</code></td>
            <td><code>CONFIGURATION</code>, <code>MANDATORY</code>, <code>WITH_DEFAULT_VALUE</code>, <code>NON_DEDUCTIBLE</code>, <code>WRITABLE</code></td>
            <td>$<code>remote_addr</code> $<code>remote_user</code> - [$<code>time_local</code>] "$<code>request_method</code> $<code>request_uri</code> $<code>request_protocol</code>" $<code>status</code> $<code>body_bytes_sent</code> "$<code>http_referer</code>" "$<code>http_user_agent</code>"</td>
        </tr>
        <tr>
            <td><code>log_location</code></td>
            <td>Location in which nginx logs messages</td>
            <td><code>STRING</code></td>
            <td><code>CONFIGURATION</code>, <code>MANDATORY</code>, <code>WITH_DEFAULT_VALUE</code>, <code>NON_DEDUCTIBLE</code>, <code>WRITABLE</code></td>
            <td>/<code>var</code>/<code>log</code>/<code>nginx</code>/<code>access.log</code></td>
        </tr>
        <tr>
            <td><code>port</code></td>
            <td>Port on which the web server runs</td>
            <td><code>INTEGER</code></td>
            <td><code>CONFIGURATION</code>, <code>MANDATORY</code>, <code>WITH_DEFAULT_VALUE</code>, <code>NON_DEDUCTIBLE</code>, <code>WRITABLE</code></td>
            <td><code>80</code></td>
        </tr>
        <tr>
            <td><code>top_attackers</code></td>
            <td>Top 3 attackers</td>
            <td><code>LIST_OF_STRINGS</code></td>
            <td><code>METRIC</code>, <code>READ_ONLY</code></td>
            <td></td>
        </tr>
        <tr>
            <td><code>top_attacks_types</code></td>
            <td>Top 3 types of web attacks</td>
            <td><code>LIST_OF_STRINGS</code></td>
            <td><code>METRIC</code>, <code>READ_ONLY</code></td>
            <td></td>
        </tr>
        <tr>
            <td><code>version</code></td>
            <td>Installed version</td>
            <td><code>STRING</code></td>
            <td><code>METRIC</code></td>
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
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><code>json_alerts</code></td>
            <td>Generated alerts in JSON format</td>
        </tr>
        <tr>
            <td><code>text_alerts</code></td>
            <td>Generated alerts in plaintext format</td>
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
            <td><code>bad_user_agent_detection</code></td>
            <td>Checks if teler detects a request with a bad user agent.</td>
            <td><code>SECURITY</code></td>
        </tr>
        <tr>
            <td><code>internet_access</code></td>
            <td>Checks if host has Internet access.</td>
            <td><code>REQUIREMENT</code></td>
        </tr>
        <tr>
            <td><code>nginx_active</code></td>
            <td>Checks if nginx is installed and the service is active.</td>
            <td><code>REQUIREMENT</code></td>
        </tr>
        <tr>
            <td><code>presence</code></td>
            <td>Checks if a file is present.</td>
            <td><code>PRESENCE</code></td>
        </tr>
        <tr>
            <td><code>process_running</code></td>
            <td>Checks if teler's process is running.</td>
            <td><code>OPERATIONAL</code></td>
        </tr>
        <tr>
            <td><code>supported_architecture</code></td>
            <td>Checks if there is any build for this architecture.</td>
            <td><code>REQUIREMENT</code></td>
        </tr>
    </tbody>
</table>

## References

- [https://teler.app](https://teler.app)
- [https://github.com/kitabisa/teler](https://github.com/kitabisa/teler)
