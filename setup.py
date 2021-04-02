from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Conflux account'
LONG_DESCRIPTION = 'Conflux account that can sign a conflux transaction'

# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="cfx-account",
    version=VERSION,
    author="The conflux foundation",
    author_email="wangpan@conflux-chain.org",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        "eth-account>=0.5.3,<0.6.0",
        "cfx-address"
    ],  # add any additional packages that
    # needs to be installed along with your package. Eg: 'caer'

    keywords=['python', 'first package'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)