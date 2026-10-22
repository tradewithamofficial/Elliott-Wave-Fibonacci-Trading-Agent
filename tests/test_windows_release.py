"""Windows packaging smoke checks. No model analysis or delivery; startup reads only."""
from contextlib import ExitStack
import hashlib
import json
import marshal
from pathlib import Path
import sys
import time
import types
import unittest
from unittest.mock import patch

PROJECT=Path(__file__).resolve().parents[1]
RELEASE=PROJECT/'release/ElliottWaveFibonacciTradingAgent'
EXE=RELEASE/'ElliottWaveFibonacciTradingAgent.exe'


@unittest.skipUnless(EXE.is_file(),'Build the Windows package first')
class WindowsReleaseTests(unittest.TestCase):
    def test_package_resources_version_and_editable_prompts(self):
        import pefile
        self.assertEqual(json.loads((RELEASE/'telegram_config.example.json').read_text()),{'bot_token':'','chat_id':''})
        self.assertFalse((RELEASE/'telegram_config.local.json').exists())
        for name in ('swing.txt','Intraday.txt','EntryConditions.txt'):
            self.assertEqual((RELEASE/'reference_simple'/name).read_bytes(),(PROJECT/'reference_simple'/name).read_bytes())
        for name in ('TradeWithAM_Robot.ico','Futuristic AI Robot with Breakout Chart.png'):
            self.assertEqual((RELEASE/'_internal/assets'/name).read_bytes(),(PROJECT/'assets'/name).read_bytes())
        pe=pefile.PE(str(EXE))
        try:
            self.assertEqual(pe.FILE_HEADER.Machine,0x8664)
            self.assertEqual(pe.OPTIONAL_HEADER.Subsystem,2)
            self.assertEqual((pe.VS_FIXEDFILEINFO[0].FileVersionMS,pe.VS_FIXEDFILEINFO[0].FileVersionLS),(0x10000,0))
        finally:pe.close()

    def test_bundled_gui_controls_and_readonly_discovery(self):
        from PyInstaller.archive.readers import CArchiveReader
        archive=CArchiveReader(str(EXE));pyz=archive.open_embedded_archive('PYZ.pyz')
        with ExitStack() as stack:
            modules={name:types.ModuleType(name) for name in ('sr_grouping','sr_agent','telegram_sender','ui_dialogs')}
            stack.enter_context(patch.dict(sys.modules,modules))
            stack.enter_context(patch.object(sys,'frozen',True,create=True))
            stack.enter_context(patch.object(sys,'executable',str(EXE)))
            for name,module in modules.items():
                module.__file__=str(RELEASE/'_internal'/f'{name}.py')
                exec(pyz.extract(name),module.__dict__)
            gui=types.ModuleType('bundled_gui_smoke');gui.__file__=str(RELEASE/'_internal/main.py')
            exec(marshal.loads(archive.extract('main')),gui.__dict__)
            # Existing startup readers only: no chart setter or paid Codex exec.
            catalog=modules['sr_agent'].load_codex_models()
            watchlist=modules['sr_agent'].get_tradingview_watchlist()
            self.assertTrue(catalog['models']);self.assertTrue(watchlist['symbols'])
            stack.enter_context(patch.object(gui,'load_codex_models',return_value=catalog))
            stack.enter_context(patch.object(gui,'get_tradingview_watchlist',return_value=watchlist))
            analysis=stack.enter_context(patch.object(gui,'run_simple_elliott_analysis',side_effect=AssertionError('No analysis')))
            entry=stack.enter_context(patch.object(gui,'run_simple_entry_conditions',side_effect=AssertionError('No entry analysis')))
            sender=stack.enter_context(patch.object(gui,'send_trade_analysis',side_effect=AssertionError('No send')))
            root=gui.ctk.CTk();root.withdraw()
            try:
                app=gui.SupportResistanceApp(root)
                deadline=time.monotonic()+5
                while time.monotonic()<deadline:
                    root.update()
                    if app.model.get() and not app.refreshing:break
                    time.sleep(.01)
                self.assertEqual(root.title(),'Trade With AM — Elliott Wave & Fibonacci Trading Agent')
                self.assertIsNotNone(app.agent_image)
                self.assertTrue(app.swing.get());self.assertFalse(app.intraday.get())
                app.intraday_box.toggle();self.assertTrue(app.intraday.get())
                app.swing_box.toggle();self.assertFalse(app.swing.get())
                app.swing_box.toggle();app.intraday_box.toggle()
                self.assertEqual(app.find_button.cget('text'),'Elliott Wave & Fibonacci Analysis')
                self.assertEqual(app.trade_button.cget('text'),'Check Entry Conditions')
                self.assertEqual(app.model_box.cget('values'),catalog['models'])
                self.assertEqual(app.symbol_box.cget('values'),watchlist['symbols'])
                self.assertEqual(modules['sr_agent'].PROJECT_DIR,RELEASE)
                self.assertEqual(modules['telegram_sender'].local_config_path(),RELEASE/'telegram_config.local.json')
                analysis.assert_not_called();entry.assert_not_called();sender.assert_not_called()
                print(f"Bundled selectors: {len(catalog['models'])} models; {len(watchlist['symbols'])} symbols; watchlist source={watchlist['source']}.")
            finally:
                for callback in root.tk.call('after','info'):root.tk.call('after','cancel',callback)
                root.destroy()
