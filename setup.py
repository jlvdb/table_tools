import setuptools
import os


with open("requirements.txt") as f:
    install_requires = [pkg.strip() for pkg in f.readlines() if pkg.strip()]
scripts = [
    os.path.join("bin", fname) for fname in os.listdir("bin")]

setuptools.setup(
    name="table_tools",
    version="1.0",
    author="Jan Luca van den Busch",
    description="Tools to handle astronomical table data.",
    url="https://github.com/jlvdb/table_tools",
    packages=setuptools.find_packages(),
    scripts=scripts,
    install_requires=install_requires)
