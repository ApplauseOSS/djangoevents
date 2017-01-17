from setuptools import setup

setup(
    name='djangoevents',
    version='0.9.2',
    url='https://github.com/ApplauseOSS/django-eventsourcing',
    license='MIT',
    description='small library that connects Django and eventsourcing package',
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
    ],
)
