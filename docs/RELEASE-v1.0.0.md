# v1.0.0 — Windows release

Trade With AM — Elliott Wave & Fibonacci Trading Agent.

- Swing, Intraday and combined analysis using the existing Codex CLI/MCP setup.
- Up to three evidence-supported scenarios per category, with direct model drawing/grouping.
- Read-only Check Entry Conditions inquiry using existing scenarios.
- Complete original-response Telegram HTML with sequential numbered parts.
- Editable public prompts, green robot icon and Elliott Wave chart illustration.

Windows distribution: `ElliottWaveFibonacciTradingAgent-v1.0.0-windows-x64.zip`.
Extract the entire one-folder build; do not move only the EXE. Codex CLI, Node.js,
TradingView Desktop and the existing MCP connector remain external prerequisites.
Telegram credentials are optional and private. See README and RELEASE-SETUP.txt.

Build uses PyInstaller 6.22.3 and its hooks, with the reference application's
windowed/onedir convention. Source prompts are copied byte-for-byte to
`reference_simple` beside the EXE. No connector, credentials, response records,
environment, IDE files or diagnostic experiments are distributed.

Release verification checks startup, controls/assets, prompt/resource paths,
Codex/model discovery, read-only watchlist loading and offline formatting tests.
It does not run Astra analysis, change chart objects, place orders or send Telegram.
The EXE is unsigned. External services and private APIs can change; only the
maintainer's local installation has been checked. This is chart analysis, not
automated trade execution. No automatic group cleanup, retry or rollback occurs.
