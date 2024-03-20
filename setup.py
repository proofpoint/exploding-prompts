from os import path
from setuptools import setup, find_packages

cwd_path = path.abspath(path.dirname(__file__))

with open(path.join(cwd_path, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

with open("version.txt") as f:
    version = f.read().strip()

with open("requirements.txt") as f:
    requirements = f.read().split("\n")

setup(
    name="exploding_prompts",
    version=version,
    description="Prompt Lifecycle Management via exploding template composition.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="TBD: pfpt blog post",
    author="Jason Cronquist",
    author_email="jcronquist@proofpoint.com",
    classifiers=[],
    keywords="library",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=requirements,
    package_data={},
    entry_points={"console_scripts": ["exploding-prompts=exploding_prompts.cli:cli"]},
)
