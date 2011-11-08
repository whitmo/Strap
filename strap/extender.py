from path import path
import os
import sys


class BootstrapExtender(object):
    """
    Extension base class, included in the executable bundle. State bag
    for virtualenv hook functions.  Basically some reach arounds to
    help deal with wrapping virtualenv from the inside.
    """
    
    def __init__(self, location, use_distribute=True):
        self.location = path(location).parent.abspath()
        self.use_distribute = use_distribute
    
    _subprocess = False
    
    @property
    def subprocess(self):
        if not self._subprocess:
            from bootstrap import call_subprocess
            self._subprocess = call_subprocess
        return self._subprocess

    @property
    def bundle(self):
        # assumes Extender lives in root of pybundle
        return path(self.location).parent

##     @property
##     def workon_home(self):
# feature is coming
##         venv = os.environ.get('WORKON_HOME')
##         if venv:
##             return path(venv)
##         return None

    @property
    def virtualenv(self):
        venv = os.environ.get('VIRTUAL_ENV')
        if venv:
            return path(venv)

    def extend_parser(self, optparse_parser):
        """
        As extend_parser is run before any other hook, we can use it
        to make split logic between installing the bundle in the
        current virtualenv or creating a new virtualenv.
        """
        self.modify_parser(optparse_parser)
        if self.virtualenv:
            options, args = optparse_parser.parse_args()
            self.setup_logger_global(options)
            self.subprocess(('pip install %s' %self.bundle).split(' '))
            self.adjust_options(options, args)
            self.build_hook(options, self.virtualenv)
            sys.exit(0)

    def setup_logger_global(self, options):
        import bootstrap
        verbosity = options.verbose - options.quiet
        bootstrap.logger = bootstrap.Logger([(bootstrap.Logger.level_for_integer(2-verbosity), sys.stdout)])

    def after_install(self, options, home_dir):
        cmd = "%(home_dir)s/bin/pip install -E %(home_dir)s %(location)s" %dict(home_dir=home_dir, location=self.location)
        self.subprocess(cmd.split(' '))
        self.build_hook(options, home_dir)

    def adjust_options(self, options, args):
        """
        Override to adjust options and args
        """
        pass

    def build_hook(self, options, home_dir):
        """
        Override this hook to add build steps
        """
        print "this is a message".upper()

    def modify_parser(self, optparse_parser):
        """
        Override this method to manipulate the default optparse
        instance
        """
        pass



