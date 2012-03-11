"""
Text inserted into the virtualenv generated bootstrap

`Strap` is a protocol stub. Define your own `Strap` to extend
"""
from extender import BootstrapExtender
import subprocess
import sys
import textwrap


class Strap(BootstrapExtender):
    """
    The `BootstrapExtender` class does all the work here.  This class
    exists for giving you a clear picture of how to write your hooks.
    """
    default_message = """
    Environment created and populated. To activate environment:

      $ cd %s
      $ . bin/activate

    Installed packages
    ==================
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
        sys.stdout.write('\n')
        sys.stdout.write(textwrap.dedent(self.default_message % home_dir))
        sys.stdout.write('\n')
        cmd = ". %(home_dir)s/bin/activate && %(home_dir)s/bin/pip freeze -l" %dict(home_dir=home_dir)
        subprocess.check_call(cmd, shell=True)


_strap = Strap(__file__)

extend_parser = _strap.extend_parser
adjust_options = _strap.adjust_options
after_install = _strap.after_install
#install_distribute = _strap.install_distribute
