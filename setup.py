import runpy
from setuptools import setup, find_packages

PACKAGE_NAME = "epiphancloud"
VERSION = "2.0"

with open("README.md") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    requirements = []
    for r in f.readlines():
        r = r.strip()
        if len(r) > 0 and r[0] != '#':
            requirements.append(r)

if __name__ == "__main__":
    setup(
        name=PACKAGE_NAME,
        version=VERSION,
        packages=find_packages(),
        install_requires=requirements,
        python_requires=">=2.7",
        description="Python wrappers for Epiphan Cloud public API",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/epiphan-video/epiphancloud_api",
        author="Vadim Kalinsky",
        author_email="vkalinsky@epiphan.com",
        keywords="epiphancloud",
        project_urls={
            "Documentation": "https://epiphan-video.github.io/epiphancloud_api"
        },
        license="MIT"
    )
