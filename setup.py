from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))
with open('README.md') as f:
    long_description = f.read()

setup(
    name='nighres',
    version='0.1.0',
    description='Processing tools for high-resolution neuroimaging',
    long_description=long_description,
    url='https://nighres.github.io/',
    author='Julia M Huntenburg, Pierre-Louis Bazin, Chris Steele',
    author_email='ju.huntenburg@gmail.com',
    license='Apache License, 2.0',
    classifiers=[
                 'Development Status :: 3 - Alpha',
                 'Intended Audience :: Scientists',
                 'Topic :: High-resolution Neuroimage Processing ',
                 'License :: Apache License, 2.0',
                 'Programming Language :: Python :: 2.7',
                 ],
    keywords='MRI high-resolution laminar',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['numpy', 'nibabel'],
)
