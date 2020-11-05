import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="LMIPy",
    version="0.4.0",
    author="Vizzuality",
    author_email="benjamin.laken@vizzuality.com",
    description="Pythonic interface to various backend ecosystems related geospatial data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url="https://github.com/Vizzuality/LMIPy",
    install_requires=['requests>=2.2.0',
                        'pypng>=0.0.19',
                        'folium==0.8.3',
                        'geopandas>=0.4.1',
                        'geojson>=2.4.0',
                        'tqdm>=4.21.0'],
    packages=['LMIPy'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
