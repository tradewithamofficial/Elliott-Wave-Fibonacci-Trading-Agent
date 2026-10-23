# Installation — Elliott Wave & Fibonacci Trading Agent

Use your own accounts and existing supported Codex/TradingView setup. Never give
an assistant your bot token, authentication files or browser sessions.

## Windows package

1. Download [ElliottWaveFibonacciTradingAgent-v1.0.0-windows-x64.zip](https://github.com/tradewithamofficial/Elliott-Wave-Fibonacci-Trading-Agent/releases/download/v1.0.0/ElliottWaveFibonacciTradingAgent-v1.0.0-windows-x64.zip) from the [v1.0.0 release](https://github.com/tradewithamofficial/Elliott-Wave-Fibonacci-Trading-Agent/releases/tag/v1.0.0).
2. Extract the complete folder to a writable location, such as Documents.
3. Keep `_internal` and `reference_simple` beside the EXE.
4. Start TradingView Desktop with your working debug/CDP launcher on port 9222.
5. Verify the existing TradingView MCP connector is installed and connected.
6. Verify existing Codex CLI authentication; install it only if missing. Open it once so the local model
   catalog is available. Your account must support the selected model.
7. Launch `ElliottWaveFibonacciTradingAgent.exe`. Select a chart symbol and model.
   Launching/refreshing does not itself run analysis or send Telegram.

Node.js, TradingView Desktop, the connector, Codex CLI and account credentials are
not included. The connector defaults to `%USERPROFILE%\tradingview-mcp`; user
environment variables `SR_TRADINGVIEW_MCP_DIR`, `SR_NODE_PATH` and `SR_CODEX_PATH`
can point to an existing nonstandard installation. Restart the app afterward.

## Source installation

Open PowerShell in the cloned/extracted project folder. Python 3.14 with Tkinter
is the locally tested series; the packaged app does not require Python.

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

## Optional private Telegram setup

Beside `main.py` or the EXE, copy the blank `telegram_config.example.json` to
`telegram_config.local.json`. Enter `bot_token` and exact numeric `chat_id` as
quoted JSON strings locally. Do not put the private file in `_internal`, GitHub,
a shared ZIP, screenshots or chat messages. The bot must be allowed to send.

Successful left-button analysis sends the full original response in numbered
parts. The entry inquiry does not send. Missing config or failed delivery preserves
the copyable analysis without automatic retry. Source users can preview an old
report via `tests/manual_telegram_test.py` with `SEND_TELEGRAM=False` first.

## First use and troubleshooting

Use a dedicated saved chart with standard candles and an exact exchange-qualified
symbol. Confirm each requested analysis; keep the tab stable. Start with Swing
only if learning the workflow. No chart-modifying test is required to verify
installation. Use Show Status for errors, but redact private data before sharing.

If the model/connector is unavailable, fix the external installation or approval
policy interactively. Do not grant unrestricted tools just to suppress an error.
If analysis is interrupted, inspect existing chart objects before another request.
The app does not place orders. See README and RELEASE-SETUP.txt for limitations.

## Copy into ChatGPT — guided installation

Copy the whole prompt below into a new ChatGPT conversation. It covers setup;
use the [full Master Prompt](docs/CHATGPT_MASTER_PROMPT.md) for optional development
after installation works. Existing Windows/source/Telegram instructions above remain applicable.

```text
You are my patient installation assistant for Trade With AM — Elliott Wave & Fibonacci Trading Agent.
Official repository: https://github.com/tradewithamofficial/Elliott-Wave-Fibonacci-Trading-Agent
Windows release: https://github.com/tradewithamofficial/Elliott-Wave-Fibonacci-Trading-Agent/releases/tag/v1.0.0
Windows ZIP: https://github.com/tradewithamofficial/Elliott-Wave-Fibonacci-Trading-Agent/releases/download/v1.0.0/ElliottWaveFibonacciTradingAgent-v1.0.0-windows-x64.zip
Full installation/development Master Prompt: https://github.com/tradewithamofficial/Elliott-Wave-Fibonacci-Trading-Agent/blob/main/docs/CHATGPT_MASTER_PROMPT.md
Existing MCP video: https://youtu.be/Qc6d5M-RPGc

Ask first what operating system I use, then wait. Check my experience and existing
installations before recommending new software. Give ONE practical action or
diagnostic per turn, tell me where to run it, and wait for my result. Explain terms.
Read the current README/release files. Verify the exact ZIP; do not invent links.
The Windows EXE needs no separate Python/PyCharm, but analysis needs installed
TradingView Desktop, Node.js, the existing TradingView MCP setup, authenticated
Codex CLI and access/usage for the selected model. Other operating systems need
separate source-compatibility checks; do not promise the Windows EXE works there.

Do not assume ordinary TradingView launch enables CDP. Before diagnosing code,
verify the existing connector's debug endpoint (default loopback port 9222), then
the correct saved standard-candlestick chart/tab/pane. Explain one read-only
PowerShell check at a time, for example:
Invoke-RestMethod 'http://127.0.0.1:9222/json/list' | Select-Object type,title
Use the actual configured host/port if overridden. Check the existing documented
launcher if it fails; ask before closing/relaunching any running instance. Do not
expose debugging publicly, kill sessions blindly or reinstall a working connector.

Verify existing Node/Codex versions, then use codex login status and codex mcp list
where supported, one result per turn. Use official Codex docs if something is
missing, and let me sign in privately. A local model dropdown is not proof of
account access; do not run a paid model test automatically or invent model IDs.
Reuse verified SR_CODEX_PATH, SR_NODE_PATH or SR_TRADINGVIEW_MCP_DIR overrides for
nonstandard installations only when needed; restart the app after changes.

Extract the WHOLE ZIP to a writable folder and launch ElliottWaveFibonacciTradingAgent.exe.
Keep _internal, notices, blank configuration and any reference_simple folder
together. Do not run inside the ZIP or copy only the EXE. Reuse the source setup
in README if I deliberately choose Python; do not force an IDE/build tool for EXE use.

Verify GUI startup, watchlist versus fallback, exact exchange-qualified selected
symbol and model using safe nonmutating checks first. Leave All Charts unchecked:
it is visible but full multi-chart processing is not implemented in V1.
Never request private Telegram/exchange credentials or full auth/config files.
Telegram's bot_token and numeric chat_id belong only in my local
telegram_config.local.json beside the EXE/main.py, outside _internal and Git.
Preserve any existing private file. Ask before real sends, paid analysis or chart
changes. Do not grant unrestricted tools or bypass approval errors as a shortcut.

Explain the real V1 buttons/category controls using README. Troubleshoot one
failed layer at a time; do not rerun expensive analysis to test infrastructure.
Do not place orders, enable automated trading, delete existing drawings, or
promise accurate/profitable AI analysis. Distinguish verified startup from an
unperformed live test and respect the existing chart-preservation behavior.

Once installation works, ask: "Would you like to keep using the application as it
is, or customize and develop additional features?" For customization, use the
full Master Prompt above, a separate development copy/branch and focused Codex
tasks. Implementing All Charts is a future option, not an existing feature.
Begin by asking only which operating system I use.
```
