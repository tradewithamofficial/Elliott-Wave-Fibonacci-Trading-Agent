# Security and private data

Supported release: v1.0.0. Never post a bot token, Codex auth file, cookies, account
identifiers or raw private run records in an Issue or pull request.

For a sensitive report, use GitHub's private vulnerability reporting on this
repository if enabled. Otherwise open a minimal Issue requesting a private contact
method without disclosing exploit details or credentials. Rotate exposed secrets
through the relevant provider; do not share them with maintainers.

The app reuses locally installed Codex/TradingView MCP configuration. Keep those
installations and policies under your control. Editable prompts affect model
behavior; do not replace them with untrusted instructions. There is no exchange
connection or order execution feature. Use a dedicated chart and inspect partial
results after failures. Telegram delivery has no automatic retry.

Private configuration belongs beside main.py/the EXE and is excluded from Git.
Do not redistribute a release folder after adding credentials or response records.
