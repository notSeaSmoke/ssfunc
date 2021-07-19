import vapoursynth as vs

from lvsfunc.dehardsub import hardsub_mask
from lvsfunc.util import replace_ranges
from lvsfunc.types import Range

from typing import Union, List

core = vs.core


def dehardsub(
    hrdsb: vs.VideoNode, clean: vs.VideoNode, ref: vs.VideoNode = None, **kwargs
):
    """
    Dehardsub wrapper for lvsfunc.dehardsub.hardsub_mask.
    Generates dehardsub mask using `ref` clip, falls back to `clean`
    if `ref` is not supplied. Hardsubbed clip is dehardsubbed using
    `clean`.

    :param hrdsb:   Hardsubbed clip
    :param clean:   Clean clip
    :param ref:     Reference clip to generate mask
    :returns:       Dehardsubbed clip.
    :rtype:         vs.VideoNode

    """
    if ref is None:
        ref = clean

    mask = hardsub_mask(hrdsb, ref, **kwargs)
    return hrdsb.std.MaskedMerge(clean, mask)


def dehardsub_signs(
    hrdsb: vs.VideoNode,
    clean: vs.VideoNode,
    ref: vs.VideoNode = None,
    ranges: Union[Range, List[Range]] = None,
    **kwargs,
):

    """
    Dehardsub wrapper for lvsfunc.dehardsub.hardsub_mask.
    Generates dehardsub mask using `ref` clip, falls back to `clean`
    if `ref` is not supplied. Hardsubbed clip is dehardsubbed using
    `clean`.

    :param hrdsb:   Hardsubbed clip
    :param clean:   Clean clip
    :param ref:     Reference clip to generate mask
    :param ranges:  Sign ranges
    :returns:       Clip with Sign ranges replaced with dehardsubbed clip
    :rtype:         vs.VideoNode

    """
    if ref is None:
        ref = clean

    mask = hardsub_mask(hrdsb, ref, **kwargs)
    dehardsubbed_clip = hrdsb.std.MaskedMerge(clean, mask)

    return replace_ranges(hrdsb, dehardsubbed_clip, ranges)


def dehardsub_fading_signs(
    hrdsb: vs.VideoNode = None,
    clean: vs.VideoNode = None,
    ref: vs.VideoNode = None,
    ranges: List = [],
    **dehardsub_args,
) -> vs.VideoNode:

    """
    Dehardsub wrapper for lvsfunc.dehardsub.hardsub_mask.
    Uses the middle frame of the supplied range as the reference
    frame for generating the mask, and applies it to the whole
    range. This allows for clean dehardsubbing of static, fading signs.

    :param hrdsb:               Hardsubbed source
    :param clean:               Clean source to dehardsub
    :param ref:                 Optional extra reference clip, mask will be
    :param ranges:              A single range or list of ranges
    :param dehardsub_args:      arguments to pass to `lvsfunc.dehardsub.hardsub_mask`

    :return:    Dehardsubbed clip
    """
    from .util import midval

    if ref is None:
        ref = clean

    for r in ranges:
        start, end = r
        list = [*range(start, end + 1, 1)]
        mid = midval(list)

        dehardsubmask = (
            hardsub_mask(hrdsb[mid], ref[mid], **dehardsub_args) * hrdsb.num_frames
        )
        dehardsub_full = hrdsb.std.MaskedMerge(clean, dehardsubmask)
        dehardsubbed = replace_ranges(hrdsb, dehardsub_full, [(start, end)])
        hrdsb = dehardsubbed

    return dehardsubbed
