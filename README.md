</br>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href="https://github.com/psf/black/blob/master/LICENSE"><img alt="License: MIT" src="https://black.readthedocs.io/en/stable/_static/license.svg"></a>
</p>

# ssfunc
SeaSmoke's VapourSynth Functions.

~~aka shit I stole and pass off as my own~~

A mix of dumb and broken wrappers, some slighly useful wrappers, and a bunch of random utility functions. [util.py](https://github.com/notSeaSmoke/ssfunc/blob/master/ssfunc/util.py), [fansub.py](https://github.com/notSeaSmoke/ssfunc/blob/master/ssfunc/fansub.py), and [misc.py](https://github.com/notSeaSmoke/ssfunc/blob/master/ssfunc/misc.py) are the only ones you'd probably want to use. [dehalo.py](https://github.com/notSeaSmoke/ssfunc/blob/master/ssfunc/dehalo.py) is still a WIP, although it's probably good enough for use. The rest are simply wrappers around existing functions/plugins written because I'm a lazy ass, may or may not be broken.

If you find something broken or very obviously wrong, feel free to open an issue or send in a PR. 

# Installation
If you have an old `ssfunc.py` or an older `stolenfunc.py` on your system, delete that. Then run the following command.
```
python -m pip install git+https://github.com/notSeaSmoke/ssfunc.git
```

# Requirements
* [Python](https://www.python.org/downloads/) 3.9 or newer
* [VapourSynth](https://github.com/vapoursynth/vapoursynth/) r51 or newer
* [vsutil](https://github.com/Irrational-Encoding-Wizardry/vsutil/) 0.5.0 or newer
* [lvsfunc](https://github.com/Irrational-Encoding-Wizardry/lvsfunc/) 0.3.7 or newer
* [python-ass](https://github.com/chireiden/python-ass/) 0.5.2 or newer
* [subdigest](https://github.com/TypesettingTools/Myaamori-Aegisub-Scripts/tree/master/scripts/sub-digest)
