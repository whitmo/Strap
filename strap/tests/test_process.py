from mock import Mock
from nose.tools import raises
from mock import patch
from path import path
import unittest
from strap.tests import pushd
import logging

class TestProcessRunner(unittest.TestCase):
    
    def _make_one(self, cmd='ls setup.py', logger=None,
                  stdout=True, stdin=None, filter_stdout=None, cwd=None,
                  raise_on_returncode=True, extra_env=None,
                  remove_from_env=None, return_output=False):
        from strap import process
        if logger is None:
            logger = self.logger = Mock()
        return process.Process(cmd, logger, stdout, stdin, filter_stdout,
                               cwd, raise_on_returncode, extra_env,
                               remove_from_env, return_output)

    def test_no_stdout_run(self):
        proc = self._make_one()
        assert proc.run() == 0

    def test_no_stdout2(self):
        proc = self._make_one(stdout=None)
        assert proc.run() == 0

    def test_no_raise(self):
        proc = self._make_one('ls --bad-option', raise_on_returncode=None)
        out = proc.run()
        assert out != 0
        assert self.logger.warn.call_args[0] == ('Command %s had error code %s', 'ls --bad-option', 1)

    def test_output_run(self):
        with pushd('strap'):
            #@@ better call sig
            proc = self._make_one('pwd', stdout=False, return_output=True)
            out = proc.run()
        assert out.endswith('strap'), out

    def test_extra_env(self):
        proc = self._make_one('pwd', stdout=False, return_output=True, extra_env=dict(THIS='is extra'))
        assert 'THIS' in proc.env

    def test_remove_env(self):
        proc = self._make_one('pwd', remove_from_env=['TERM'])
        assert not 'TERM' in proc.env

    def test_filter_logging(self):
        def tuple_filter(line):
            return (logging.WARN, line)
        
        proc = self._make_one('pwd', stdout=False, return_output=True, filter_stdout=tuple_filter)
        proc.run()

        assert isinstance(proc.logger.log.call_args[0], tuple)
        assert proc.logger.log.call_args[0][0] is logging.WARN
        def level_filter(line):
            return logging.WARN

        proc = self._make_one('pwd', stdout=False, return_output=True, filter_stdout=level_filter)
        proc.run()
        assert proc.logger.log.call_args[0][0] is logging.WARN


    @raises(OSError)
    def test_garbage_call(self):
        proc = self._make_one('something_that_doesnt_exist --canIhaz --error', stdout=False, return_output=True)
        proc.run()

    @raises(OSError)
    def test_erroring_command_call(self):
        proc = self._make_one('ls --canIhaz --error', stdout=False, return_output=True)
        proc.run()
