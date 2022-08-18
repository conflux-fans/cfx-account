from setuptools import setup, find_packages

DESCRIPTION = 'Conflux account'
LONG_DESCRIPTION = 'Conflux account that can sign a conflux transaction'

# python3 -m build
# twine upload --repository cfx-account dist/*

# Setting up
setup(
    name="cfx-account",
    version="0.1.0-beta.3", # edit using bumpversion
    author="The conflux foundation",
    author_email="wangpan@conflux-chain.org",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        "eth-account>=0.6.0,<0.7.0",
        "cfx-address>=1.0.0b1"
    ],  # add any additional packages that
    # needs to be installed along with your package. Eg: 'caer'

    keywords=['blockchain', 'conflux', "sign"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)