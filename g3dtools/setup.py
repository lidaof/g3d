import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='g3dtools',  
    version='0.1',
    scripts=['g3dtools'] ,
    author="Daofeng Li",
    author_email="lidaof@gmail.com",
    description="Generating and querying .g3d file",
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
