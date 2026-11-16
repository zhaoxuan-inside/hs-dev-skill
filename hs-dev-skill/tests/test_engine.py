"""Executable synthetic development scenarios, including refusal and recovery.

User sources here are explicit test fixtures, never actual user research.
"""
from datetime import datetime, timezone, timedelta
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from hsdev.engine import dispatch
from hsdev import knowledge, templates
from hsdev.store import write, read, hash_file


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        write(self.root/'rule.md','Test fixture: add(a,b) returns the sum; zero and negative operands are valid.\n')
        write(self.root/'approval.md','Test fixture authorizes this specific reversible local add repair and synchronized documents.\n')
        write(self.root/'src/add.py','def add(a,b):\n    return a-b\n')
        write(self.root/'checks.py',"import runpy\nf=runpy.run_path('src/add.py')['add']\nassert f(20,22)==42\nassert f(-2,5)==3\nprint('Two sum assertions passed')\n")
        self.cmd('init')
        self.source('rule','rule.md','user','requirement')
        self.source('approval','approval.md','user','decision')
        self.source('code-before','src/add.py','code','fact')
        self.delivery=self.cmd('start',title='Repair the addition result',activity='G1',scope='sum-repair')['delivery']

    def cmd(self, command, **args):
        if hasattr(self,'delivery'): args.setdefault('delivery',self.delivery)
        return dispatch(self.root,command,args)

    def source(self,id,path,kind='document',claim='fact',**extra):
        record={'id':id,'path':path,'kind':kind,'claim_type':claim,'scope':'sum-repair',
                'version':{'not_applicable_reason':'Synthetic test fixture identified by content digest'},
                'observed_at':(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat(),**extra}
        return knowledge.register_source(self.root,record)

    def assess(self):
        record={'understanding':'Repair subtraction used in the sum function; retain zero and negative operands.',
                'dialogue':{'mode':'reuse','summary':'Existing fixture rule already decides the required behavior; no new business choice is needed.','source_ids':['rule']},
                'unknowns':[], 'entries':[{'id':r['id'],'status':'supported','judgment':r['criterion']+' The fixture and current code identify this repair.','source_ids':['rule','code-before']}
                for r in templates.contract('G1')['minimum']]}
        return self.cmd('assess',record=record)

    def plan(self, authorize=True, checks=None):
        self.assess()
        d=self.delivery
        self.paths=['src/add.py',f'hs-dev/execution/evidence/{d}/validation.md',f'hs-dev/deliveries/{d}/handoff.md']
        record={'paths':self.paths,'steps':[{'id':'repair','action':'Replace subtraction with addition and record actual validation and bounded handoff.','paths':self.paths,'expected':'Sum assertions and synchronized output contracts are satisfied.'}],
                'verifications':checks or [{'id':'sum','argv':[sys.executable,'checks.py'],'expected':'Both sum assertions pass without mutating source or controls.'}],
                'recovery':{'strategy':'Restore only owned exact paths from the recorded preimage.','limitations':'Do not overwrite edits made after the owned change.'},
                'risks':['Only local files change; no service or external state is involved.'],
                'effects':{'external':False,'irreversible':False,'local_reversible':True},
                'feasibility':{'status':'supported','judgment':'The existing Python fixture can check both relevant operand cases.','source_ids':['rule','code-before']},
                'source_ids':['rule','code-before']}
        result=self.cmd('plan',record=record)
        if authorize: self.cmd('authorize',source='approval',plan_digest=result['plan_digest'])
        return result

    def locked(self):
        self.plan()
        self.cmd('lock')

    def output(self,spec,path,source_ids):
        return {'id':spec['id'],'scope':'sum-repair','path':path,
                'answers':[{'id':q['id'],'answer':f"{q['question']} The synthetic addition implementation now returns a+b, preserving negative operands and zero; this is a local fixture conclusion.",'status':'supported','source_ids':source_ids} for q in spec['questions']],
                'acceptance':[{'id':c['id'],'status':'supported','judgment':c['criterion']+' The fixture code and actual assertion output support this bounded result.','source_ids':source_ids} for c in spec['acceptance_checks']],
                'limitations':'This synthetic scenario checks local behavior; no external service or production claim is made.'}

    def complete_outputs(self):
        self.cmd('apply',changes={'src/add.py':'def add(a,b):\n    return a+b\n'})
        self.source('code-after','src/add.py','code')
        first=self.cmd('run')
        self.assertTrue(first['ok'],first)
        self.source('assertions',first['results'][0]['path'],'execution')
        specs=templates.contract('G1')['outputs']
        for i,spec in enumerate(specs):
            record=self.output(spec,self.paths[i],['rule','code-after','assertions'])
            if i==0:
                record.update(format='artifact',artifact_digest=hash_file(self.root/self.paths[0]))
                self.cmd('record-output',record=record)
            else: self.cmd('produce',record=record)
        return self.cmd('run')

    def test_full_cycle_native_code_evidence_submit_unlock_advance(self):
        self.locked()
        self.assertTrue(self.complete_outputs()['ok'])
        submitted=self.cmd('submit')
        self.assertFalse(submitted['lock_released'])
        self.assertFalse(submitted['task_complete'])
        self.assertTrue(submitted['next_action'])
        state=read(self.root/f'hs-dev/execution/deliveries/{self.delivery}.json')
        self.assertEqual(hash_file(self.root/state['commit']['path']),state['commit']['digest'])
        self.assertTrue(self.cmd('unlock')['lock_released'])
        self.assertEqual(self.cmd('advance',activity='G2')['activity'],'G2')
        story=(self.root/f'hs-dev/deliveries/{self.delivery}/story.md').read_text()
        self.assertIn('Repair subtraction',story)
        self.assertIn('G1.O1',story)

    def test_no_authorization_no_lock_and_no_unlock_before_submit(self):
        self.plan(authorize=False)
        with self.assertRaisesRegex(ValueError,'requires'): self.cmd('lock')
        with self.assertRaisesRegex(ValueError,'Unlock only'): self.cmd('unlock')

    def test_plan_file_drift_before_lock_is_not_silently_adopted(self):
        self.plan()
        write(self.root/self.paths[2],'Another developer wrote this handoff.')
        with self.assertRaisesRegex(ValueError,'changed after planning'): self.cmd('lock')

    def test_external_edit_is_not_overwritten_by_apply_or_rollback(self):
        self.locked()
        self.cmd('apply',changes={'src/add.py':'def add(a,b):\n    return a+b\n'})
        write(self.root/'src/add.py','another developer edit\n')
        with self.assertRaises(ValueError): self.cmd('apply',changes={'src/add.py':'overwrite'})
        with self.assertRaisesRegex(ValueError,'external edit'): self.cmd('rollback')
        self.assertEqual((self.root/'src/add.py').read_text(),'another developer edit\n')

    def test_rollback_restores_owned_files_and_allows_retry_same_activity(self):
        self.locked()
        original=(self.root/'src/add.py').read_bytes()
        self.cmd('apply',changes={'src/add.py':'def add(a,b):\n    return a+b\n'})
        self.cmd('rollback')
        self.assertEqual((self.root/'src/add.py').read_bytes(),original)
        self.cmd('unlock')
        self.assertEqual(self.cmd('advance',activity='G1')['activity'],'G1')

    def test_evidence_refresh_invalidates_assessment_even_same_bytes(self):
        self.assess()
        self.source('rule','rule.md','user','requirement',version='2.0.0')
        self.assertFalse(self.cmd('readiness')['ok'])

    def ask_fixture_question(self, **extra):
        return self.cmd('question', id='scope-question', question='Which company should provide an example?',
                        reason='An example may support a later effect evaluation.',
                        recommendation='Continue generic design without treating the example as scope.', **extra)

    def test_nonblocking_question_allows_independent_plan_but_default_blocks(self):
        self.ask_fixture_question()
        with self.assertRaisesRegex(ValueError, 'sourced answer'):
            self.plan()
        # A distinct, explicitly supplemental question does not relax the first one.
        self.cmd('question', id='sample', question='Which sample should later evaluation use?',
                 reason='Later evaluation needs a sample.', recommendation='Keep generic work independent.',
                 blocking=False, affected_work='Later effect evaluation',
                 nonblocking_reason='The local sum contract and its two assertions are already fixed.')
        with self.assertRaisesRegex(ValueError, 'sourced answer'):
            self.plan()
        self.cmd('question-resolve', record={'question_id':'scope-question', 'outcome':'invalid-premise',
                 'reason':'The synthetic user decision rejects making a company example a prerequisite.',
                 'source_ids':['approval']})
        self.assertTrue(self.plan()['plan_digest'])
        self.assertTrue(self.cmd('lock')['token'])
        story=(self.root/f'hs-dev/deliveries/{self.delivery}/story.md').read_text()
        self.assertIn('Later effect evaluation', story)
        self.assertIn('invalid-premise', story)

    def test_nonblocking_question_requires_valid_flag_and_dependency_explanation(self):
        for fields in ({'blocking':'false'}, {'blocking':False},
                       {'blocking':False,'affected_work':'Later sample evaluation'},
                       {'blocking':False,'nonblocking_reason':'Generic work is independent.'}):
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                self.ask_fixture_question(**fields)

    def test_resolution_needs_user_decision_and_current_evidence(self):
        self.ask_fixture_question()
        record={'question_id':'scope-question','outcome':'invalid-premise',
                'reason':'The fixture decision rejects this prerequisite.', 'source_ids':['approval']}
        for change in ({'source_ids':['rule']}, {'source_ids':[]}, {'reason':''},
                       {'outcome':'answered'}, {'question_id':'missing'}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.cmd('question-resolve',record={**record,**change})
        write(self.root/'decision.md','Synthetic document claims permission; it is not a user decision.')
        self.source('not-user','decision.md',claim='decision')
        with self.assertRaisesRegex(ValueError,'user decision'):
            self.cmd('question-resolve',record={**record,'source_ids':['not-user']})
        self.cmd('question-resolve',record=record)
        self.assertTrue(self.assess()['ok'])
        write(self.root/'approval.md','Synthetic changed decision requires the example after all.')
        self.assertFalse(self.cmd('readiness')['ok'])

    def test_answer_reopens_resolved_question_and_preserves_original(self):
        self.ask_fixture_question()
        self.cmd('question-resolve',record={'question_id':'scope-question','outcome':'withdrawn',
                 'reason':'The synthetic user withdraws this request.', 'source_ids':['approval']})
        self.cmd('answer',question_id='scope-question',source='rule',
                 understanding='The fixture rule is now offered as an actual answer.')
        self.assertFalse(self.cmd('readiness')['ok'])
        state=read(self.root/f'hs-dev/execution/deliveries/{self.delivery}.json')
        q=state['questions']['scope-question']
        self.assertNotIn('resolution',q)
        self.assertEqual(q['question'],'Which company should provide an example?')

    def test_supplemental_question_does_not_invent_answered_dialogue(self):
        self.ask_fixture_question(blocking=False, affected_work='Later example evaluation',
                                  nonblocking_reason='Current fixture contract is already decided.')
        self.assess()
        state=read(self.root/f'hs-dev/execution/deliveries/{self.delivery}.json')
        record=state['assessment']['record']
        record['dialogue']['mode']='asked'
        with self.assertRaisesRegex(ValueError,'actual current answered'):
            self.cmd('assess',record=record)

    def test_prior_supplemental_question_is_reassessed_at_next_activity(self):
        self.ask_fixture_question(blocking=False, affected_work='G2 evaluation sample',
                                  nonblocking_reason='G1 sum repair has an existing fixture.')
        self.locked()
        self.complete_outputs()
        self.cmd('submit'); self.cmd('unlock')
        moved=self.cmd('advance',activity='G2')
        self.assertEqual([q['id'] for q in moved['prior_questions']],['scope-question'])
        self.assertEqual(self.cmd('resume')['prior_questions'],moved['prior_questions'])
        record={'understanding':'Evaluate the repaired sum against the actual fixture.',
                'dialogue':{'mode':'reuse','summary':'The fixture rule remains the accepted contract.','source_ids':['rule']},
                'unknowns':[], 'entries':[{'id':r['id'],'status':'supported',
                    'judgment':'The fixture specifies inputs and observable sums for this check.', 'source_ids':['rule']}
                    for r in templates.contract('G2')['minimum']]}
        with self.assertRaisesRegex(ValueError,'every prior unanswered'):
            self.cmd('assess',record=record)
        record['prior_questions']=[{'id':'scope-question','blocks':True,
            'reason':'This evaluation was declared dependent on selecting a sample.',
            'next_action':'Obtain a user decision or choose an independently justified evaluation scope.'}]
        self.assertFalse(self.cmd('assess',record=record)['ok'])
        record['prior_questions'][0].update(blocks=False,
            reason='The sum assertions already cover this activity; company examples are unrelated.')
        self.assertTrue(self.cmd('assess',record=record)['ok'])
        self.cmd('question-resolve',record={'question_id':'scope-question','outcome':'invalid-premise',
            'reason':'The synthetic user rejects making company examples a sum prerequisite.',
            'source_ids':['approval']})
        self.assertEqual(self.cmd('resume')['prior_questions'],[])
        record.pop('prior_questions')
        self.assertTrue(self.cmd('assess',record=record)['ok'])

    def test_prior_independent_question_allows_authorized_lock(self):
        self.ask_fixture_question(blocking=False, affected_work='Later company evaluation',
                                  nonblocking_reason='The fixture sum repair is independent.')
        self.locked()
        self.complete_outputs()
        prior_plan=copy.deepcopy(read(self.root/f'hs-dev/execution/deliveries/{self.delivery}.json')['plan']['record'])
        self.cmd('submit'); self.cmd('unlock'); self.cmd('advance',activity='G2')
        self.cmd('assess',record={'understanding':'Check the actual repaired sum using its fixed fixture.',
            'dialogue':{'mode':'reuse','summary':'The fixture determines all expected sums.','source_ids':['rule']},
            'unknowns':[], 'entries':[{'id':r['id'],'status':'supported',
                'judgment':'The actual fixture supplies this check condition.','source_ids':['rule']}
                for r in templates.contract('G2')['minimum']],
            'prior_questions':[{'id':'scope-question','blocks':False,
                'reason':'Company examples are unrelated to these sum checks.',
                'next_action':'Keep the example question visible for later applicable evaluation.'}]})
        prior_plan['source_ids']=['rule']
        prior_plan['feasibility']['source_ids']=['rule']
        planned=self.cmd('plan',record=prior_plan)
        self.cmd('authorize',source='approval',plan_digest=planned['plan_digest'])
        self.assertTrue(self.cmd('lock')['token'])

    def test_legacy_question_without_new_fields_still_blocks(self):
        self.ask_fixture_question()
        file=self.root/f'hs-dev/execution/deliveries/{self.delivery}.json'
        legacy=read(file)
        for key in ('blocking','affected_work','nonblocking_reason'):
            legacy['questions']['scope-question'].pop(key)
        write(file,legacy)  # Explicitly simulate a pre-extension fixture, not a live migration.
        with self.assertRaisesRegex(ValueError,'sourced answer'):
            self.plan()

    def test_unanswered_question_and_reopened_reflection_block_planning(self):
        self.cmd('question',id='Q1',question='Should negative operands remain valid?',reason='Rejecting them would change existing accepted behavior.',recommendation='Keep negative operands because the fixture rule explicitly includes them.')
        with self.assertRaises(ValueError): self.assess()
        self.cmd('answer',question_id='Q1',source='rule',understanding='Negative operands remain valid in the sum repair.')
        self.cmd('reflect',question_id='Q1',source='rule',scenario='add(-2,5) should equal 3 rather than reject the request.',outcome='reopen',reason='The current implementation contradicts this case.')
        with self.assertRaises(ValueError): self.assess()
        self.cmd('reflect',question_id='Q1',source='rule',scenario='The repaired addition expression handles negative operands.',outcome='supported',reason='The rule requires this behavior and the planned assertion checks it.')
        self.assertTrue(self.assess()['ok'])

    def test_failed_check_and_source_mutating_check_cannot_submit(self):
        self.locked()
        self.assertFalse(self.cmd('run')['ok'])
        with self.assertRaises(ValueError): self.cmd('submit')
        self.cmd('rollback');self.cmd('unlock');self.cmd('advance',activity='G1')
        checks=[{'id':'mutate','argv':[sys.executable,'-c',"from pathlib import Path; Path('other.txt').write_text('mutation')"],'expected':'A mutating checker must be detected as failed verification.'}]
        self.plan(checks=checks);self.cmd('lock')
        self.assertFalse(self.cmd('run')['ok'])

    def test_outputs_changed_after_run_require_current_verification(self):
        self.locked();self.complete_outputs()
        self.cmd('apply',changes={'src/add.py':'def add(a,b):\n    return a+b+1\n'})
        with self.assertRaises(ValueError):self.cmd('submit')

    def test_post_submit_external_change_preserved_when_unlocking(self):
        self.locked();self.complete_outputs();self.cmd('submit')
        write(self.root/'src/add.py','new change after consistent submit\n')
        result=self.cmd('unlock')
        self.assertTrue(result['post_submit_drift'])
        self.assertEqual((self.root/'src/add.py').read_text(),'new change after consistent submit\n')

    def test_interrupted_apply_reconciles_without_undoing_owned_write(self):
        self.locked()
        from hsdev import engine
        real_write=engine.write
        fired=[False]
        def interrupted(file,value):
            real_write(file,value)
            if Path(file)==self.root/'src/add.py' and not fired[0]:
                fired[0]=True
                raise OSError('synthetic interruption after source write')
        with patch.object(engine,'write',interrupted):
            with self.assertRaises(OSError):self.cmd('apply',changes={'src/add.py':'def add(a,b):\n    return a+b\n'})
        self.assertTrue(self.cmd('resume')['ok'])
        self.cmd('rollback')
        self.assertIn('a-b',(self.root/'src/add.py').read_text())

    def test_changed_input_is_not_accepted_as_current_output_evidence(self):
        self.locked()
        self.cmd('apply',changes={'src/add.py':'def add(a,b):\n    return a+b\n'})
        spec=templates.contract('G1')['outputs'][0]
        record=self.output(spec,'src/add.py',['code-before'])
        record.update(format='artifact',artifact_digest=hash_file(self.root/'src/add.py'))
        with self.assertRaisesRegex(ValueError,'baseline'): self.cmd('record-output',record=record)

    def test_outside_scope_write_and_noncanonical_alias_are_refused(self):
        self.locked()
        with self.assertRaises(ValueError):self.cmd('apply',changes={'outside.py':'escaped'})
        with self.assertRaises(ValueError):self.cmd('apply',changes={'src/./add.py':'aliased'})
        self.assertFalse((self.root/'outside.py').exists())

    def test_explicit_preserve_resolves_rollback_without_overwriting_external_edit(self):
        self.locked()
        self.cmd('apply',changes={'src/add.py':'owned change'})
        write(self.root/'src/add.py','later external edit')
        self.cmd('rollback',record={'preserve':['src/add.py'],'reason':'Preserve the later collaborator edit; relinquish our local modification.','source_ids':['approval']})
        self.cmd('unlock')
        self.assertEqual((self.root/'src/add.py').read_text(),'later external edit')

    def test_interrupted_lock_acquisition_and_unlock_are_recoverable(self):
        self.plan()
        from hsdev import engine
        real_save=engine._save
        fired=[False]
        def interrupted(root,state):
            real_save(root,state)
            if state['status']=='locking' and not fired[0]:
                fired[0]=True
                raise OSError('synthetic lock acquisition interruption')
        with patch.object(engine,'_save',interrupted):
            with self.assertRaises(OSError): self.cmd('lock')
        self.assertEqual(self.cmd('resume')['status'],'locked')
        self.cmd('rollback')
        real_write=engine.write
        fired=[False]
        def interrupted_unlock(file,value):
            real_write(file,value)
            if Path(file)==self.root/'hs-dev/execution/workspace.json' and value.get('lock') is None and not fired[0]:
                fired[0]=True
                raise OSError('synthetic interruption after lock release')
        with patch.object(engine,'write',interrupted_unlock):
            with self.assertRaises(OSError): self.cmd('unlock')
        self.assertTrue(self.cmd('unlock')['lock_released'])

    def test_interrupted_rollback_continues_from_write_ahead_record(self):
        self.locked()
        self.cmd('apply',changes={'src/add.py':'owned change'})
        from hsdev import engine
        real_write=engine.write
        fired=[False]
        def interrupted(file,value):
            real_write(file,value)
            if Path(file)==self.root/'src/add.py' and not fired[0]:
                fired[0]=True
                raise OSError('synthetic rollback interruption')
        with patch.object(engine,'write',interrupted):
            with self.assertRaises(OSError): self.cmd('rollback')
        self.assertEqual(self.cmd('rollback')['status'],'rolled-back')
        self.cmd('unlock')
        self.assertIn('a-b',(self.root/'src/add.py').read_text())

    def test_bounded_policy_reuses_existing_authority_but_high_risk_does_not(self):
        import shutil
        shutil.rmtree(self.root/'hs-dev')
        policy={'mode':'bounded','allow':['src','hs-dev/deliveries','hs-dev/execution/evidence'],
                'source':{'path':'approval.md','digest':hash_file(self.root/'approval.md')}}
        self.cmd('init',record={'policy':policy})
        self.source('rule','rule.md','user','requirement')
        self.source('approval','approval.md','user','decision')
        self.source('code-before','src/add.py','code')
        self.delivery=self.cmd('start',title='Use existing bounded authority',activity='G1',scope='sum-repair')['delivery']
        self.plan(authorize=False)
        self.assertTrue(self.cmd('lock')['ok'])
        self.cmd('rollback');self.cmd('unlock');self.cmd('advance',activity='G1')
        self.plan(authorize=False)
        state=read(self.root/f'hs-dev/execution/deliveries/{self.delivery}.json')
        new=copy.deepcopy(state['plan']['record'])
        new['effects']['external']=True
        self.cmd('plan',record=new)
        with self.assertRaisesRegex(ValueError,'requires'):self.cmd('lock')

    def test_verification_output_has_a_hard_bound_and_cannot_pass_overflow(self):
        checks=[{'id':'flood','argv':[sys.executable,'-c',"import sys; sys.stdout.write('x'*5000000)"],'expected':'Output over the declared log budget must be a failed check.'}]
        self.plan(checks=checks);self.cmd('lock')
        result=self.cmd('run')
        self.assertFalse(result['ok'])
        self.assertEqual(result['results'][0]['exit_code'],125)
        self.assertLessEqual((self.root/result['results'][0]['path']).stat().st_size,4000000)

    def test_control_mutating_check_cannot_replace_a_previous_success(self):
        checks=[{'id':'control','argv':[sys.executable,'-c',"from pathlib import Path; Path('hs-dev/execution/workspace.json').write_text('{}')"],'expected':'Changes to execution control must be detected rather than accepted.'}]
        self.plan(checks=checks);self.cmd('lock')
        with self.assertRaisesRegex(ValueError,'controls'):self.cmd('run')
        state=read(self.root/f'hs-dev/execution/deliveries/{self.delivery}.json')
        self.assertIsNone(state['verification'])

    def test_full_cycle_through_actual_json_cli(self):
        import subprocess
        cli=Path(__file__).resolve().parents[1]/'scripts/hs-dev.py'
        def invoke(command,**args):
            arguments=[sys.executable,str(cli),'--root',str(self.root),command]
            if command not in {'init','start','status','source-add','reindex'}:
                arguments.append(self.delivery)
            for key,value in args.items():
                if key=='delivery':continue
                arguments.extend(['--'+key.replace('_','-'),json.dumps(value,ensure_ascii=False) if isinstance(value,(dict,list)) else str(value)])
            result=subprocess.run(arguments,capture_output=True,text=True,timeout=20)
            self.assertEqual(result.returncode,0,result.stderr)
            return json.loads(result.stdout)['result']
        self.cmd=invoke
        self.locked()
        self.assertTrue(self.complete_outputs()['ok'])
        self.assertEqual(self.cmd('submit')['status'],'submitted')
        self.assertTrue(self.cmd('unlock')['lock_released'])


if __name__=='__main__':unittest.main()
