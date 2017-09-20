from setuptools import setup
from setuptools.command.upload import upload
import os


class ReleaseToPyPICommand(upload):

    def finalize_options(self):
        self.repository = 'https://upload.pypi.org/legacy/'
        self.username = os.environ['PYPI_USERNAME']
        self.password = os.environ['PYPI_PASSWORD']


setup(
    name='djangoevents',
    version='0.13.2',
    url='https://github.com/ApplauseOSS/djangoevents',
    license='MIT',
    description='Building blocks for building Event Sourcing Django applications.',
    author='Applause',
    author_email='eng@applause.com',
    zip_safe=False,
    packages=[
        'djangoevents',
        'djangoevents.migrations',
        'djangoevents.tests.settings',
    ],
    include_package_data=True,
    install_requires=[
        'eventsourcing>=1.2,<1.3',
        'django',
        'avro-python3==1.7.7',
        'stringcase==1.0.6',
    ],
    cmdclass={
        'release_to_pypi': ReleaseToPyPICommand
    }
)
