# Test Case Generator

## Secure credentials

This repository supports both:
- environment variables
- `jira-xray-config.json` config file

### Recommended setup

1. Copy `.env.example` to `.env`
2. Fill in your values
3. Do not commit `.env`

Alternatively, create a local config file:

```bash
cp jira-xray-config.example.json jira-xray-config.json
```

Then update `jira-xray-config.json` with your credentials.

## Environment variables supported

- `JIRA_EMAIL`
- `JIRA_API_TOKEN`
- `XRAY_CLIENT_ID`
- `XRAY_CLIENT_SECRET`

## Notes

- `jira-xray-config.json` is ignored by git to prevent secrets from being committed.
- Keep `jira-xray-config.example.json` in the repository as a safe template.
