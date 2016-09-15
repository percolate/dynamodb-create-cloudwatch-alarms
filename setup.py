from setuptools import setup
from dynamodb_create_cloudwatch_alarms.constants import VERSION


setup(
    name='dynamodb-create-cloudwatch-alarms',
    version=VERSION,
    description='AWS DynamoDB Tool for creating Metric Alarms',
    url='https://github.com/percolate/dynamodb-create-cloudwatch-alarms',
    author='Mihailo Pavlisin',
    author_email='mihailo@percolate.com',
    license='GPLv3',
    keywords='aws dynamodb alarms cloudwatch boto',
    packages=['dynamodb_create_cloudwatch_alarms'],
    install_requires=[
        'boto',
        'docopt'
    ],
    entry_points={
        'console_scripts': [
            'dynamodb-create-cloudwatch-alarms=dynamodb_create_cloudwatch_alarms.main:main'
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Topic :: System :: Systems Administration"
    ]
)
