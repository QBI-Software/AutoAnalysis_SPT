from distutils.core import setup

setup(
    # Application name:
    name="MSD Analysis Application",

    # Version number (initial):
    version="0.1.0",

    # Application author details:
    author="Liz Cooper-Williams",
    author_email="e.cooperwilliams@uq.edu.au",
    maintainer="QBI Custom Software, UQ",
    maintainer_email="qbi-dev-admin@uq.edu.au",

    # Packages
    packages=["msdapp"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    #url="http://pypi.python.org/pypi/MyApplication_v010/",

    #
    license="LICENSE",
    description="MSD file processing for Meunier Lab",

    long_description=open("README.md").read(),

    # Dependent packages (distributions)
    install_requires=[
        "numpy","scipy",
    ],
)