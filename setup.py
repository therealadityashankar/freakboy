#!/usr/bin/env python3
from setuptools import setup
from Cython.Build import cythonize

setup(
    name='freakboy',
    version='0.0.1',
    description='play specified frequencies and keyboard notes',
    author='Aditya Shankar',
    author_email='aditniru@gmail.com',
    packages=['freakboy'],
    install_requires=['pyaudio'],
    ext_modules=cythonize("freakboy/*.pyx")
)
