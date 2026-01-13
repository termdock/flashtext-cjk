from setuptools import setup, Command
import subprocess


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        errno = subprocess.call(['py.test'])
        raise SystemExit(errno)

name = 'flashtext-i18n'
version = '2.8.0'

cmdclass = {'test': PyTest}

try:
    from sphinx.setup_command import BuildDoc
    cmdclass['build_sphinx'] = BuildDoc
except ImportError:
    print('WARNING: sphinx not available, not building docs')

setup(
    name=name,
    version=version,
    url='https://github.com/termdock/flashtext-i18n',
    author='termdock',
    author_email='termdock@users.noreply.github.com',
    description='Extract/Replace keywords in sentences. Fork with internationalization fixes.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=['flashtext'],
    install_requires=[],
    platforms='any',
    cmdclass=cmdclass,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: Chinese (Traditional)',
        'Natural Language :: Japanese',
        'Natural Language :: Korean',
    ],
    python_requires='>=3.8',
    command_options={
        'build_sphinx': {
            'project': ('setup.py', name),
            'version': ('setup.py', version),
            'release': ('setup.py', version)
        }
    }
)
