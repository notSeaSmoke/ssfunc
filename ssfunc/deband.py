import vapoursynth as vs
from vardefunc.deband import dumb3kdb
from vardefunc.placebo import deband as placebo_db
from vsutil import split, depth, get_depth, join

core = vs.core


def masked_deband(
    clip: vs.VideoNode,
    dmask: vs.VideoNode = None,
    output_depth: float = 16,
    placebo=False,
    **deband_args,
) -> vs.VideoNode:

    if get_depth(clip) != 16:
        clip = depth(clip, 16)

    planes = split(clip)
    planes[1] = placebo_db(planes[1], **deband_args)
    planes[2] = placebo_db(planes[2], **deband_args)

    if placebo:
        deband_y = placebo_db(planes[0], **deband_args)
    else:
        deband_y = dumb3kdb(planes[0], **deband_args)

    if dmask is not None:
        if get_depth(dmask) == get_depth(deband_y):
            planes[0] = deband_y.std.MaskedMerge(planes[0], dmask)
        else:
            dmask = depth(dmask, get_depth(deband_y))
            planes[0] = deband_y.std.MaskedMerge(planes[0], dmask)
    else:
        planes[0] = deband_y

    deband = join(planes)

    if output_depth != 16:
        return depth(deband, output_depth)
    else:
        return deband
