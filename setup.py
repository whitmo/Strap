from setuptools import setup
from setuptools import find_packages

version = '0.1'

setup(name='Strap',
      version=version,
      description="A bootstrap creator",
      long_description=""" """,
      classifiers=[], 
      keywords='',
      author='whit at surveymonkey.com',
      author_email='whit at surveymonkey.com',
      url='http://strap.github.com',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=["path.py",
                        "virtualenv",
                        "pip"],
      entry_points="""
      [console_scripts]
      strap = strap:main
      """,
      )
