import unittest

class TestDottedNameResolver(unittest.TestCase):

    def _makeOne(self, package=None):
        from strap.resolver import _dotted_name_resolver as DottedNameResolver
        return DottedNameResolver(package)

    def config_exc(self, func, *arg, **kw):
        from strap.resolver import ConfigurationError
        try:
            func(*arg, **kw)
        except ConfigurationError, e:
            return e
        else:
            raise AssertionError('Invalid not raised') # pragma: no cover

    def test_zope_dottedname_style_resolve_absolute(self):
        typ = self._makeOne()
        result = typ._zope_dottedname_style(
            'strap.tests.test_resolver.TestDottedNameResolver')
        self.assertEqual(result, self.__class__)

    def test_zope_dottedname_style_irrresolveable_absolute(self):
        typ = self._makeOne()
        self.assertRaises(ImportError, typ._zope_dottedname_style,
            'strap.tests.test_resolver.nonexisting_name')

    def test__zope_dottedname_style_resolve_relative(self):
        import strap.tests
        typ = self._makeOne(package=strap.tests)
        result = typ._zope_dottedname_style(
            '.test_resolver.TestDottedNameResolver')
        self.assertEqual(result, self.__class__)

##     def test__zope_dottedname_style_resolve_relative_leading_dots(self):
##         import strap.tests.test_configuration
##         typ = self._makeOne(package=strap.tests)
##         result = typ._zope_dottedname_style(
##             '..tests.test_resolver.TestDottedNameResolver')
##         self.assertEqual(result, self.__class__)

    def test__zope_dottedname_style_resolve_relative_is_dot(self):
        import strap.tests
        typ = self._makeOne(package=strap.tests)
        result = typ._zope_dottedname_style('.')
        self.assertEqual(result, strap.tests)

    def test__zope_dottedname_style_irresolveable_relative_is_dot(self):
        typ = self._makeOne()
        e = self.config_exc(typ._zope_dottedname_style, '.')
        self.assertEqual(
            e.args[0],
            "relative name '.' irresolveable without package")

    def test_zope_dottedname_style_resolve_relative_nocurrentpackage(self):
        typ = self._makeOne()
        e = self.config_exc(typ._zope_dottedname_style, '.whatever')
        self.assertEqual(
            e.args[0],
            "relative name '.whatever' irresolveable without package")

    def test_zope_dottedname_style_irrresolveable_relative(self):
        import strap.tests
        typ = self._makeOne(package=strap.tests)
        self.assertRaises(ImportError, typ._zope_dottedname_style,
                          '.notexisting')

    def test__zope_dottedname_style_resolveable_relative(self):
        import strap
        typ = self._makeOne(package=strap)
        result = typ._zope_dottedname_style('.tests')
        from strap import tests
        self.assertEqual(result, tests)

    def test__zope_dottedname_style_irresolveable_absolute(self):
        typ = self._makeOne()
        self.assertRaises(
            ImportError,
            typ._zope_dottedname_style, 'strap.fudge.bar')

    def test__zope_dottedname_style_resolveable_absolute(self):
        typ = self._makeOne()
        result = typ._zope_dottedname_style(
            'strap.tests.test_resolver.TestDottedNameResolver')
        self.assertEqual(result, self.__class__)

    def test__pkg_resources_style_resolve_absolute(self):
        typ = self._makeOne()
        result = typ._pkg_resources_style(
            'strap.tests.test_resolver:TestDottedNameResolver')
        self.assertEqual(result, self.__class__)

    def test__pkg_resources_style_irrresolveable_absolute(self):
        typ = self._makeOne()
        self.assertRaises(ImportError, typ._pkg_resources_style,
            'strap.tests:nonexisting')

    def test__pkg_resources_style_resolve_relative(self):
        import strap.tests
        typ = self._makeOne(package=strap.tests)
        result = typ._pkg_resources_style(
            '.test_resolver:TestDottedNameResolver')
        self.assertEqual(result, self.__class__)

    def test__pkg_resources_style_resolve_relative_is_dot(self):
        import strap.tests
        typ = self._makeOne(package=strap.tests)
        result = typ._pkg_resources_style('.')
        self.assertEqual(result, strap.tests)

    def test__pkg_resources_style_resolve_relative_nocurrentpackage(self):
        typ = self._makeOne()
        from strap.resolver import ConfigurationError
        self.assertRaises(ConfigurationError, typ._pkg_resources_style,
                          '.whatever')

    def test__pkg_resources_style_irrresolveable_relative(self):
        import strap
        typ = self._makeOne(package=strap)
        self.assertRaises(ImportError, typ._pkg_resources_style,
                          ':notexisting')

    def test_resolve_not_a_string(self):
        typ = self._makeOne()
        e = self.config_exc(typ.resolve, None)
        self.assertEqual(e.args[0], 'None is not a string')

    def test_resolve_using_pkgresources_style(self):
        typ = self._makeOne()
        result = typ.resolve(
            'strap.tests.test_resolver:TestDottedNameResolver')
        self.assertEqual(result, self.__class__)

    def test_resolve_using_zope_dottedname_style(self):
        typ = self._makeOne()
        result = typ.resolve(
            'strap.tests.test_resolver:TestDottedNameResolver')
        self.assertEqual(result, self.__class__)

    def test_resolve_missing_raises(self):
        typ = self._makeOne()
        self.assertRaises(ImportError, typ.resolve, 'cant.be.found')

    def test_ctor_string_module_resolveable(self):
        import strap.tests
        typ = self._makeOne('strap.tests.test_resolver')
        self.assertEqual(typ.package, strap.tests)
        self.assertEqual(typ.package_name, 'strap.tests')

    def test_ctor_string_package_resolveable(self):
        import strap.tests
        typ = self._makeOne('strap.tests')
        self.assertEqual(typ.package, strap.tests)
        self.assertEqual(typ.package_name, 'strap.tests')

    def test_ctor_string_irresolveable(self):
        from strap.resolver import ConfigurationError
        self.assertRaises(ConfigurationError, self._makeOne, 'cant.be.found')

    def test_ctor_module(self):
        import strap.tests
        import strap.tests.test_resolver
        typ = self._makeOne(strap.tests.test_resolver)
        self.assertEqual(typ.package, strap.tests)
        self.assertEqual(typ.package_name, 'strap.tests')

    def test_ctor_package(self):
        import strap.tests
        typ = self._makeOne(strap.tests)
        self.assertEqual(typ.package, strap.tests)
        self.assertEqual(typ.package_name, 'strap.tests')

    def test_ctor_None(self):
        typ = self._makeOne(None)
        self.assertEqual(typ.package, None)
        self.assertEqual(typ.package_name, None)
