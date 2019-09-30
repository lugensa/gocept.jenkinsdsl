# This should be only one line. If it must be multi-line, indent the second
# line onwards to keep the PKG-INFO file format intact.
"""Create a DSL script for the Jenkins Job DSL plugin from configuration.
"""

from setuptools import setup, find_packages
import glob


setup(
    name='gocept.jenkinsdsl',
    version='1.0',

    install_requires=[
        'setuptools >= 30',
    ],

    extras_require={
        'test': [
        ],
    },

    entry_points={
        'console_scripts': [
            'jenkinsdsl = gocept.jenkinsdsl.jenkinsdsl:main'
        ],
    },

    author='gocept <mail@gocept.com>',
    author_email='mail@gocept.com',
    license='ZPL 2.1',
    url='https://github.com/gocept/gocept.jenkinsdsl',

    keywords='jenkins DSL job groovy',
    classifiers="""\
Development Status :: 4 - Beta
License :: OSI Approved :: Zope Public License
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3 :: Only
Programming Language :: Python :: Implementation :: CPython
"""[:-1].split('\n'),
    description=__doc__.strip(),
    long_description='\n\n'.join(open(name).read() for name in (
        'README.rst',
        'HACKING.rst',
        'CHANGES.rst',
    )),

    namespace_packages=['gocept'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    data_files=[
        ('', glob.glob('*.txt')),
        ('', glob.glob('*.rst')),
    ],
    zip_safe=False,
)
