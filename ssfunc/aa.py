import vapoursynth as vs

from typing import Dict, Any
from vsutil import depth, fallback, get_y, plane, join
from nnedi3_rpow2 import nnedi3_rpow2
from math import ceil

core = vs.core

shader = "FSRCNNX_x2_56-16-4-1.glsl"


def basedAA(
    clip,
    ssfac=2.0,
    mask_thr=60 << 8,
    fsrcnnx=False,
    shader=shader,
    opencl=False,
    **eedi3override,
):
    eedi3args: Dict[str, Any] = {
        "field": 0,
        "alpha": 0.125,
        "beta": 0.25,
        "gamma": 40,
        "nrad": 2,
        "mdis": 20,
        "vcheck": 2,
        "vthresh0": 12,
        "vthresh1": 24,
        "vthresh2": 4,
    }
    eedi3args.update(eedi3override)

    nnedi3args: Dict[str, Any] = dict(field=0, nsize=0, nns=4, qual=2)

    def eedi3s(clip, sclip, mclip=None):
        out = (
            clip.eedi3m.EEDI3CL(sclip=sclip, **eedi3args)
            if opencl
            else clip.eedi3m.EEDI3(sclip=sclip, **eedi3args)
        )

        if mclip is not None:
            return core.std.Expr([clip, out, mclip], "z y x ?")
        return out

    def nnedi3s(clip: vs.VideoNode, dh: bool = False) -> vs.VideoNode:
        return (
            clip.nnedi3cl.NNEDI3CL(dh=dh, **nnedi3args)
            if opencl
            else clip.nnedi3.nnedi3(dh=dh, **nnedi3args)
        )

    def resize_mclip(mclip, w=None, h=None):
        iw = mclip.width
        ih = mclip.height
        ow = fallback(w, iw)
        oh = fallback(h, ih)
        if (ow > iw and ow / iw != ow // iw) or (oh > ih and oh / ih != oh // ih):
            mclip = mclip.resize.Point(iw * ceil(ow / iw), ih * ceil(oh / ih))
        return mclip.fmtc.resample(ow, oh, kernel="box", fulls=1, fulld=1)

    clip = depth(clip, 16)

    aaw = round(clip.width * ssfac) >> 1 << 1
    aah = round(clip.height * ssfac) >> 1 << 1
    mask = (
        clip.std.Prewitt()
        .std.Binarize(mask_thr)
        .std.Maximum()
        .std.BoxBlur(0, 1, 1, 1, 1)
    )
    mclip = resize_mclip(mask, aaw, aah)
    mclip = get_y(mclip)

    aa = clip.std.Transpose()

    if fsrcnnx:
        aa = get_y(
            join([aa] * 3).placebo.Shader(
                shader=shader, filter="box", width=aa.width * 2, height=aa.height * 2
            )
        )
    else:
        aa = nnedi3_rpow2(get_y(aa), rfactor=ssfac)

    aa = aa.resize.Spline36(aah, aaw)

    if opencl:
        aa = eedi3s(aa, sclip=nnedi3s(aa)).std.Transpose()
        aa = eedi3s(aa, sclip=nnedi3s(aa)).resize.Spline16(clip.width, clip.height)
    else:
        aa = eedi3s(aa, sclip=nnedi3s(aa), mclip=mclip.std.Transpose()).std.Transpose()
        aa = eedi3s(aa, sclip=nnedi3s(aa), mclip=mclip).resize.Spline36(
            clip.width, clip.height
        )

    aa = get_y(clip).std.MaskedMerge(aa, resize_mclip(mclip, clip.width, clip.height))
    return join([aa, plane(clip, 1), plane(clip, 2)], vs.YUV)
