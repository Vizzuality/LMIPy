import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Skydipper",
    version="0.2.0",
    author="Vizzuality",
    author_email="benjamin.laken@vizzuality.com",
    description="Pythonic interface to the Skydipper API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url="https://github.com/Skydipper/Skydipper",
    install_requires=['requests>=2.2.0',
                        'folium==0.8.3',
                        'google-cloud-storage==1.25.0',
                        'earthengine-api==0.1.210',
                        'geopandas>=0.4.1',
                        'geojson>=2.4.0',
                        'pypng>=0.0.19',
                        'tqdm==4.41.1'],
    packages=['Skydipper'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
