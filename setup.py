#!/usr/bin/env python

# This file is part of PyEMMA.
#
# Copyright (c) 2015, 2014 Computational Molecular Biology Group, Freie Universitaet Berlin (GER)
#
# MSMTools is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""EMMA: Emma's Markov Model Algorithms

EMMA is an open source collection of algorithms implemented mostly in
`NumPy <http://www.numpy.org/>`_ and `SciPy <http://www.scipy.org>`_
to analyze trajectories generated from any kind of simulation
(e.g. molecular trajectories) via Markov state models (MSM).

"""

from __future__ import print_function, absolute_import

import sys
import os
from distutils.log import info

import versioneer
import warnings
from io import open

from setup_util import lazy_cythonize, get_pybind_include

try:
    from setuptools import setup, Extension, find_packages
except ImportError as ie:
    print("PyEMMA requires setuptools. Please install it with conda or pip.")
    sys.exit(1)

#if sys.version_info[0] < 3:
#    print('PyEMMA requires Python3k')
#    sys.exit(2)


DOCLINES = __doc__.split("\n")

CLASSIFIERS = """\
Development Status :: 5 - Production/Stable
Environment :: Console
Environment :: MacOS X
Intended Audience :: Science/Research
License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)
Natural Language :: English
Operating System :: MacOS :: MacOS X
Operating System :: POSIX
Operating System :: Microsoft :: Windows
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Topic :: Scientific/Engineering :: Bio-Informatics
Topic :: Scientific/Engineering :: Chemistry
Topic :: Scientific/Engineering :: Mathematics
Topic :: Scientific/Engineering :: Physics

"""
from setup_util import lazy_cythonize
try:
    from setuptools import setup, Extension, find_packages
except ImportError as ie:
    print("PyEMMA requires setuptools. Please install it with conda or pip.")
    sys.exit(1)

###############################################################################
# Extensions
###############################################################################
def extensions():
    """How do we handle cython:
    1. when on git, require cython during setup time (do not distribute
    generated .c files via git)
     a) cython present -> fine
     b) no cython present -> install it on the fly. Extensions have to have .pyx suffix
    This is solved via a lazy evaluation of the extension list. This is needed,
    because build_ext is being called before cython will be available.
    https://bitbucket.org/pypa/setuptools/issue/288/cannot-specify-cython-under-setup_requires

    2. src dist install (have pre-converted c files and pyx files)
     a) cython present -> fine
     b) no cython -> use .c files
    """
    USE_CYTHON = False
    try:
        from Cython.Build import cythonize
        USE_CYTHON = True
    except ImportError:
        warnings.warn('Cython not found. Using pre cythonized files.')


    import mdtraj
    # Note, that we add numpy include to every extension after declaration.
    from numpy import get_include as _np_inc
    np_inc = _np_inc()

    pybind_inc = get_pybind_include()

    lib_prefix = 'lib' if sys.platform.startswith('win') else ''
    common_cflags = ['-O3', ]

    clustering_module = \
        Extension('pyemma.coordinates.clustering._ext',
                  sources=['pyemma/coordinates/clustering/src/clustering_module.cpp'],
                  include_dirs=[
                      mdtraj.capi()['include_dir'],
                      pybind_inc,
                      'pyemma/coordinates/clustering/include',
                  ],
                  language='c++',
                  libraries=[lib_prefix+'theobald'],
                  library_dirs=[mdtraj.capi()['lib_dir']],
                  extra_compile_args=common_cflags)

    covar_module = \
        Extension('pyemma._ext.variational.estimators.covar_c._covartools',
                  sources=['pyemma/_ext/variational/estimators/covar_c/covartools.cpp'],
                  include_dirs=['pyemma/_ext/variational/estimators/covar_c/',
                                pybind_inc,
                                ],
                  language='c++',
                  extra_compile_args=common_cflags)

    eig_qr_module = \
        Extension('pyemma._ext.variational.solvers.eig_qr.eig_qr',
                  sources=['pyemma/_ext/variational/solvers/eig_qr/eig_qr.pyx'],
                  include_dirs=['pyemma/_ext/variational/solvers/eig_qr/', np_inc],
                  extra_compile_args=['-std=c99'] + common_cflags)

    orderedset = \
        Extension('pyemma._ext.orderedset._orderedset',
                  sources=['pyemma/_ext/orderedset/_orderedset.pyx'],
                  extra_compile_args=['-std=c99'] + common_cflags)

    extra_compile_args = ["-O3", "-std=c99"]
    ext_bar = Extension(
        "pyemma.thermo.extensions.bar",
        sources=["pyemma/thermo/extensions/bar/bar.pyx",
                 "pyemma/thermo/extensions/bar/_bar.c",
                 "pyemma/thermo/extensions/util/_util.c"],
        extra_compile_args=extra_compile_args)
    ext_wham = Extension(
        "pyemma.thermo.extensions.wham",
        sources=["pyemma/thermo/extensions/wham/wham.pyx",
                 "pyemma/thermo/extensions/wham/_wham.c",
                 "pyemma/thermo/extensions/util/_util.c"],
        extra_compile_args=extra_compile_args)
    ext_mbar = Extension(
        "pyemma.thermo.extensions.mbar",
        sources=["pyemma/thermo/extensions/mbar/mbar.pyx",
                 "pyemma/thermo/extensions/mbar/_mbar.c",
                 "pyemma/thermo/extensions/util/_util.c"],
        extra_compile_args=extra_compile_args)
    ext_tram = Extension(
        "pyemma.thermo.extensions.tram",
        sources=["pyemma/thermo/extensions/tram/tram.pyx",
                 "pyemma/thermo/extensions/tram/_tram.c",
                 "pyemma/thermo/extensions/util/_util.c"],
        extra_compile_args=extra_compile_args)
    ext_dtram = Extension(
        "pyemma.thermo.extensions.dtram",
        sources=["pyemma/thermo/extensions/dtram/dtram.pyx",
                 "pyemma/thermo/extensions/dtram/_dtram.c",
                 "pyemma/thermo/extensions/util/_util.c"],
        extra_compile_args=extra_compile_args)
    ext_trammbar = Extension(
        "pyemma.thermo.extensions.trammbar",
        sources=["pyemma/thermo/extensions/trammbar/trammbar.pyx",
                 "pyemma/thermo/extensions/tram/_tram.c",
                 "pyemma/thermo/extensions/util/_util.c"],
        extra_compile_args=extra_compile_args + ["-DTRAMMBAR"])
    ext_mbar_direct = Extension(
        "pyemma.thermo.extensions.mbar_direct",
        sources=["pyemma/thermo/extensions/mbar_direct/mbar_direct.pyx",
                 "pyemma/thermo/extensions/mbar_direct/_mbar_direct.c",
                 "pyemma/thermo/extensions/util/_util.c"],
        extra_compile_args=extra_compile_args)
    ext_tram_direct = Extension(
        "pyemma.thermo.extensions.tram_direct",
        sources=["pyemma/thermo/extensions/tram_direct/tram_direct.pyx",
                 "pyemma/thermo/extensions/tram_direct/_tram_direct.c",
                 "pyemma/thermo/extensions/util/_util.c"],
        extra_compile_args=extra_compile_args)
    ext_trammbar_direct = Extension(
        "pyemma.thermo.extensions.trammbar_direct",
        sources=["pyemma/thermo/extensions/trammbar_direct/trammbar_direct.pyx",
                 "pyemma/thermo/extensions/tram_direct/_tram_direct.c",
                 "pyemma/thermo/extensions/util/_util.c"],
        extra_compile_args=extra_compile_args + ["-DTRAMMBAR"])
    ext_util = Extension(
        "pyemma.thermo.extensions.util",
        sources=["pyemma/thermo/extensions/util/util.pyx",
                 "pyemma/thermo/extensions/util/_util.c"],
        extra_compile_args=extra_compile_args)

    exts_thermo = [
        ext_bar,
        ext_wham,
        ext_mbar,
        ext_tram,
        ext_dtram,
        ext_trammbar,
        ext_mbar_direct,
        ext_tram_direct,
        ext_trammbar_direct,
        ext_util]

    exts = [clustering_module,
             covar_module,
             eig_qr_module,
             orderedset
             ]
    exts += exts_thermo

    for e in exts:
        e.include_dirs.append(np_inc)

    if not USE_CYTHON:
        # replace pyx files by their pre generated c code.
        for e in exts:
            new_src = []
            for s in e.sources:
                new_src.append(s.replace('.pyx', '.c'))
            e.sources = new_src
    else:
        exts = cythonize(exts, language_level=sys.version_info[0])

    return exts


def get_cmdclass():
    versioneer_cmds = versioneer.get_cmdclass()

    sdist_class = versioneer_cmds['sdist']
    class sdist(sdist_class):
        """ensure cython files are compiled to c, when distributing"""

        def run(self):
            # only run if .git is present
            if not os.path.exists('.git'):
                print("Not on git, can not create source distribution")
                return

            try:
                from Cython.Build import cythonize
                print("cythonizing sources")
                cythonize(extensions())
            except ImportError:
                warnings.warn('sdist cythonize failed')
            return sdist_class.run(self)

    versioneer_cmds['sdist'] = sdist

    from setuptools.command.test import test as TestCommand

    class PyTest(TestCommand):
        user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

        def initialize_options(self):
            TestCommand.initialize_options(self)
            self.pytest_args = ['pyemma']

        def run_tests(self):
            # import here, cause outside the eggs aren't loaded
            import pytest
            errno = pytest.main(self.pytest_args)
            sys.exit(errno)

    versioneer_cmds['test'] = PyTest

    from setuptools.command.build_ext import build_ext
    # taken from https://github.com/pybind/python_example/blob/master/setup.py
    class BuildExt(build_ext):
        """A custom build extension for adding compiler-specific options."""
        c_opts = {
            'msvc': ['/EHsc'],
            'unix': [],
        }

        def build_extensions(self):
            from setup_util import cpp_flag, has_flag, detect_openmp
            # enable these options only for clang, OSX
            if sys.platform == 'darwin':
                import sysconfig
                compiler = os.path.basename(sysconfig.get_config_var("CC"))
                if 'clang' in str(compiler):
                    self.c_opts['unix'] += ['-stdlib=libc++', '-mmacosx-version-min=10.7']

            ct = self.compiler.compiler_type
            opts = self.c_opts.get(ct, [])
            if ct == 'unix':
                opts.append('-DVERSION_INFO="%s"' % self.distribution.get_version())
                opts.append(cpp_flag(self.compiler))
                if has_flag(self.compiler, '-fvisibility=hidden'):
                    opts.append('-fvisibility=hidden')
            elif ct == 'msvc':
                opts.append('/DVERSION_INFO=\\"%s\\"' % self.distribution.get_version())

            # setup OpenMP support
            openmp_enabled, additional_libs = detect_openmp(self.compiler)
            if openmp_enabled:
                warnings.warn('enabled openmp')
                if sys.platform == 'darwin':
                    omp_compiler_args = ['-fopenmp=libiomp5']
                else:
                    omp_compiler_args = ['-fopenmp']
                omp_libraries = ['-l%s' % l for l in additional_libs]
                omp_defines = [('USE_OPENMP', None)]
            # debug
            if self.debug:
                dbg_flag = ['-g']
            else:
                dbg_flag = ['-g0', '-DNDEBUG']

            for ext in self.extensions:
                if ext.language == 'c++':
                    ext.extra_compile_args = opts + dbg_flag
                elif ext.language is None:  # C
                    ext.extra_compile_args += dbg_flag
                if openmp_enabled:
                    ext.extra_compile_args += omp_compiler_args
                    ext.extra_link_args += omp_libraries
                    ext.define_macros += omp_defines

            build_ext.build_extensions(self)

    versioneer_cmds['build_ext'] = BuildExt

    return versioneer_cmds


metadata = dict(
    name='pyEMMA',
    maintainer='Martin K. Scherer',
    maintainer_email='m.scherer@fu-berlin.de',
    author='The Emma team',
    author_email='info@emma-project.org',
    url='http://github.com/markovmodel/PyEMMA',
    license='LGPLv3+',
    description=DOCLINES[0],
    long_description=open('README.rst', encoding='utf8').read(),
    version=versioneer.get_version(),
    platforms=["Windows", "Linux", "Solaris", "Mac OS-X", "Unix"],
    classifiers=[c for c in CLASSIFIERS.split('\n') if c],
    keywords='Markov State Model Algorithms',
    # install default emma.cfg into package.
    package_data=dict(pyemma=['pyemma.cfg']),
    cmdclass=get_cmdclass(),
    tests_require=['pytest'],
    # runtime dependencies
    install_requires=[
        'bhmm>=0.6,<0.7',
        'decorator>=4.0.0',
        'h5py>=2.7.1',
        'matplotlib',
        'mdtraj>=1.8.0',
        'msmtools>=1.2',
        'numpy>=1.8.0',
        'pathos',
        'psutil>=3.1.1',
        'pyyaml',
        'scipy>=0.11',
        'thermotools>=0.2.6',
        'tqdm>=4.23',
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': ['pyemma_list_models=pyemma._base.serialization.cli:main']
    }
)

# this is only metadata and not used by setuptools
metadata['requires'] = ['numpy', 'scipy']

# not installing?
if len(sys.argv) == 1 or (len(sys.argv) >= 2 and ('--help' in sys.argv[1:] or
                          sys.argv[1] in ('--help-commands',
                                          '--version',
                                          'clean'))):
    pass
else:
    # setuptools>=2.2 can handle setup_requires
    metadata['setup_requires'] = ['numpy>=1.7.0',
                                  'scipy',
                                  'mdtraj>=1.7.0',
                                  'pybind11',
                                  ]

    metadata['package_data'] = {
                                'pyemma': ['pyemma.cfg', 'logging.yml'],
                                'pyemma.coordinates.tests': ['data/*'],
                                'pyemma.msm.tests': ['data/*'],
                                'pyemma.datasets': ['*.npz'],
                                'pyemma.util.tests': ['data/*'],
                                }

    # when on git, we require cython
    if os.path.exists('.git'):
        warnings.warn('using git, require cython')
        metadata['setup_requires'] += ['cython>=0.22']

        # init submodules
        import subprocess
        modules = []
        cmd = "git submodule update --init {mod}"
        for m in modules:
            subprocess.check_call(cmd.format(mod=m).split(' '))

    # only require numpy and extensions in case of building/installing
    metadata['ext_modules'] = lazy_cythonize(callback=extensions)
    # packages are found if their folder contains an __init__.py,
    metadata['packages'] = find_packages()

if __name__ == '__main__':
    setup(**metadata)
