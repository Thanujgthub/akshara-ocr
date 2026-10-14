import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from ocr.windows_keep_awake import hold_request,owner_matches,CONTINUOUS,SYSTEM_REQUIRED


class KeepAwakeTests(unittest.TestCase):
    def owner(self):
        return SimpleNamespace(is_running=lambda:True,create_time=lambda:123.,cmdline=lambda:['python','-m','ocr.colab_runner'])

    def test_pid_reuse_and_wrong_stage_rejected_before_power_request(self):
        owner=self.owner();self.assertFalse(owner_matches(owner,124.))
        set_state=Mock(return_value=1)
        with self.assertRaises(RuntimeError):hold_request(owner,124.,set_state,Mock(),Mock())
        set_state.assert_not_called()
        owner.cmdline=lambda:['python','-m','ocr.scale_experiment']
        self.assertFalse(owner_matches(owner,123.))

    def test_request_cleared_when_controller_exits(self):
        owner=self.owner();set_state=Mock(return_value=1);record=Mock()
        def wait(seconds):
            self.assertEqual(seconds,30);owner.is_running=lambda:False
        hold_request(owner,123.,set_state,wait,record)
        self.assertEqual([c.args[0] for c in set_state.call_args_list],[CONTINUOUS|SYSTEM_REQUIRED,CONTINUOUS])
        self.assertEqual([c.args[0] for c in record.call_args_list],['active','released'])

    def test_error_still_clears_registered_request(self):
        owner=self.owner();set_state=Mock(return_value=1)
        with self.assertRaises(ValueError):hold_request(owner,123.,set_state,Mock(side_effect=ValueError('monitor failed')),Mock())
        self.assertEqual(set_state.call_args_list[-1].args,(CONTINUOUS,))
