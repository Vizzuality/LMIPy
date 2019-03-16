import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="LMIPy",
    version="0.0.1",
    author="Vizzuality",
    author_email="benlaken@icloud.com",
    description="Interface to modify geospatial layers in the Resource Watch API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url="https://github.com/Vizzuality/LMIPy",
    install_requires=['requests>=2.2.0'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
