from mock import Mock
from mock import patch
from path import path
import unittest


class TestBootstrapExtender(unittest.TestCase):
    """
    The extender object is injected into the generated bootstrap. We
    test it's basic organs here.
    """
    def _make_one(self, location='/here', dist=True):
        from strap import extender
        return extender.BootstrapExtender(location, dist)
        
    def test_subprocess_prop(self):
        """
        Subproc property outside of a true bootstrap should be a noop.
        """
        be = self._make_one()
        assert be.subprocess.__module__ == 'strap.bootstrap'
        assert be.subprocess() is None

##     def test_bundle_prop(self):
##         be = self._make_one('tests/testreq.txt')
##         assert be.bundle.abspath().name == 'tests', be.bundle.name

    def test_virtualenv_prop(self):
        """
        should always be run in an env and always return a path object
        """
        be = self._make_one()
        assert isinstance(be.virtualenv, path), be.virtualenv

    def test_stubs(self):
        be = self._make_one()
        assert be.modify_parser(None) is None
        assert be.adjust_options(None, None) is None
        assert be.build_hook(None, None) is None

    @patch('sys.exit')
    def test_extendparser(self, exit_mock):
        be = self._make_one()
        parser = Mock()
        arg_ret = Mock()
        parser.parse_args = Mock(return_value=(arg_ret, None))
        arg_ret.verbose = 1
        arg_ret.quiet = 1
        assert be.extend_parser(parser) is None
        assert exit_mock.call_args[0][0] == 0

    @patch('strap.extender.BootstrapExtender.build_hook')
    @patch('strap.extender.BootstrapExtender.subprocess')
    def test_afterinstall(self, subproc_mock, bh_mock):
        be = self._make_one()
        be.after_install("options", "homedir")
        assert subproc_mock
        assert bh_mock

def test_bootstrap_dummy():
    from strap import bootstrap
    assert bootstrap.main() is None


def test_hook_protocol_stub():
    """
    These are stubs, should take the right number of args and do
    nothing.
    """
    from strap import default_bootstrap
    strap = default_bootstrap.Strap('here')
    assert strap.modify_parser(None) is None
    assert strap.adjust_options(None, None) is None
    assert strap.build_hook(None, None) is None



