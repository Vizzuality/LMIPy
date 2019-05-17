import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="LMIPy",
    version="0.1.15",
    author="Vizzuality",
    author_email="benjamin.laken@vizzuality.com",
    description="Interface to data and layers in the Resource Watch API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url="https://github.com/Vizzuality/LMIPy",
    install_requires=['requests>=2.2.0',
                        'folium>=0.8.0, <1.0',
                        'geopandas>=0.4.1',
                        'colored>=1.3.93',
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
