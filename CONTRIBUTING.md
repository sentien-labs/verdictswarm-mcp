# Contributing

Thanks for helping improve VerdictSwarm MCP.

## What This Project Optimizes For

This package is a thin, reliable MCP wrapper around the VerdictSwarm API. Contributions should keep the server:

- easy to install in MCP-compatible clients;
- explicit about network, API key, and payment behavior;
- safe around secrets and wallet/user data;
- covered by fast offline tests.

## Local Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

The test suite should run without a live API key. Use mocked clients or fixtures for behavior that depends on the VerdictSwarm API.

## Good First Contributions

- Improve setup examples for MCP clients.
- Add tests around formatting, config parsing, or error states.
- Improve documentation for environment variables and failure modes.
- Add small examples that do not require private keys, wallet data, or paid scans.

## Pull Request Checklist

- Run `pytest -q`.
- Add or update tests when behavior changes.
- Update README/examples when commands, config, or tool output changes.
- Do not commit `VS_API_KEY`, `.env`, private reports, wallet/customer research, or generated local output.

## Security And Data Safety

Do not open public issues for secrets, private reports, or vulnerabilities. Use GitHub private vulnerability reporting when available.
