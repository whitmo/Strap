from itertools import count
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
    
    def _makeone(self, et='print "Wheeeeeeee"', bundle=None, reqfile=path(__file__).dirname() / 'testreq.txt'):
        from strap.factory import StrapFactory
        if bundle is None:
            td = path(tempfile.mkdtemp())
            bundle = td / 'test_bundle-%s.pybundle' %next(self.counter)
        return StrapFactory(et, bundle, reqfile)

    def test_init(self):
        factory = self._makeone('','','')
        assert factory
        
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

    def test_bundle_exec(self):
        env = os.environ['VIRTUAL_ENV']
        from strap import default_bootstrap
        factory = self._makeone(et=inspect.getsource(default_bootstrap))
        (stat, out) = commands.getstatusoutput('%s/bin/python %s' %(env, factory.run()))
        assert out.find('Successfully installed dummycode') != -1, out

    

    
