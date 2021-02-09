# -*- coding: utf-8 -*-
from setuptools import setup

from enigma.settings import bot_version

with open('requirements.txt') as f:
    requirements = f.read().splitlines()


with open('runtime.txt') as f:
    py_version = f.read().splitlines()[0]

setup(
    name='Enigma-Bot',
    version=bot_version(),
    author='Jakub Suchenek',
    url='https://github.com/AnonymousX86/Enigma-Bot',
    description='Multiple purpose Discord bot',
    license='GPL-3.0',
    packages=[
        'enigma',
        'enigma.cogs',
        'enigma.embeds',
        'enigma.settings',
        'enigma.utils'
    ],
    python_requires=f'~={py_version}',
    install_requires=requirements
)
