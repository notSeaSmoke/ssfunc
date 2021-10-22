"""
    SeaSmoke's VapourSynth functions. Varying levels of useless.
    Most of these are either adapted from other functions, or
    are wrappers around existing functions/plugins.
"""

import functools
from typing import Callable

from . import aa, deband, dehalo, misc, mask, misc, util  # noqa
from ._metadata import __version__, __author__  # noqa


class EpisodeNotFound(Exception):
    def __str__(self):
        return "Unrecognised episode. Ping @SeaSmoke#0002"


def __deprecate(old_name: str, func: Callable):
    @functools.wraps(func)
    def deprecated(*args, **kwargs) -> Callable:
        print(
            f"Warning: {old_name} is a deprecated alias for {func.__module__}.{func.__name__}."
            "If you're running this, please let the script writer know"
        )
        return func(*args, **kwargs)

    globals().update({old_name: deprecated})


__deprecate("RetinexLinemask", mask.retinex_linemask)
__deprecate("Blurred_Dehalo", dehalo.blurred_dehalo)
__deprecate("Halocide", dehalo.halocide)
__deprecate("OutputFrames", misc.output_ranges)
__deprecate("OutputFrames", misc.output_ranges)
__deprecate("OutputFramesSimple", misc.output_ranges)
__deprecate("ofs", misc.output_ranges)
__deprecate("ScreenGenMod", misc.screengen)
__deprecate("ScreenGen", misc.screengen)
__deprecate("LazyList", util.lazylist)
__deprecate("MaskedDB", deband.masked_deband)

masked_deband = deband.masked_deband
basedAA = aa.basedAA
