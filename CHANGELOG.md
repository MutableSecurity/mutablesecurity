# Changelog

## `v0.3.0` | 2022-08-07

### Added

- Automatic documentation of modules, that are used inside the new website's documentation
- Integration with Poe for task running

### Changed

- Upgrading two modules, teler and Fail2ban, to the new API
- Refactoring the whole codebase
- Upgrading the existent solutions API

### Removed

- Removing (for a while) the support for Suricata and Let's Encrypt, as they became outdated due to the new API

## `v0.2.0` | 2022-06-01

### Added

- Support for teler and Let's Encrypt
- Deployment to multiple hosts, in parallel
- Remote deployment with SSH key
- Feedback form
- Check for Python version

## `v0.1.0` | 2022-05-04

### Added

- Support for Suricata
- Remote deployment via password-based SSH
- Local deployment
- Command line interface