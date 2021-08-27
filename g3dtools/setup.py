import setuptools

from utils import version

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='g3dtools',
    version=version.__version__,
    scripts=['g3dtools'],
    author="Daofeng Li",
    author_email="lidaof@gmail.com",
    description="Generate and query genome 3D stucture (.g3d) file",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lidaof/g3d",
    packages=setuptools.find_packages(),
    install_requires=[
        'msgpack',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
