from setuptools import setup

import sys

if sys.version_info < (3, 6):
    print('tuijam requires python>=3.6.')
    exit(1)

with open('requirements.txt') as f:
    requirements = f.readlines()

setup(
    name='tuijam',
    version='0.1.0',
    description='A fancy TUI client for Google Play Music',
    url='https://github.com/cfangmeier/tuijam',
    author='Caleb Fangmeier',
    author_email='caleb@fangmeier.tech',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console :: Curses',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: Unix',
        'Topic :: Multimedia :: Sound/Audio :: Players',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='terminal music streaming',
    install_requires=requirements,
    scripts=[
        'tuijam',
    ],
)
