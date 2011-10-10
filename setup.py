#!/usr/bin/env python

from distutils.core import setup
from distutils.extension import Extension

rho_j_k_ext = Extension('dsf._rho_j_k', 
                        sources=['src/_rho_j_k.c'],
                        extra_compile_args=['-fopenmp', '-O3'],
                        extra_link_args=['-fopenmp'])


setup(name = 'python-dynsf',
      version = '0.1',
      description = 'Tool for calculating the dynamical structure factor',
      author = 'Mattias Slabanja',
      author_email = 'slabanja@chalmers.se',
      packages = ['dsf'],
      ext_modules = [rho_j_k_ext],
      scripts = ['dynsf'],
      requires = ['numpy'],
      license      = "GPL2+",
      classifiers  = ['Development Status :: 3 - Alpha',
                      'Intended Audience :: Education', 
                      'Intended Audience :: Science/Research',
                      'License :: OSI Approved :: GNU General Public License (GPL)',
                      'Programming Language :: Python',
                      'Programming Language :: C',
                      'Topic :: Scientific/Engineering :: Chemistry',
                      'Topic :: Scientific/Engineering :: Physics'
                      ]
      )

