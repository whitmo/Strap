from itertools import count
from mock import patch
from path import path
import commands
import inspect
import os
import sys
import tempfile
import unittest
import zipfile


class TestResolveExtraText(unittest.TestCase):
    @staticmethod
    def assert_functions_in_text(txt):
        co = compile(txt, 'default_bootstrap', mode='exec')
        basefuncs = set(('extend_parser', 'adjust_options', 'after_install'))
        assert basefuncs.issubset(set(co.co_names)), "Names not found in set: %s" %list(co.co_names)

    def get_assert_text(self, func, spec):
        mod_text = func(spec)
        assert mod_text, "No text returned"
        return mod_text

    def test_resolve_zopestyle_module_spec(self):
        from strap import resolve_extra_text
        mod_text = self.get_assert_text(resolve_extra_text, 'strap.default_bootstrap')
        self.assert_functions_in_text(mod_text)

    def test_resolve_filename(self):
        from strap import resolve_extra_text
        ex = path(__file__).dirname() / 'example_extratext.py'
        mod_text = self.get_assert_text(resolve_extra_text, ex.abspath())
        self.assert_functions_in_text(mod_text)


class TestStrapFactory(unittest.TestCase):
    """
    Test the main class
    """
    counter = count()
    reqfile = path(__file__).dirname() / 'testreq.txt'
    
    def _makeone(self, et='print "Wheeeeeeee"', packages='', bundle=None, reqfile=[reqfile]):
        from strap.factory import StrapFactory
        if bundle is None:
            td = path(tempfile.mkdtemp())
            bundle = td / 'test_bundle-%s.pybundle' %next(self.counter)
        return StrapFactory(et, packages, reqfile, bundle)

    @patch('argparse.ArgumentParser.add_argument')
    @patch('argparse.ArgumentParser.parse_args')
    def test_argparser(self, parse_mock, add_mock):
        factory = self._makeone()
        blah = factory.argparser()
        assert blah
        assert parse_mock.call_args_list == [((), {})]
        assert set(x[0][0] for x in add_mock.call_args_list) == set(['-h', 'packages', '-n', '-r', '-m']), set(x[0][0] for x in add_mock.call_args_list)

    def test_init(self):
        factory = self._makeone('','','')
        assert factory

    @patch('sys.exit')
    def test_createbundle_fail_no_req(self, exit_mock):
        factory = self._makeone(reqfile=['idonotexist'])
        factory.create_bundle()
        exit_mock.assert_called_once_with(1)

    def test_createbundle(self):
        factory = self._makeone()
        rp = factory.create_bundle()
        assert rp.exists(), "%s does not exist." %rp 
        assert rp == factory.bundle_name, "%s != %s" %(rp, factory.bundle_name)

    def test_append_main(self):
        factory = self._makeone()
        rp = factory.create_bundle()
        factory.append_to_zip(rp)
        with zipfile.ZipFile(rp, mode='r') as bundle:
            files = [x.filename for x in reversed(bundle.infolist())]
            #@@ import factory and reference class var
            assert ['bootstrap.py', 'extender.py', '__main__.py', 'path.py'] == files[:4], "Actual filelist: %s" %files[:3]

    def test_bundle_has_bootstrap(self):
        from strap import default_bootstrap
        factory = self._makeone(et=inspect.getsource(default_bootstrap))
        bundle_path = factory.run()
        sys.path.insert(0, str(bundle_path))
        import bootstrap
        for func in ('extend_parser', 'adjust_options', 'after_install'):
            assert hasattr(bootstrap, func), "No function %s in %s: %s" %(func, bootstrap, dir(bootstrap))
        del sys.path[0]

    def test_bundle_exec(self):
        env = os.environ['VIRTUAL_ENV']
        from strap import default_bootstrap
        factory = self._makeone(et=inspect.getsource(default_bootstrap))
        filename = factory.run()

        (stat, out) = commands.getstatusoutput('%s/bin/python %s' %(env, filename))
        assert out.find('Successfully installed dummycode') != -1, out

    def test_main(self):
        from strap import default_bootstrap
        factory = self._makeone(et=inspect.getsource(default_bootstrap))
        factory.main(['-r %s' %self.reqfile])
    

    
