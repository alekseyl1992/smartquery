from setuptools import setup, find_packages

version = '0.1.8'

setup(
    name="smartquery",
    version=version,
    description='SmartQuery',
    long_description='SmartQuery is a simple interpreted programming language'
                     ' designed to be easily embedded in other programs',
    author='Aleksey Leontiev',
    author_email='alekseyl@list.ru',
    license='CC BY-NC-SA 4.0',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Intended Audience :: Developers',
        'License :: Free for non-commercial use',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=[
        'setuptools>=40.6.2',
        'regex>=2020.11.13',
    ],
    extras_require={
        'repl': [
            'prompt-toolkit==3.0.36',
        ],
    },
)
