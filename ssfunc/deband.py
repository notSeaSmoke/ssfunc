import vapoursynth as vs
from debandshit import dumb3kdb
from vsutil import split, depth, get_depth, join

core = vs.core


def masked_deband(
    clip: vs.VideoNode,
    dmask: vs.VideoNode = None,
    output_depth: float = 16,
    placebo: bool = True,
    chroma: bool = True,
    luma_args: dict = None,
    chroma_args: dict = None,
) -> vs.VideoNode:

    """
    Unified masked debanding wrapper for vapoursynth. Handles plane-splitting, bitdepth conversions, and masking.
    Currently supports Varde's dumb3kdb and vapoursynth-placebo. Support for GradFun3 and f3kbilateral is planned.

    Dependencies:

    * vapoursynth-placebo
    * vardefunc
    * debandshit

    :param clip: Input clip
    :param dmask: Mask clip
    :param output_depth: Output bitdepth
    :param placebo: Use vapoursynth-placebo deband
    :param chroma: Apply chroma deband
    :param luma_args: Arguments passed for luma deband
    :param chroma_args: Arguments passed for chroma deband

    :return: Debanded clip

    WIP:

    * Chroma handling for f3kdb.
    * Scenefiltering with f3kbilateral
    * Handling variable format clips

    """

    if get_depth(clip) != 16:
        clip = depth(clip, 16)

    planes = split(clip)

    if placebo and chroma:
        db = join(
            [
                core.placebo.Deband(planes[0], **luma_args),
                core.placebo.Deband(planes[1], **chroma_args),
                core.placebo.Deband(planes[2], **chroma_args),
            ]
        )
    elif placebo:
        deband_y = core.placebo.Deband(
            planes[0], iterations=1, threshold=3, radius=16, grain=3
        )
        db = join([deband_y, planes[1], planes[2]])
    else:
        deband_y = dumb3kdb(planes[0], **luma_args)
        db = join([deband_y, planes[1], planes[2]])

    if dmask is not None:
        if get_depth(dmask) == get_depth(db):
            planes[0] = db.std.MaskedMerge(clip, dmask)
        else:
            dmask = depth(dmask, get_depth(deband_y))
            planes[0] = db.std.MaskedMerge(clip, dmask)
    else:
        planes[0] = deband_y

    if output_depth != 16:
        return depth(db, output_depth)
    else:
        return db
