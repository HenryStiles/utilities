from setuptools import setup, find_packages

setup(
    name='utilities-repo',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pytest',
    ],
    entry_points={
        'console_scripts': [
            'zipcompare=scripts.zipcompare:main'
        ],
    },
    author='Henry Stiles',
    description='A collection of useful Python utilities.',
    license='MIT',
)