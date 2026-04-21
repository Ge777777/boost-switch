# Security Policy

## Supported Scope

This repository is currently an alpha / mainline project. Security-sensitive
areas include:

- privileged write paths under `system/`
- authorization logic in `src/boost_switch/service/`
- install and verification scripts
- any behavior that can write to `/sys/devices/system/cpu/cpufreq/boost`

## Reporting A Vulnerability

Please avoid posting public exploit details for privilege-escalation,
authorization-bypass, or arbitrary-write issues.

Preferred reporting path:

1. Use the repository hosting platform's private vulnerability reporting feature
   if it is enabled.
2. If that is unavailable, contact the maintainer privately through the hosting
   platform and include reproduction steps, impacted files, and risk summary.
3. If private contact is not possible, open a minimal public issue without
   exploit details and request a private follow-up channel.

## What To Include

- affected commit / branch
- host environment
- exact reproduction steps
- expected vs actual behavior
- whether the issue requires root, group membership, or an active GNOME session

## What Not To Do

- do not publish working local privilege escalation steps in a public issue
- do not include secrets, tokens, or unrelated host data
- do not assume CI coverage replaces host verification for privileged paths
