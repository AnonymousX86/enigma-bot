# -*- coding: utf-8 -*-
from setuptools import setup

from enigma.settings import version

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='3N1GM4',
    version=version,
    author='Jakub S.',
    url='https://github.com/AnonymousX86/Enigma-Bot',
    description='Multiple purpose Discord bot',
    license='GPL-3.0',
    packages=['enigma', 'enigma.cogs', 'enigma.utils'],
    python_requires='>=3.7.6',
    install_requires=requirements
)
