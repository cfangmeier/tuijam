from setuptools import setup, find_packages
from setuptools.command.install import install
from tuijam import __version__

import sys

if sys.version_info < (3, 7):
    print("tuijam requires python>=3.7")
    exit(1)

with open("requirements.txt") as f:
    requirements = f.readlines()

with open("README.md") as f:
    desc = f.read()

class PostInstallCommand(install):
    def run(self):
        from babel.messages.frontend import compile_catalog
        compiler = compile_catalog(self.distribution)
        option_dict = self.distribution.get_option_dict('compile_catalog')
        compiler.domain = [option_dict['domain'][1]]
        compiler.directory = option_dict['directory'][1]
        compiler.run()
        super().run()

setup(
    name="tuijam",
    version=__version__,
    description="A fancy TUI client for Google Play Music",
    long_description=desc,
    long_description_content_type="text/markdown",
    url="https://github.com/cfangmeier/tuijam",
    author="Caleb Fangmeier",
    author_email="caleb@fangmeier.tech",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Environment :: Console :: Curses",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: Unix",
        "Topic :: Multimedia :: Sound/Audio :: Players",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="terminal music streaming",
    install_requires=requirements,
    setup_requires=['babel',],
    packages=find_packages(),
    entry_points={"console_scripts": ["tuijam=tuijam.app:main"]},
    cmdclass={"install": PostInstallCommand,},
    package_data={'tuijam': ['lang/*/*/*.mo', 'lang/*/*/*.po']},
    include_package_data=True,
)
