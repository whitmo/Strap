"""
This code gets inserted into the virtualenv generated bootstrap
"""
from extender import BootstrapExtender



class Strap(BootstrapExtender):
    """
    The `BootstrapExtender` class does all the work here.  This class
    exists for giving you a clear picture of how to write your hooks.
    """

    def modify_parser(self, optparse_parser):
        """
        Override this method to manipulate the default optparse
        instance.
        """
        pass
    
    def adjust_options(self, options, args):
        """
        Override to adjust options and args
        """
        pass

    def build_hook(self, options, home_dir):
        """
        Override this hook to add build steps.  This method is run
        regardless of whether the virtualenv is created or the bundle
        is just installed.
        """
        pass


_strap = Strap(__file__)

extend_parser = _strap.extend_parser
adjust_options = _strap.adjust_options
after_install = _strap.after_install
