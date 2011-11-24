from path import path
from process import Process
from strap.resolver import DottedNameResolver
import argparse
import inspect
import logging
import pkg_resources
import sys
import virtualenv
import zipfile


logger = logging.getLogger(__name__)
resolve = DottedNameResolver(None).maybe_resolve


class StrapFactory(object):

    default_modules = [('path.py', 'path'),
                       ('__main__.py', 'strap._main_'),
                       ('extender.py', 'strap.extender')]

    process = Process
    
    def __init__(self, extra_text, packages, requirements_files=[], bundle_name=None, modules=default_modules, logger=logger):
        self.text_spec = extra_text
        self.requirements_files = [x.lstrip() for x in requirements_files]
        self.packages = packages
        self.modules = modules
        self.logger = logger
        self.bundle_name = self.make_bundle_name(bundle_name)

    def make_bundle_name(self, bundle_name, template="%s.strap.pybundle"):
        if bundle_name:
            if not bundle_name.endswith('pybundle'):
                return template % bundle_name
            return bundle_name
        
        if self.requirements_files:
            return template % path(self.requirements_files[0]).namebase

        if self.packages:
            pkg_list = pkg_resources.parse_requirements('\n'.join(self.packages))
            return template % '_'.join(x.project_name for x in pkg_list)

    @staticmethod
    def argparser(*args, **kw):
        parser = argparse.ArgumentParser(description="""
        STRAP creates executable python bundles that create populated
        virtualenvs.
        """)
        parser.add_argument('packages', nargs='*', metavar="PKG_SPEC",
                            default=None,
                            help="0-N package specifications."), 
        parser.add_argument('-n', dest='bundle_name',
                            help='Name of output bundle')

# unimplemented options
## @@ consider -o for output directory
##         parser.add_argument('-p', dest='pip_options',
##                             help="""
##                             options for running pip to create bundle
##                             ex: find_links, index, etc.
##                             """)
##        parser.add_argument('-c', dest='config_file',
##                             help="NotImplemented")
##         parser.add_argument('-e', dest='editable_reqs',
##                             default=[], action='append',
##                             metavar="LOCAL_OR_VCS_SRC",
##                             help="A file system or vcs source tree. May be used multiple times.")
##         parser.add_argument('-v', dest='virtualenv_options', metavar='VENV_OPT',
##                             help='Any options you want passed to virtualenv creation.')
        
        parser.add_argument('-r', dest='requirements_file',
                            default=[], action='append',
                            help="A pip requirements file.  Mayb be used multiple times.")

        parser.add_argument('-m', dest="extra_text", default='strap.default_bootstrap',
                            help="dotted name for a module providing the extension api.")
        return parser.parse_args(*args, **kw)        

    def append_to_zip(self, bundle_path):
        """
        Populate the bundle with necessary bootstrapping python
        """
        with zipfile.ZipFile(bundle_path, mode='a') as bundle:
            for mod_name, spec in self.modules:
                mod = resolve(spec)
                if mod is not None:
                    bundle.writestr(mod_name, inspect.getsource(mod))
                else:
                    #@@ needs negative test
                    logger.error("%s does not return a module", spec)
            bundle.writestr('bootstrap.py', virtualenv.create_bootstrap_script(self.extra_text))

    @property
    def pip_options(self):
        pass            

    def create_bundle(self):
        requirements_files = None
        if self.requirements_files and not isinstance(self.requirements_files, basestring):
            requirements_files = "-r %s" % " -r ".join(self.requirements_files)

        arguments = dict(pip_options=self.pip_options or '',
                         packages=' '.join(self.packages),
                         requires=requirements_files or '',
                         bundle_name=self.bundle_name)
        cmd = 'pip bundle %(pip_options)s %(requires)s %(bundle_name)s %(packages)s' %arguments
        cmd = cmd.replace('  ', ' ')
        try:
            self.process(cmd, self.logger).run()
        except OSError, e:
            self.logger.error("%s", e)
            sys.exit(e.retcode)
        return path('.').abspath() / self.bundle_name

    @staticmethod
    def resolve_extra_text(et):
        """
        Given a string `et` that is either a filepath or the dotted name
        to a module, returns the contents of the file as a string.
        """
        if path(et).exists():
            return path(et).text()
        module = None
        try:
            module = resolve(et)
        except ImportError:
            pass
        except ValueError:
            pass
        if module and inspect.ismodule(module):
            return path(inspect.getsourcefile(module)).text()
        assert isinstance(et, basestring)
        return et # just a string

    @property
    def extra_text(self):
        et = getattr(self, '_extra_text', None)
        if et is None:
            et = self.resolve_extra_text(self.text_spec)
            self._extra_text = et
        return self._extra_text

    def run(self):
        bundle_path = self.create_bundle()
        self.append_to_zip(bundle_path)
        return bundle_path

    def setup_logger(self, format="%(message)s", level=logging.INFO):
        root = logging.getLogger()
        if root.handlers:
            root.handlers = []
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter(format))
        root.setLevel(level)
        root.addHandler(ch)
        return root

    @classmethod
    def main(cls, args=None):
        if args is not None:
            options = cls.argparser(args)
        else:
            options = cls.argparser()
        
        factory = cls(options.extra_text, options.packages, options.requirements_file, options.bundle_name)
        factory.setup_logger() # set level, format
        return factory.run()









