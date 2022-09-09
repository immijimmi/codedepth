from setuptools import setup

with open("README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

setup(
    name="codedepth",
    packages=[
        "codedepth", "codedepth.parsers", "codedepth.colourpickers"
    ],
    version="2.0.2",
    license="MIT",
    description="Generates scores for how many layers of local imports/exports are in a file",
    long_description_content_type="text/markdown",
    long_description=long_description,
    author="immijimmi",
    author_email="imranhamid99@msn.com",
    url="https://github.com/immijimmi/codedepth",
    download_url="https://github.com/immijimmi/codedepth/archive/refs/tags/v2.0.2.tar.gz",
    keywords=[
        "abstraction", "level", "directory", "abstract", "imports", "import"
    ],
    install_requires=[
        "graphviz~=0.16", "networkx~=2.5", "matplotlib~=3.3.4"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
)
