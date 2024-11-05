from setuptools import setup, find_packages

DESCRIPTION = 'Conflux account'
LONG_DESCRIPTION = 'Conflux account that can sign a conflux transaction'

extras_require = {
    'tester': [
        "pytest>8,<9",
        # "conflux-web3>=1.4.0",
    ],
    'linter': [
        # "black>=22.1.0,<23.0",
        # "flake8==3.8.3",
        # "isort>=4.2.15,<4.3.5",
        # "mypy==0.910",
        # "types-setuptools>=57.4.4,<58",
        # "types-requests>=2.26.1,<3",
        # "types-protobuf==3.19.13",
    ],
    'docs': [
        # "mock",
        # "sphinx-better-theme>=0.1.4",
        # "click>=5.1",
        # "configparser==3.5.0",
        # "contextlib2>=0.5.4",
        # "py-geth>=3.8.0,<4",
        # "py-solc>=0.4.0",
        # "pytest>=6.2.5,<7",
        # "sphinx>=4.2.0,<5",
        # "sphinx_rtd_theme>=0.1.9",
        # "toposort>=1.4",
        # "towncrier==18.5.0",
        # "urllib3",
        # "wheel"
    ],
    'dev': [
        # "bumpversion",
        "wheel",
        # "flaky>=3.7.0,<4",
        # "hypothesis>=3.31.2,<6",
        # "pytest>=6.2.5,<7",
        # "pytest-asyncio>=0.18.1,<0.19",
        # "pytest-mock>=1.10,<2",
        # "pytest-pythonpath>=0.3",
        # "pytest-watch>=4.2,<5",
        # "pytest-xdist>=1.29,<2",
        # "setuptools>=38.6.0",
        # "tox>=1.8.0",
        # "tqdm>4.32,<5",
        # "twine>=1.13,<2",
        # "pluggy==0.13.1",
        # "when-changed>=0.3.0,<0.4"
    ]
}

extras_require['dev'] = (
    extras_require['tester'] # type: ignore
    + extras_require['linter']
    + extras_require['docs']
    + extras_require['dev']
)
# Setting up
setup(
    name="cfx-account",
    version="1.2.1", # edit using bumpversion
    author="The conflux foundation",
    author_email="wangpan@conflux-chain.org",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    package_data={'cfx_account': ['py.typed']},
    install_requires=[
        "eth-account>=0.13.1",
        "cfx-address>=1.2.0",
        "cfx-utils>=1.0.5"
    ],  # add any additional packages that
    # needs to be installed along with your package. Eg: 'caer'
    extras_require=extras_require,
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