from fabric.api import local
from path import path
import argparse
import inspect
import sys
import virtualenv
import zipfile


try:
    from pyramid.utils import DottedNameResolver
except ImportError:
    from strap.resolver import DottedNameResolver


resolve = DottedNameResolver(None).maybe_resolve


class StrapFactory(object):

    const_slug = "<CONSTANTS>"
    
    def __init__(self, extra_text, bundle_name, requirements_file):
        self.text_spec = extra_text
        self.bundle_name = bundle_name
        self.requirements_file = requirements_file

    def constants(self):
        """
        Constants required by the __main__.py's functions 
        """
        pass

    @staticmethod
    def argparser(*args, **kw):
        parser = argparse.ArgumentParser(description='This is STRAP')
        parser.add_argument('-e', action="store", dest="extra_text", default='strap.default_bootstrap')
        parser.add_argument('-r', action="store", dest="requirements_file",
                            default=None, required=True)
        parser.add_argument('bundle_name', action="store", required=True)
        return parser.parse_args(*args, **kw)        

    def append_to_zip(self, bundle_path):
        """
        Add our __main__.py and path.py
        """
        import path as path_module
        import strap._main_ as main_mod
        
        with zipfile.ZipFile(bundle_path, mode='a') as bundle:
            bundle.writestr('path.py', inspect.getsource(path_module))
            bundle.writestr('bootstrap.py', virtualenv.create_bootstrap_script(self.extra_text))
            bundle.writestr('__main__.py', inspect.getsource(main_mod))

    def create_bundle(self):
        local('pip bundle -r %s %s' %(self.requirements_file, self.bundle_name))
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
        return et # just a string

    def inject_constants(self, text):
        return text

    @property
    def extra_text(self):
        et = getattr(self, '_extra_text', None)
        if et is None:
            et = self.resolve_extra_text(self.text_spec)
            self._extra_text = self.inject_constants(et)
        return self._extra_text

    def run(self):
        bundle_path = self.create_bundle()
        self.append_to_zip(bundle_path)
        return bundle_path

    @classmethod
    def main(cls, args=None):
        """
        bundle name
        -e extra text to resolve
        -r requirements file
        """
        if args is None:
            args = sys.argv
        args = cls.argparser(args)
        factory = cls(args.extra_text, args.bundle_name, args.requirements_file)
        return factory.run()


main = StrapFactory.main
resolve_extra_text = StrapFactory.resolve_extra_text



