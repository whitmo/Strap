from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='Strap',
      version=version,
      description="A bootstrap creator",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='whit at surveymonkey.com',
      author_email='whit at surveymonkey.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=["path.py",
                        "Fabric",
                        "virtualenv",
                        "pip"],
      entry_points="""
      [console_scripts]
      strap = strap:main
      """,
      )
