import vapoursynth as vs
from enum import Enum

core = vs.core


class Mode(Enum):
    KIRSCH = 1
    FDOG = 2


def retinex_linemask(
    clip: vs.VideoNode, sigma: float = 1, scale: float = 1, mode: Mode = Mode.KIRSCH
) -> vs.VideoNode:
    """
    Use retinex to greatly improve the accuracy of the edge detection in dark scenes.
    Original function by kageru, modified by SeaSmoke and Zewia.

    Valid modes are:
        – 1: Uses Varde's fixed Kirsch mask.
        – 2: Uses FDOG for line detection and Extended Laplace for catching particles.

    :param clip:    Input clip
    :param sigma:   Sigma value for TCanny
    :param scale:   Multiplication factor
    :param mode:    Mask to be be used

    """
    from vardefunc.mask import FDOG, ExLaplacian1, Kirsch
    from vsutil import get_y

    luma = get_y(clip)
    ret = core.retinex.MSRCP(luma, sigma=[50, 200, 350], upper_thr=0.005)
    tcanny = ret.tcanny.TCanny(mode=1, sigma=sigma).std.Minimum(
        coordinates=2 * [1, 0] + 2 * [0, 1]
    )

    if mode == 1:
        if scale == 1:
            mask = get_y(Kirsch().get_mask(clip))
        else:
            mask = get_y(Kirsch().get_mask(clip)).std.Expr(f"x {scale} *")
        return core.std.Expr([mask, tcanny], "x y +")
    elif mode == 2:
        if scale == 1:
            fdm = get_y(FDOG().get_mask(clip))
        else:
            fdm = get_y(FDOG().get_mask(clip)).std.Expr(f"x {scale} *")

        exlap = get_y(ExLaplacian1().get_mask(clip))
        mask = core.std.Expr([fdm, exlap], "x y +")

        return core.std.Expr([mask, tcanny], "x y +")
    else:
        print("Invalid `mode` used.")
