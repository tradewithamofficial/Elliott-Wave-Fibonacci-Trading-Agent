"""Focused offline checks of the supplied script's CLI/text-response approach."""
import json
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import ANY,patch

import main
import sr_agent as sr
from tests.test_grouping import TARGET
from tests.test_trade_setups import SetupGuiTests


class SimpleCliTests(unittest.TestCase):
    def setUp(self):
        self.folder=Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.reference=self.folder/'reference_simple';self.reference.mkdir()
        for name,text in (('swing.txt','EDITABLE SWING PROMPT'),('Intraday.txt','EDITABLE INTRADAY PROMPT')):
            (self.reference/name).write_text(text,encoding='utf-8')
        self.enterContext(patch.object(sr,'PROJECT_DIR',self.folder))
        self.verify=self.enterContext(patch.object(sr,'verify_tradingview_chart',return_value=json.dumps(TARGET)))
        self.enterContext(patch.object(sr,'codex_command',return_value=['codex.exe']))
        self.enterContext(patch.object(sr,'node_executable',return_value=None))
        self.legacy=self.enterContext(patch.object(sr,'_execute_codex',side_effect=AssertionError('Legacy executor must be bypassed')))
        self.groups=self.enterContext(patch.object(sr,'TradeSetupSession',side_effect=AssertionError('No grouping/parser session')))
        self.run=self.enterContext(patch.object(sr.subprocess,'run',side_effect=self.complete))

    def complete(self,command,**kwargs):
        out=Path(command[command.index('--output-last-message')+1])
        out.write_text('Plain analytical scenario. NO TRADE / WAIT. No structured drawing records.',encoding='utf-8')
        return subprocess.CompletedProcess(command,0,'Offline Codex output','')

    def analyze(self,categories,**kwargs):
        return sr.run_simple_elliott_analysis(TARGET['symbol'],categories,'gpt-6-sol',
            confirmed_chart=json.dumps(TARGET),live_confirmed=True,**kwargs)

    def test_both_matches_reference_command_model_cwd_stdin_and_separate_responses(self):
        phases=[];out=self.analyze(['intraday','swing'],on_phase=phases.append)
        self.assertEqual(out.status,'completed_response',out.errors)
        self.assertEqual(phases,['swing','intraday']);self.assertEqual(self.run.call_count,2)
        paths=[]
        for call,category in zip(self.run.call_args_list,phases):
            command=call.args[0];path=Path(command[-2]);paths.append(path)
            self.assertEqual(command,['codex.exe','exec','--model','gpt-6-sol','--sandbox','read-only',
                '--skip-git-repo-check','--output-last-message',str(path),'-'])
            self.assertEqual(call.kwargs['cwd'],self.reference)
            self.assertEqual(call.kwargs['encoding'],'utf-8');self.assertFalse(call.kwargs['shell'])
            self.assertIn('EDITABLE '+category.upper()+' PROMPT',call.kwargs['input'])
            self.assertIn(TARGET['tab_id'],call.kwargs['input']);self.assertIn(TARGET['symbol'],call.kwargs['input'])
            self.assertIn('do not delete, replace',call.kwargs['input'])
            self.assertIn('not a JSON completion contract',call.kwargs['input'])
            self.assertNotIn('APPLICATION COMPLETION PROTOCOL',call.kwargs['input'])
            self.assertIn(str(path),out.output);self.assertTrue(path.read_text(encoding='utf-8').startswith('Plain analytical'))
        self.assertNotEqual(paths[0],paths[1]);self.assertIn('Swing',out.final_analysis);self.assertIn('Intraday',out.final_analysis)
        self.assertFalse(out.drawings_verified);self.groups.assert_not_called();self.legacy.assert_not_called()

    def test_single_modes_read_latest_file_and_intraday_preserves_swing_context(self):
        for category in ('swing','intraday'):
            self.run.reset_mock();name='swing.txt' if category=='swing' else 'Intraday.txt'
            (self.reference/name).write_text('LATEST USER EDIT '+category,encoding='utf-8')
            self.assertEqual(self.analyze([category]).status,'completed_response')
            self.run.assert_called_once();prompt=self.run.call_args.kwargs['input']
            self.assertIn('LATEST USER EDIT '+category,prompt)
            if category=='intraday':
                self.assertIn('Preserve all Swing',prompt);self.assertIn('do not assume three exist',prompt)
                self.assertIn('Elliott Wave Intraday Scenario 3',prompt)

    def test_neither_or_unapproved_never_runs_cli(self):
        self.assertEqual(self.analyze([]).status,'failed')
        out=sr.run_simple_elliott_analysis(TARGET['symbol'],['swing'])
        self.assertEqual(out.status,'confirmation_required');self.run.assert_not_called()

    def test_missing_or_empty_second_prompt_stops_before_any_analysis(self):
        for missing in (False,True):
            p=self.reference/'Intraday.txt';p.write_text('',encoding='utf-8')
            if missing:p.unlink()
            self.assertEqual(self.analyze(['swing','intraday']).status,'failed')
            self.run.assert_not_called()

    def test_chart_mismatch_before_or_after_first_execution_stops_next(self):
        other=json.dumps(dict(TARGET,tab_id='OTHER'))
        self.verify.return_value=other
        self.assertEqual(self.analyze(['swing','intraday']).status,'failed');self.run.assert_not_called()
        self.verify.side_effect=[json.dumps(TARGET),other]
        out=self.analyze(['swing','intraday'])
        self.assertEqual(out.status,'failed');self.run.assert_called_once();self.assertIn('Swing',out.final_analysis)

    def test_failed_process_empty_response_and_infrastructure_failure_stop_without_retry(self):
        for mode in ('exit','empty','infrastructure'):
            self.run.reset_mock()
            def fail(command,**kwargs):
                if mode=='infrastructure':
                    Path(command[-2]).write_text('FAILURE: unsupported call: tool_searchtool_search_tool',encoding='utf-8')
                return subprocess.CompletedProcess(command,1 if mode=='exit' else 0,'','Offline execution failure' if mode=='exit' else '')
            self.run.side_effect=fail
            out=self.analyze(['swing','intraday'])
            self.assertEqual(out.status,'failed');self.assertFalse(out.analysis_completed);self.run.assert_called_once()

    def test_swing_response_survives_intraday_failure(self):
        attempts=[]
        def second_fails(command,**kwargs):
            attempts.append(command)
            if len(attempts)==1:return self.complete(command,**kwargs)
            return subprocess.CompletedProcess(command,2,'','Offline Intraday failure')
        self.run.side_effect=second_fails
        out=self.analyze(['swing','intraday'])
        self.assertEqual(out.status,'failed');self.assertEqual(len(attempts),2)
        self.assertTrue(Path(attempts[0][-2]).is_file());self.assertIn('Swing',out.final_analysis)

    def test_model_does_not_repeat_app_pane_inspection_and_exact_app_checks_remain(self):
        out=self.analyze(['swing','intraday'])
        self.assertEqual(out.status,'completed_response')
        self.assertEqual(self.verify.call_count,4)
        for call in self.run.call_args_list:
            text=call.kwargs['input']
            self.assertIn('application has already independently verified',text)
            self.assertIn('Do not call pane_list',text)
            self.assertIn('or repeat the application\'s layout/pane inspection through another tool',text)
            self.assertIn('chart_get_state and tab_list',text)
            self.assertIn('never work around a permission denial',text)
            self.assertNotIn('Verify this exact target before drawing',text)
            self.assertNotIn('-c',call.args[0]);self.assertNotIn('--dangerously-bypass-approvals-and-sandbox',call.args[0])

    def test_zero_exit_approval_rejection_in_response_or_stdout_stops_intraday(self):
        for location in ('response','stdout'):
            self.run.reset_mock()
            message=('Automatic approval review rejected the MCP pane-inspection action because approval policy is never.'
                     if location=='response' else 'MCP tool call requires approval, but approval policy is never')
            def deny(command,**kwargs):
                Path(command[-2]).write_text(message if location=='response' else 'Analysis only; no drawings.',encoding='utf-8')
                return subprocess.CompletedProcess(command,0,message if location=='stdout' else '','')
            self.run.side_effect=deny
            out=self.analyze(['swing','intraday'])
            self.assertEqual(out.status,'approval_blocked');self.assertFalse(out.analysis_completed)
            self.assertFalse(out.drawings_verified);self.run.assert_called_once()
            self.assertIn('No permission was bypassed or changed',out.errors)


class SimpleGuiTests(unittest.TestCase):
    setUp=SetupGuiTests.setUp
    close=SetupGuiTests.close
    pump=SetupGuiTests.pump

    def test_both_single_modes_model_popup_and_telegram_delivery(self):
        self.confirm.return_value=True
        self.app.model.set('gpt-6-sol')
        self.simple_run.return_value=sr.AnalysisOutcome('completed_response',return_code=0,analysis_completed=True,final_analysis='Plain text analysis, no special schema.')
        with patch.object(main,'send_trade_analysis',return_value=main.DeliveryOutcome('accepted',1,1,(123,))) as send,patch.object(self.app,'show_trade_results') as popup:
            for swing,intraday,categories in ((True,False,['swing']),(False,True,['intraday']),(True,True,['swing','intraday'])):
                self.simple_run.reset_mock();popup.reset_mock();self.simple_run.return_value.trade_report=None
                self.app.swing.set(swing);self.app.intraday.set(intraday)
                self.app.find_button.invoke();self.pump(lambda:not self.app.running)
                self.simple_run.assert_called_once_with(TARGET['symbol'],categories,'gpt-6-sol',
                    confirmed_chart=json.dumps(TARGET),live_confirmed=True,on_phase=ANY)
                popup.assert_called_once_with(self.simple_run.return_value.final_analysis,title='Elliott Wave & Fibonacci — Analysis Results')
            self.ew_run.assert_not_called();self.run.assert_not_called();self.assertEqual(send.call_count,3)
        self.assertIn('response ready',self.app.status.get());self.assertEqual(len(self.app.telegram_attempted),3)

    def test_neither_blocks_left_and_does_not_change_right(self):
        self.app.swing.set(False);self.app.intraday.set(False)
        self.app.find_levels();self.error.assert_called_once();self.simple_run.assert_not_called()
        self.confirm.return_value=True
        self.app.find_trade_setups();self.pump(lambda:not self.app.running)
        self.entry_simple.assert_called_once();self.simple_run.assert_not_called()

    def test_existing_background_worker_keeps_tk_responsive_and_failure_shows_partial_response(self):
        entered,release=threading.Event(),threading.Event();self.addCleanup(release.set)
        self.confirm.return_value=True;threads=[]
        def slow(*args,**kwargs):
            threads.append(threading.get_ident());entered.set();release.wait(3)
            return sr.AnalysisOutcome('failed',errors='Offline Intraday failure; stopped.',final_analysis='Swing response retained.')
        self.simple_run.side_effect=slow
        with patch.object(main,'send_trade_analysis') as send,patch.object(self.app,'show_trade_results') as popup:
            self.app.find_levels();self.pump(entered.is_set)
            ticks=[];self.root.after(1,lambda:ticks.append(True));self.pump(lambda:bool(ticks))
            self.assertNotEqual(threads[0],threading.get_ident());self.assertTrue(self.app.running)
            self.app.find_levels();self.simple_run.assert_called_once()
            release.set();self.pump(lambda:not self.app.running)
            self.warning.assert_called_once();self.success.assert_not_called()
            popup.assert_called_once_with('Swing response retained.',title='Elliott Wave & Fibonacci — Analysis Results')
            send.assert_not_called()
