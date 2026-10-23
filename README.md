# Trade With AM — Elliott Wave & Fibonacci Trading Agent

**Version 1.0.0 · Windows x64 · MIT**

A dark CustomTkinter desktop application using your existing Codex CLI and
TradingView MCP connection. Choose Swing, Intraday, or both to request Elliott
Wave and Fibonacci scenarios, drawn and grouped directly by the selected model.
Check Entry Conditions reassesses existing scenarios without requesting drawing changes.

This is a **chart-analysis application, not an automated trade-execution system**.
Scenarios are conditional interpretations, not confirmed entries. External
accounts, subscriptions and AI usage are separate. Analysis can be wrong.

## Install or Customize with ChatGPT — No Coding Experience Required to Start

Copy the [installation guide](INSTALL-WITH-CHATGPT.md) into a new ChatGPT conversation
for one-step-at-a-time setup. The [full ChatGPT Master Prompt](docs/CHATGPT_MASTER_PROMPT.md)
also guides optional, focused development using Codex after installation works.
Start with the [Windows v1.0.0 release](https://github.com/tradewithamofficial/Elliott-Wave-Fibonacci-Trading-Agent/releases/tag/v1.0.0); Python/PyCharm are not needed
for its EXE, but the existing external Codex/TradingView MCP setup is required for
analysis. Future examples include implementing the visible **All Charts** checkbox;
multi-chart processing is not implemented in V1. No code or release asset changes
are made by this documentation update.

## Windows release

Download the v1.0.0 Windows ZIP from this repository's Releases section:

- Repository: https://github.com/tradewithamofficial/Elliott-Wave-Fibonacci-Trading-Agent
- Releases: https://github.com/tradewithamofficial/Elliott-Wave-Fibonacci-Trading-Agent/releases
- Asset: `ElliottWaveFibonacciTradingAgent-v1.0.0-windows-x64.zip`

Extract the whole ZIP into a writable folder such as Documents. Keep `_internal`,
`reference_simple`, the EXE and notices together. Run
`ElliottWaveFibonacciTradingAgent.exe`. Python and PyCharm are not required for
this one-folder Windows x64 application. It is unsigned; follow normal Windows
security policy. See [Windows instructions](RELEASE-SETUP.txt).

## External prerequisites

- TradingView Desktop, signed in, with your working debugging/CDP setup on port
  9222. Start with a dedicated saved standard-candlestick chart.
- A working TradingView MCP connector, its dependencies and Node.js. Default
  connector folder: `%USERPROFILE%\tradingview-mcp`.
- Installed and authenticated Codex CLI, the existing TradingView MCP configuration,
  and account access to a supported model. A model appearing in the dropdown
  does not guarantee account access. Live requests can consume paid usage.
- Optional Telegram bot credentials and numeric destination chat ID for analysis
  delivery. The bot needs permission to send there.

These programs, connector installations, accounts, credentials and sessions are
not bundled. Reuse your working setup; see [installation](INSTALL-WITH-CHATGPT.md).

## Use

1. Start your existing TradingView/MCP setup and authenticate Codex.
2. Select an exact exchange-qualified symbol (for example `BYBIT:BTCUSDT.P`) and
   a supported model. The app checks the selected chart. Keep its tab stable.
   Leave **All Charts** unchecked; it is not implemented.
3. Select **Swing**, **Intraday**, or both. At least one is required for the left button.
4. Click **Elliott Wave & Fibonacci Analysis** and review the confirmation. Swing
   considers Daily/4H/1H. Intraday considers 15m and available Swing context.
   Both completes Swing before starting Intraday.
5. Review the copyable response and chart objects. CLI completion is not independent
   Python verification of drawings. No automatic old-group deletion, replacement,
   rollback or retry is performed on this path.
6. **Check Entry Conditions** ignores the checkboxes and inspects existing scenarios
   on the current chart. It requests read-only behavior and provides WAIT, MONITOR
   or conditional guidance. It never sends Telegram or places orders.

Group names are `Elliott Wave Swing Scenario 1`, `2`, `3` and
`Elliott Wave Intraday Scenario 1`, `2`, `3`. Scenarios and trade ideas require
supporting evidence; a drawn scenario does not imply a confirmed entry. Prefer
a clean chart for initial analysis and inspect existing groups before another run.

## Editable prompts and responses

Edit these files beside the EXE or in the source project:

```text
reference_simple/swing.txt
reference_simple/Intraday.txt
reference_simple/EntryConditions.txt
```

They are read for each request. Preserve chart identity, unrelated-object and
read-only entry-inquiry instructions. The existing MCP configuration applies;
the app does not install a connector or change global Codex settings. Tool
approvals can require operator action.

Local results are saved under `responses/` beside the EXE/source, including
`swing-response.txt`, `intraday-response.txt` and `entry-conditions-response.txt`.
Keep these private; they are excluded from source and release packages.

## Telegram

Copy `telegram_config.example.json` to `telegram_config.local.json` beside the EXE
or `main.py`, outside `_internal`. Fill `bot_token` and the numeric `chat_id`
privately, both as JSON strings. Never publish the private file or credentials.
Only a blank example is distributed. Missing config does not prevent startup.

Successful left-button analysis sends the **complete original response**, formatted
with headings/bold, vertical tables and readable URLs. Long reports use numbered
parts. Both sends Swing before Intraday. Nothing is summarized or truncated.
Delivery stops on failure without automatic retry; the analysis remains copyable.
Acceptance is separate from analysis success and does not prove somebody read it.

From source, `tests/manual_telegram_test.py` can preview a saved response with
`SEND_TELEGRAM=False`, without Codex, TradingView or credential access. It prints
and saves all parts. Set True only for an intentional real send. Every manual
True run sends again; inspect the chat before repeating an uncertain attempt.

## Run from source

From the cloned/extracted repository in PowerShell, using Python with Tkinter
(3.14 is the locally tested build series):

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

For nonstandard installations, user environment variables `SR_CODEX_PATH`,
`SR_NODE_PATH` and `SR_TRADINGVIEW_MCP_DIR` can specify the installed Codex binary,
node.exe and connector folder. Restart the application after changing them.

## Build and offline checks

```powershell
.\build.ps1
.\.venv\Scripts\python.exe -B -m unittest tests.test_simple_cli.SimpleCliTests tests.test_telegram_response
```

The reference application's PyInstaller onedir/windowed approach is reused.
Output is `release/ElliottWaveFibonacciTradingAgent/`. Preserve/move an existing
output folder before rebuilding; local release data is not overwritten. Public
prompts, assets, blank config example and notices are copied explicitly.
See [release notes](docs/RELEASE-v1.0.0.md).

## Limits, support and license

The maintainer's local integration has been tested; Codex/MCP/TradingView changes
can affect other installations. Interrupted analysis can leave partial chart
results; inspect before another request. There is no exchange-account integration
or trade execution. Historical responses are not current entry confirmations.

Use repository Issues for sanitized bug reports. See [SECURITY.md](SECURITY.md)
and [CONTRIBUTING.md](CONTRIBUTING.md). Do not post private logs, account/chart
identifiers or credentials.

[MIT](LICENSE), copyright 2026 Trade With AM. Bundled dependencies retain their
own terms: [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) and
`third_party_licenses/`. Supplied artwork is included under MIT to the extent
the project owner holds applicable rights.
