# Installation — Elliott Wave & Fibonacci Trading Agent

Use your own accounts and existing supported Codex/TradingView setup. Never give
an assistant your bot token, authentication files or browser sessions.

## Windows package

1. Download the Windows ZIP from this repository's Releases section.
2. Extract the complete folder to a writable location, such as Documents.
3. Keep `_internal` and `reference_simple` beside the EXE.
4. Start TradingView Desktop with your working debug/CDP launcher on port 9222.
5. Verify the existing TradingView MCP connector is installed and connected.
6. Install and authenticate Codex CLI separately. Open it once so the local model
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
