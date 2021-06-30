import vapoursynth as vs

core = vs.core


def blurred_dehalo(
    clip: vs.VideoNode = None,
    sigmaB: float = 16,
    sigmaG: float = None,
) -> vs.VideoNode:

    """
    Bilateral-based dehalo function. Dehalos's white regions
    using Bilateral blurring, and optionally dark lines using
    Gaussian blurring. Must be used with a mask. Intended for
    use with `ssfunc.dehalo.halocide`.

    :param clip:        Input clip to be dehalo'd
    :param sigmaB:      Sigma value for Bilateral
    :param sigmaG:      Sigma value for Gaussian

    """

    try:
        blurLight = clip.bilateralgpu.Bilateral(sigmaB)
    except:
        blurLight = clip.bilateral.Bilateral(sigmaS=sigmaB)

    if sigmaG is not None:

        blurDark = clip.bilateral.Gaussian(sigma=sigmaG)
        dehalo = core.std.Expr([blurLight, blurDark], "x y < x y ?")

    else:
        dehalo = blurLight

    return dehalo


def halocide(
    clip: vs.VideoNode = None, thmi: int = 164, thma: int = 256, **dehalo_args
) -> vs.VideoNode:

    from vardefunc.mask import FDOG
    from havsfunc import mt_expand_multi
    from vsutil import iterate, get_depth, plane, depth
    from util import scale

    # Building Mask

    if clip.format != vs.GRAY:
        luma = plane(clip, 0)
    else:
        luma = clip

    if get_depth(luma) != 8:
        luma = depth(luma, 8)

    peak = (1 << luma.format.bits_per_sample) - 1

    linemask = FDOG().get_mask(luma)
    edgemask = linemask.std.Expr(
        expr=[f"x {scale(thmi, peak)} - {thma - thmi} / 255 *"]
    )
    xpand = mt_expand_multi(edgemask, sw=1, sh=1)

    vEdge = core.std.Expr([luma, luma.std.Maximum().std.Maximum()], ["y x - 8 - 225 *"])
    mask2 = iterate(vEdge, core.std.Maximum, 2)
    mask2 = iterate(mask2, core.std.Minimum, 2)
    mask2 = mask2.std.Convolution(matrix=[1, 2, 1, 2, 4, 2, 1, 2, 1])
    mask = core.std.Expr([xpand, mask2], ["x y -"])

    dehalo = blurred_dehalo(clip, **dehalo_args)

    if get_depth(clip) != 8:
        dehalo_m = clip.std.MaskedMerge(dehalo, depth(mask, get_depth(clip)))
    else:
        dehalo_m = clip.std.MaskedMerge(dehalo, mask)

    return dehalo_m
