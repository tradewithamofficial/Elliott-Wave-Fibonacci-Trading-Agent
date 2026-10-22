"""Entry CLI and Telegram integration only; all external operations mocked."""
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

import main
import sr_agent as sr
import telegram_sender as tg
from tests import test_simple_cli as cli
from tests import test_trade_setups as gui
from tests.test_grouping import TARGET


SOURCE='''**1. Primary path**

Measured reaction, pending confirmation.

- **Expected path:** Watch the measured range, not a guaranteed direction.
- **Confirmation:** Completed candle above 101 and successful retest.
- **Invalidation:** Below 95 invalidates this interpretation.

**2. Alternative**

Alternative explanation excluded from the primary excerpt.

**Potential setups to watch**

| Direction | Trigger | Invalidation | Targets |
|---|---|---|---|
| Short | Conditional rejection at 100 | Above 102 | 96 |
| Long — preferred | Close above 101 and retest | Below 99 | 105 |

NO TRADE / WAIT until the trigger is confirmed.
'''


def outcome(categories=('swing',)):
    text='\n\n'.join(c.title()+'\n\n'+SOURCE for c in categories)
    return sr.AnalysisOutcome('completed_response',return_code=0,analysis_completed=True,final_analysis=text)


class EntryCliTests(unittest.TestCase):
    def setUp(self):
        cli.SimpleCliTests.setUp(self)
        self.prompt=(Path(sr.__file__).parent/'reference_simple/EntryConditions.txt').read_text(encoding='utf-8')
        (self.reference/'EntryConditions.txt').write_text(self.prompt,encoding='utf-8')

    complete=cli.SimpleCliTests.complete

    def entry(self):
        return sr.run_simple_entry_conditions(TARGET['symbol'],'gpt-6-sol',confirmed_chart=json.dumps(TARGET),live_confirmed=True)

    def test_entry_uses_same_flags_selected_chart_model_editable_prompt_and_output_file(self):
        value=self.entry();self.assertEqual(value.status,'completed_response',value.errors)
        self.run.assert_called_once();command=self.run.call_args.args[0]
        self.assertEqual(command[:7],['codex.exe','exec','--model','gpt-6-sol','--sandbox','read-only','--skip-git-repo-check'])
        path=Path(command[-2]);self.assertEqual(path.name,'entry-conditions-response.txt');self.assertTrue(path.is_file())
        self.assertEqual(self.run.call_args.kwargs['cwd'],self.reference)
        self.assertTrue(self.run.call_args.kwargs['input'].startswith(self.prompt))
        self.assertIn(TARGET['symbol'],self.run.call_args.kwargs['input']);self.assertEqual(self.verify.call_count,2)
        self.legacy.assert_not_called();self.groups.assert_not_called()
        self.assertIn('strictly READ-ONLY',self.prompt);self.assertIn('Do not switch timeframe',self.prompt)
        self.assertIn('No Elliott Wave scenarios were found',self.prompt)
        for name in ('Swing','Intraday'):
            for rank in (1,2,3):self.assertIn(f'Elliott Wave {name} Scenario {rank}',self.prompt)

    def test_entry_missing_file_wrong_chart_and_approval_failure_stop_accurately(self):
        path=self.reference/'EntryConditions.txt';path.unlink()
        self.assertEqual(self.entry().status,'failed');self.run.assert_not_called()
        path.write_text(self.prompt,encoding='utf-8')
        self.verify.return_value=json.dumps(dict(TARGET,tab_id='OTHER'))
        self.assertEqual(self.entry().status,'failed');self.run.assert_not_called()
        self.verify.return_value=json.dumps(TARGET)
        def blocked(command,**kwargs):
            Path(command[-2]).write_text('MCP tool call requires approval, but approval policy is never',encoding='utf-8')
            return subprocess.CompletedProcess(command,0,'','')
        self.run.side_effect=blocked
        value=self.entry();self.assertEqual(value.status,'approval_blocked');self.assertFalse(value.analysis_completed)


class NotificationTests(unittest.TestCase):
    def test_complete_combined_response_preserves_levels_and_all_ideas(self):
        report=dict(analysis_kind='simple_elliott',cli_completed=True,categories=['swing','intraday'],
                    final_analysis=outcome(('swing','intraday')).final_analysis)
        messages=tg.format_trade_messages(report,TARGET['symbol'],['1D','4H','1H','15m'],chart_verified=False)
        self.assertEqual(len(messages),1);text=messages[0]
        for token in ('Trade With AM','Both','Swing','Intraday','101','95','Long — preferred','NO TRADE / WAIT'):self.assertIn(token,text)
        self.assertIn('Alternative explanation',text);self.assertLess(tg._units(text),4097)
        self.assertIn('Conditional rejection at 100',text)

    def test_plain_response_is_preserved_without_invented_fields_and_html_escaped(self):
        report=dict(analysis_kind='simple_elliott',cli_completed=True,categories=['swing'],
                    final_analysis='Swing\n\nNo structured headings. <b>unsafe & text</b> NO TRADE / WAIT.')
        text=tg.format_simple_elliott_message(report,TARGET['symbol'])[0]
        self.assertIn('No structured headings.',text);self.assertNotIn('Not clearly identified',text)
        report['final_analysis']='Swing\n\n**1. <unsafe> & path**\n\nExpected path: supported & conditional.\n\nNO TRADE / WAIT.'
        text=tg.format_simple_elliott_message(report,TARGET['symbol'])[0]
        self.assertIn('&lt;unsafe&gt; &amp;',text);self.assertNotIn('<unsafe>',text)

    def test_incomplete_failed_interrupted_or_empty_results_are_ineligible(self):
        for status in ('failed','approval_blocked','timed_out'):
            value=outcome();value.status=status;self.assertFalse(tg.simple_analysis_complete(value))
        for text in ('Analysis incomplete: data missing.','Run interrupted.','Execution could not complete.',''):
            value=outcome();value.final_analysis=text;self.assertFalse(tg.simple_analysis_complete(value))
        self.assertTrue(tg.simple_analysis_complete(outcome()))

    def test_existing_sender_loads_own_config_and_makes_one_mock_request(self):
        report=dict(analysis_kind='simple_elliott',cli_completed=True,categories=['swing'],final_analysis=outcome().final_analysis)
        config=tg.TelegramConfig('123456789:'+('A'*30),'12345')
        with patch.object(tg,'load_config',return_value=config) as load,patch.object(tg,'_request',return_value=123) as request:
            result=tg.send_trade_analysis(report,TARGET['symbol'],['1H'],chart_verified=False,live_send_enabled=True)
        self.assertTrue(result.accepted);load.assert_called_once_with(None);request.assert_called_once()

    def test_missing_private_config_never_makes_network_request(self):
        report=dict(analysis_kind='simple_elliott',cli_completed=True,categories=['swing'],final_analysis=outcome().final_analysis)
        with patch.object(tg,'load_config',side_effect=tg.TelegramError('Missing private configuration.')),patch.object(tg,'_request') as request:
            result=tg.send_trade_analysis(report,TARGET['symbol'],['1H'],chart_verified=False,live_send_enabled=True)
        self.assertFalse(result.accepted);request.assert_not_called()


class FeatureGuiTests(unittest.TestCase):
    setUp=gui.SetupGuiTests.setUp
    close=gui.SetupGuiTests.close
    pump=gui.SetupGuiTests.pump

    def test_right_ignores_modes_uses_selected_model_copy_popup_and_never_telegram(self):
        self.confirm.return_value=True;self.app.model.set('gpt-6-sol')
        self.entry_simple.return_value=sr.AnalysisOutcome('completed_response',return_code=0,analysis_completed=True,
            final_analysis='WAIT: no scenario confirmation from completed candles yet.')
        with patch.object(main,'send_trade_analysis') as send,patch.object(self.app,'show_trade_results') as popup:
            for modes in ((False,False),(True,True)):
                self.entry_simple.reset_mock();self.app.swing.set(modes[0]);self.app.intraday.set(modes[1])
                self.app.find_trade_setups();self.pump(lambda:not self.app.running)
                self.entry_simple.assert_called_once_with(TARGET['symbol'],'gpt-6-sol',confirmed_chart=json.dumps(TARGET),live_confirmed=True)
            self.assertEqual(popup.call_count,2);send.assert_not_called();self.entry_run.assert_not_called()

    def test_left_sends_once_after_both_complete_and_duplicate_result_is_not_resent(self):
        value=outcome(('swing','intraday'));self.simple_run.return_value=value
        receipt=tg.DeliveryOutcome('accepted',1,1,(123,))
        with patch.object(main,'send_trade_analysis',return_value=receipt) as send:
            values=(TARGET['symbol'],['1D','4H','1H','15m'],1,sr.DEFAULT_MODEL)
            self.app.worker(values,True,json.dumps(TARGET),True)
            self.app.worker(values,True,json.dumps(TARGET),True)
        send.assert_called_once();report=send.call_args.args[0]
        self.assertEqual(report['categories'],['swing','intraday']);self.assertIn('Intraday',report['final_analysis'])
        self.assertFalse(send.call_args.kwargs['chart_verified']);self.assertTrue(send.call_args.kwargs['live_send_enabled'])

    def test_failure_incomplete_and_explicit_disable_never_notify(self):
        with patch.object(main,'send_trade_analysis') as send:
            values=(TARGET['symbol'],['1D','4H','1H'],1,sr.DEFAULT_MODEL)
            for status in ('failed','approval_blocked'):
                value=outcome();value.status=status;self.simple_run.return_value=value
                self.app.worker(values,True,json.dumps(TARGET),True)
            value=outcome();value.final_analysis='Analysis incomplete: stopped.';self.simple_run.return_value=value
            self.app.worker(values,True,json.dumps(TARGET),True)
            self.simple_run.return_value=outcome();self.app.worker(values,True,json.dumps(TARGET),True,send_telegram=False)
        send.assert_not_called()

    def test_missing_config_reports_failure_and_keeps_analysis_copyable(self):
        self.confirm.return_value=True;self.simple_run.return_value=outcome()
        failed=tg.DeliveryOutcome('failed',error='Missing telegram_config.local.json beside main.py or the EXE.')
        with patch.object(main,'send_trade_analysis',return_value=failed),patch.object(self.app,'show_trade_results') as popup:
            self.app.find_levels();self.pump(lambda:not self.app.running)
            self.warning.assert_called_once();self.assertIn('telegram_config.local.json',self.warning.call_args.args[1])
            popup.assert_called_once();self.assertIn('unconfirmed',self.app.status.get())
