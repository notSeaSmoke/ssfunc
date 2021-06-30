from setuptools import setup
from distutils.util import convert_path

# stolen from https://github.com/Irrational-Encoding-Wizardry/vsutil/blob/master/setup.py
meta = {}
exec(open(convert_path("ssfunc/_metadata.py")).read(), meta)

setup(
    name="ssfunc",
    version=meta["__version__"],
    packages=["ssfunc"],
    author=meta["__author__"],
    description=meta["__description__"],
    url="https://github.com/notSeaSmoke/ssfunc.git",
    install_requires=["vapoursynth"],
    python_requires=meta["__python__"],
)
