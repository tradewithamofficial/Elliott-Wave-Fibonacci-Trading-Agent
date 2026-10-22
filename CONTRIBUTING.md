# Contributing

Open an Issue with a sanitized reproduction before proposing a substantial change.
Preserve the tested Codex CLI, editable prompts and chart-selection behavior.
Never include credentials, local responses, browser/session state or machine-specific
diagnostics in a pull request. Use focused offline mocks, not paid/live chart actions.

```powershell
.\.venv\Scripts\python.exe -B -m unittest tests.test_simple_cli.SimpleCliTests tests.test_telegram_response
```

Use a focused branch and explain changes, validation and limitations. TradingView,
Codex, Node and Telegram remain external integrations. A passing offline suite does
not establish model quality or account/tool availability. Contributions are under MIT.
