from functools import partial
from itertools import count
from mock import Mock
from path import path
from strap import factory
from strap import process
from strap.tests import pushd
import sys
import tempfile
import unittest


class TestStrapFile(unittest.TestCase):
    """
    Test the execution of the prod of our strap making
    """

    reqfile = path(__file__).dirname() / 'testreq.txt'
    counter = count()

    def setUp(self):
        self.logger_mock = Mock()
        self.proc = partial(process.Process, logger=self.logger_mock, return_output=True)
    
    def _makeone(self):
        self.td = td = path(tempfile.mkdtemp()).abspath()
        bundle = td / 'test_bundle-%s.pybundle' %next(self.counter)
        args = ['-r %s' %self.reqfile,
                '-n %s' %bundle]
        return factory.StrapFactory.main(args)

    def test_exec_bundle(self):
        bundle_path = self._makeone()
        dirpath = bundle_path.parent
        outvenv = dirpath / 'testvenv'
        py = self.find_non_venv_python()
        
        #proc = process.Process("python %s %s" %(bundle_path, outvenv), logger_mock, return_output=True)
        #output = proc.run()
        #import pdb;pdb.set_trace()        

    def find_non_venv_python(self):
        pythons = self.proc('which -a python', return_output=True).run().split('\n')
        
