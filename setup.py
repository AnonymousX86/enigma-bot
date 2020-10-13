from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='3N1GM4',
    version='0.1',
    author='Jakub S.',
    # url='',
    description='Multipurpose Discord bot',
    license='GPL-3.0',
    packages=['enigma', 'enigma.cogs', 'enigma.utils'],
    python_requires='>=3.8.1',
    install_requires=requirements
)
