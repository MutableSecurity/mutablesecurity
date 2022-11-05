# Vector

## Metadata

- **Identifier**: `vector`
- **Maturity**: Production

### Categories

- Log Shipper

## Description

Vector is a lightweight tool for building observability pipelines. As soon as solutions are enabled in the configuration, Vector starts to send their logs to the configured Loki instance. The latter can be either on-premise or in the cloud, the only condition being to permit authentication via username and API token.

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
            <td><code>start_service</code></td>
            <td>Starts the Vector service.</td>
            <td></td>
        </tr>
        <tr>
            <td><code>stop_service</code></td>
            <td>Stops the Vector service.</td>
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
            <td><code>enabled_solutions</code></td>
            <td>Solution whose logs are processed</td>
            <td><code>LIST_OF_STRINGS</code></td>
            <td><code>CONFIGURATION</code>, <code>MANDATORY</code>, <code>NON_DEDUCTIBLE</code>, <code>WRITABLE</code></td>
            <td></td>
        </tr>
        <tr>
            <td><code>loki_endpoint</code></td>
            <td>Endpoint where Loki listens</td>
            <td><code>STRING</code></td>
            <td><code>CONFIGURATION</code>, <code>MANDATORY</code>, <code>NON_DEDUCTIBLE</code>, <code>WRITABLE</code></td>
            <td></td>
        </tr>
        <tr>
            <td><code>loki_token</code></td>
            <td>Token to authenticate to Loki</td>
            <td><code>STRING</code></td>
            <td><code>CONFIGURATION</code>, <code>MANDATORY</code>, <code>NON_DEDUCTIBLE</code>, <code>WRITABLE</code></td>
            <td></td>
        </tr>
        <tr>
            <td><code>loki_user</code></td>
            <td>User to authenticate to Loki</td>
            <td><code>STRING</code></td>
            <td><code>CONFIGURATION</code>, <code>MANDATORY</code>, <code>NON_DEDUCTIBLE</code>, <code>WRITABLE</code></td>
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
            <td><code>json_alerts</code></td>
            <td>Functional logs in JSON format</td>
            <td>/<code>var</code>/<code>log</code>/<code>vector.log</code></td>
            <td><code>JSON</code></td>
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
            <td>Checks if Vector's service is running.</td>
            <td><code>OPERATIONAL</code></td>
        </tr>
        <tr>
            <td><code>internet_access</code></td>
            <td>Checks if host has Internet access, which is required to download the package and, eventually, connect to Loki.</td>
            <td><code>REQUIREMENT</code></td>
        </tr>
        <tr>
            <td><code>present_command</code></td>
            <td>Checks if Vector is present as a command.</td>
            <td><code>PRESENCE</code></td>
        </tr>
        <tr>
            <td><code>process_running</code></td>
            <td>Checks if Vector's process is running.</td>
            <td><code>OPERATIONAL</code></td>
        </tr>
        <tr>
            <td><code>valid_configuration</code></td>
            <td>Checks if the generated Vector configuration is valid. It includes a healthcheck for the connection with Loki.</td>
            <td><code>OPERATIONAL</code></td>
        </tr>
    </tbody>
</table>

## References

- [https://vector.dev/](https://vector.dev/)
- [https://github.com/vectordotdev/vector](https://github.com/vectordotdev/vector)
