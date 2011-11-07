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
    
    def __init__(self, extra_text, packages, requirements_file=None, bundle_name=None, modules=default_modules, logger=logger):
        self.text_spec = extra_text
        self.requirements_file = requirements_file
        self.packages = packages
        self.modules = modules
        self.logger = logger
        self.bundle_name = self.make_bundle_name(bundle_name)

    def make_bundle_name(self, bundle_name, template="%s.strap.pybundle"):
        if bundle_name:
            if not bundle_name.endswith('pybundle'):
                return template % bundle_name
            return bundle_name
        
        if self.requirements_file:
            return template % path(self.requirements_file).namebase

        if self.packages:
            pkg_list = pkg_resources.parse_requirements('\n'.join(self.packages.split()))
            return template % '_'.join(x.project_name for x in pkg_list)

    @staticmethod
    def argparser(*args, **kw):
        parser = argparse.ArgumentParser(description='This is STRAP: creates executable bundles ' \
                                         'that creates loaded virtualenvs.')
        parser.add_argument('packages', action="store")
        parser.add_argument('-n', dest='bundle_name', action="store",
                            help='Name of output bundle')
        parser.add_argument('-p', dest='pip_options', action="store",
                            help='options for running pip to create bundle')
        parser.add_argument('-c', dest='config_file', action="store",
                            help="NotImplemented")
        parser.add_argument('-r', dest='requirements_file', action="store", default='',
                            help="A pip requirements file")
        parser.add_argument('-v', dest='virtualenv_options', action="store",
                            help='Any options you want passed to virtualenv creation')
        parser.add_argument('-m', action="store", dest="extra_text", default='strap.default_bootstrap',
                            help="dotted name for a module providing the extension api")
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
        arguments = dict(pip_options=self.pip_options or '',
                         packages=self.packages,
                         requires=self.requirements_file and "-r %s" %self.requirements_file or '',
                         bundle_name=self.bundle_name)
        cmd = 'pip bundle %(pip_options)s %(requires)s %(bundle_name)s %(packages)s' %arguments
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
            options = cls.argparser(args=args)
        else:
            options = cls.argparser()
        
        try:
            factory = cls(options.extra_text, options.packages, options.bundle_name, options.requirements_file)
            factory.setup_logger() # set level, format
            return factory.run()
        except :
            import pdb, sys; pdb.post_mortem(sys.exc_info()[2])








