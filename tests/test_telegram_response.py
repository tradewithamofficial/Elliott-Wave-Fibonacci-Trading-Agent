"""Saved-response formatting/manual-run checks; no AI, chart or real delivery."""
import html
import importlib.util
import io
from pathlib import Path
import socket
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import telegram_sender as tg
from tests.test_telegram_sender import HtmlCheck

SYMBOL='BYBIT:XAUUSDT.P'
SWING='''**1. Bearish continuation**

- **Expected path:** Rebound into 4,161–4,187, then conditional decline to 4,065.63.
- **Fibonacci levels:** 50% at 4,160.80; 61.8% at 4,171.61; extension 3,978.51.
- **Confirmation:** A 1H close below 4,115 and a failed reclaim.
- **Negation:** Above 4,206.60 the immediate count requires revision.

**2. Consolidation**

- **Expected path:** Overlapping rally into 4,161–4,187 before a possible break.

**3. Recovery**

- **Expected path:** Reclaim 4,206.60 before recovery toward 4,313–4,325.

**Potential setups to watch**

| Direction | Trigger and zone | Setup invalidation | Reasoning / objectives |
|---|---|---|---|
| Short — preferred | Require rejection at 4,161–4,187, then break the reversal low | Above the rejection swing | Conditional 4,115 then 4,082–4,074 |

NO TRADE / WAIT until the trigger is confirmed.
'''
INTRADAY='''**1. Corrective rebound extends**

The W–X–Y structure remains tentative.

A 15m close above **4,150.47**, followed by a successful retest, favors recovery.

Below **4,131.70**, the upward-leg interpretation fails.

This fits Swing 1's corrective rebound; an intraday rally alone does not confirm the Swing reversal.

**2. Bearish continuation**

Rejection could lead to 4,119.18–4,115.

**3. Sideways correction**

Rotation within 4,131.70–4,150.47.

| 15m Scenario | Expected Move | Confirmation | Invalidation | Key Fibonacci Levels | Compatible Higher-Timeframe Scenario(s) |
|---|---|---|---|---|---|
| 1 — Rebound | 4,156–4,163 | Close above 4,150.47, then hold retest | Immediate leg below 4,131.70 | 4,156.43/64, 4,162.15 | Swing 1 corrective |
| 2 — Bearish | 4,119–4,115 | Close below 4,131.70 | Above 4,150.47 | 4,119.18 | Swing 1 |
| 3 — Sideways | 4,131.70–4,150.47 | Boundary rejection | Accepted breakout | 4,141.09 | Neutral |

**Intraday trade ideas worth monitoring**

| Setup | Entry and exact trigger | Stop / invalidation logic | Targets and illustrative R:R |
|---|---|---|---|
| Long — Scenario 1 | First require a 15m close above 4,150.47 and a retest that holds | Below the actual retest low | 4,156.43/64, 4,162.15/96 |
| Short — Scenario 2 | Require a 15m close below 4,131.70 then a failed reclaim | Above the retest high | 4,119.18–4,115 |

Neither directional setup is confirmed. Waiting is preferable to initiating either setup.
'''


def body_text(messages):
    return ''.join(html.unescape(__import__('re').sub(r'</?(?:b|i)>','',message.split('\n\n',1)[1])) for message in messages)


class ResponseFormattingTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.object(socket,'socket',side_effect=AssertionError('No network')))

    def test_complete_swing_and_intraday_content_prices_and_wait_are_retained(self):
        for scope,source in (('Swing',SWING),('Intraday',INTRADAY)):
            messages=tg.format_elliott_response(source,SYMBOL,scope)
            text=body_text(messages)
            for line in source.splitlines():
                if not line.strip() or line.startswith('|'):continue
                self.assertIn(line.replace('**','').removeprefix('- '),text)
            for line in source.splitlines():
                if line.startswith('|') and not set(line)<=set('|-: '):
                    for cell in line.strip('|').split('|'):
                        self.assertIn(cell.strip().replace('**',''),text)
            self.assertNotIn('Source excerpts',text)
            self.assertIn('NO TRADE / WAIT' if scope=='Swing' else 'Neither directional setup is confirmed',text)

    def test_headings_bullets_links_paragraphs_and_safe_bold(self):
        source='# Heading <&>\n\nFirst paragraph.\n\nSecond **bold & clear** paragraph.\n\n- Bullet 4,150.47\n- [Source](https://example.test/a?x=1&y=2)'
        messages=tg.format_elliott_response(source,SYMBOL,'Swing')
        self.assertEqual(len(messages),1);message=messages[0]
        self.assertIn('<b>Heading &lt;&amp;&gt;</b>',message)
        self.assertIn('<b>bold &amp; clear</b>',message)
        text=body_text(messages)
        for value in ('First paragraph.\n\nSecond','• Bullet 4,150.47','Source (https://example.test/a?x=1&y=2)'):
            self.assertIn(value,text)

    def test_tables_keep_every_cell_and_illustrative_examples_in_vertical_blocks(self):
        source=INTRADAY.replace('4,156.43/64, 4,162.15/96 |','4,156.43/64, 4,162.15/96. Example: entry 9,999 / stop 9,998 |')
        messages=tg.format_elliott_response(source,SYMBOL,'Intraday')
        text=body_text(messages)
        for token in ('Expected Move: 4,156–4,163','Entry and exact trigger: First require','Example: entry 9,999 / stop 9,998','Short — Scenario 2','4,141.09'):
            self.assertIn(token,text)
        self.assertNotIn('|---',text)
        ragged='| A | B |\n|---|---|\n| x | y | extra |'
        self.assertIn('| x | y | extra |',body_text(tg.format_elliott_response(ragged,SYMBOL,'Swing')))

    def test_multipart_bold_unicode_and_entities_reassemble_without_any_loss_or_twenty_part_cap(self):
        source=('**🟢 <&> 4,150.47** stable text. '*4500)+'\n\nTHE COMPLETE END.'
        messages=tg.format_elliott_response(source,SYMBOL,'Swing')
        self.assertGreater(len(messages),20)
        expected=html.unescape(__import__('re').sub(r'</?(?:b|i)>','',tg._format_complete_markdown(source)))
        self.assertEqual(body_text(messages),expected)
        for index,message in enumerate(messages,1):
            self.assertLessEqual(tg._units(message),4096);self.assertIn(f'({index}/{len(messages)})',message)
            parser=HtmlCheck();parser.feed(message);self.assertFalse(parser.stack)
        unbroken=tg.format_elliott_response('🟢&'*7000,SYMBOL,'Intraday')
        self.assertEqual(body_text(unbroken),'🟢&'*7000)

    def test_sentences_and_both_reports_remain_in_order_using_the_same_adapter(self):
        source='Swing\n\n'+SWING+'\n\nIntraday\n\n'+INTRADAY
        messages=tg.format_elliott_response(source,SYMBOL,'Both')
        report=dict(analysis_kind='simple_elliott',cli_completed=True,categories=['swing','intraday'],final_analysis=source)
        self.assertEqual(tg.format_trade_messages(report,SYMBOL,[],chart_verified=False),messages)
        text=body_text(messages);self.assertLess(text.index('Bearish continuation'),text.index('Corrective rebound extends'))
        self.assertIn('Swing\n\n',text);self.assertIn('Intraday\n\n',text)
        sentences='A complete sentence with a 4,150.47 condition. '*400
        chunks=tg._split_formatted_response(sentences,'Header')
        for chunk in chunks:
            self.assertTrue(chunk.split('\n\n',1)[1].rstrip().endswith('.'))
        with self.assertRaises(tg.TelegramError):tg.format_elliott_response(SWING,SYMBOL,'Both')

    def test_sender_sends_all_parts_sequentially_and_stops_on_failure(self):
        report=dict(analysis_kind='simple_elliott',cli_completed=True,categories=['swing'],final_analysis=SWING*12)
        expected=tg.format_trade_messages(report,SYMBOL,[],chart_verified=False)
        config=tg.TelegramConfig('123456:'+'X'*30,'12345')
        with patch.object(tg,'load_config',return_value=config),patch.object(tg,'_request',side_effect=range(1,len(expected)+1)) as request:
            result=tg.send_trade_analysis(report,SYMBOL,[],chart_verified=False,live_send_enabled=True)
        self.assertTrue(result.accepted);self.assertEqual(result.required_parts,len(expected))
        self.assertEqual([call.args[1] for call in request.call_args_list],expected)
        with patch.object(tg,'load_config',return_value=config),patch.object(tg,'_request',side_effect=[123,tg.TelegramError('Part 2 unconfirmed')]) as request:
            result=tg.send_trade_analysis(report,SYMBOL,[],chart_verified=False,live_send_enabled=True)
        self.assertFalse(result.accepted);self.assertEqual(result.accepted_parts,1)
        self.assertEqual(result.required_parts,len(expected));self.assertEqual(request.call_count,2)


class ManualScriptTests(unittest.TestCase):
    def setUp(self):
        self.root=Path(self.enterContext(tempfile.TemporaryDirectory()))
        (self.root/'tests').mkdir()
        (self.root/'responses').mkdir()
        (self.root/'responses/intraday.txt').write_text(INTRADAY,encoding='utf-8')
        (self.root/'responses/swing.txt').write_text(SWING,encoding='utf-8')
        path=Path(__file__).with_name('manual_telegram_test.py')
        spec=importlib.util.spec_from_file_location('offline_manual_test',path)
        self.manual=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.manual)
        self.manual.PROJECT_ROOT=self.root
        self.manual.RESPONSE_FILE='responses/intraday.txt';self.manual.SYMBOL=SYMBOL
        self.enterContext(patch.object(socket,'socket',side_effect=AssertionError('No network')))
        self.enterContext(patch.object(subprocess,'Popen',side_effect=AssertionError('No Codex/subprocess')))

    def test_preview_uses_production_formatter_no_sender_or_config_and_writes_exact_preview(self):
        with patch.object(self.manual,'format_elliott_response',wraps=tg.format_elliott_response) as formatter,\
             patch.object(self.manual,'send_trade_analysis') as send,patch.object(tg,'load_config') as load,\
             patch('sys.stdout',new=io.StringIO()) as output:
            self.assertEqual(self.manual.main(),0)
        formatter.assert_called_once_with(INTRADAY,SYMBOL,'Intraday');send.assert_not_called();load.assert_not_called()
        self.assertEqual((self.root/'tests/telegram_preview.txt').read_text(encoding='utf-8'),'\n\n----- NEXT TELEGRAM MESSAGE -----\n\n'.join(tg.format_elliott_response(INTRADAY,SYMBOL,'Intraday')))
        self.assertIn('SEND_TELEGRAM=False',output.getvalue())

    def test_both_relative_and_absolute_paths_use_same_production_sender_and_config(self):
        self.manual.ANALYSIS_TYPE='Both';self.manual.SWING_RESPONSE_FILE=str(self.root/'responses/swing.txt')
        self.manual.SEND_TELEGRAM=True
        with patch.object(tg,'load_config',return_value=tg.TelegramConfig('123456:'+'X'*30,'12345')) as load,\
             patch.object(tg,'_request',side_effect=range(1,100)) as request,patch('sys.stdout',new=io.StringIO()) as output:
            self.assertEqual(self.manual.main(),0)
        load.assert_called_once_with(None);self.assertGreaterEqual(request.call_count,1)
        preview=(self.root/'tests/telegram_preview.txt').read_text(encoding='utf-8')
        self.assertEqual('\n\n----- NEXT TELEGRAM MESSAGE -----\n\n'.join(call.args[1] for call in request.call_args_list),preview);self.assertIn('accepted all',output.getvalue())

    def test_missing_file_second_phase_and_missing_config_fail_without_delivery(self):
        self.manual.ANALYSIS_TYPE='Both'
        with patch.object(self.manual,'send_trade_analysis') as send,patch('sys.stdout',new=io.StringIO()):
            self.assertEqual(self.manual.main(),1);send.assert_not_called()
        self.manual.ANALYSIS_TYPE='Intraday';self.manual.SEND_TELEGRAM=True
        with patch.object(tg,'load_config',side_effect=tg.TelegramError('Missing private config')),\
             patch.object(tg,'_request') as request,patch('sys.stdout',new=io.StringIO()) as output:
            self.assertEqual(self.manual.main(),1);request.assert_not_called()
        self.assertIn('NOT complete',output.getvalue())
        self.assertTrue((self.root/'tests/telegram_preview.txt').is_file())
        self.manual.RESPONSE_FILE='missing.txt'
        with patch.object(self.manual,'send_trade_analysis') as send,patch('sys.stdout',new=io.StringIO()):
            self.assertEqual(self.manual.main(),1);send.assert_not_called()
