import vapoursynth as vs
import os

from .util import lazylist
from typing import cast, Tuple, List

core = vs.core


def output_ranges(clip: vs.VideoNode, ranges: str = None) -> vs.VideoNode:
    """
    Simple modification of fvsfunc.ReplaceFrames() that returns ranges
    of input clips rather than replacing them with a different clip.

    Could be useful for testing filter settings, i.e. make a test encode
    of all filtered ranges to confirm scenefiltering is as expected.

    Functions almost entirely the same as rfs (as the point is to be able
    to use it to test rfs), with the only difference being that, since
    zero length clips are not supported in VapourSynth, mappings without
    any ranges (i.e. what would pass through `clipa` in rfs) will throw
    an error here.

    Original function by EoE, modified by SeaSmoke to lvsfunc.ReplaceFrames
    format.

    :param clip:        Input clip
    :param ranges:      Frame ranges for output. Ranges are inclusive exactly the same as fvsfunc.ReplaceFrames.

    :return:            Clip trimmed to specified frame ranges
    """

    if not isinstance(clip, vs.VideoNode):
        raise TypeError('OutputFrames: "clipa" must be a clip!')

    for r in ranges:
        if type(r) is tuple:
            start, end = cast(Tuple[int, int], r)
        else:
            start = cast(int, r)
            end = cast(int, r)

    if start > end:
        raise ValueError(
            "OutputFrames: Start frame is bigger than end frame: [{} {}]".format(
                start, end
            )
        )
    if end >= clip.num_frames:
        raise ValueError(
            "OutputFrames: End frame too big, one of the clips has less frames: {}".format(
                end
            )
        )

    # create clip with with tempory frame at the start as zero length clips aren't allowed by vs
    out = core.std.BlankClip(clip, length=1)
    for start, end in ranges:
        out = out + clip[start : end + 1]
    # remember to remove our tempory frame
    return out[1:]


def screengen(
    clip: vs.VideoNode,
    folder: str,
    prefix: str,
    frame_numbers: List = None,
    start: int = 1,
    delim=" ",
):
    """
    Mod of Narkyy's screenshot generator, stolen from awsmfunc.
    Generates screenshots from a list of frames.
    Not specifying `frame_numbers` will use `ssfunc.util.lazylist()` to generate a list of frames.

    :param folder:            Name of folder where screenshots are saved.
    :param prefix:            Name prepended to screenshots (usually group name).
    :param frame_numbers:     List of frames. Either a list or an external file.
    :param start:             Frame to start from.
    :param delim:             Delimiter for the external file.

    > Usage: ScreenGen(src, "Screenshots", "a")
             ScreenGen(enc, "Screenshots", "b")
    """

    frame_num_path = "./{name}".format(name=frame_numbers)
    folder_path = "./{name}".format(name=folder)

    if isinstance(frame_numbers, str) and os.path.isfile(frame_num_path):
        with open(frame_numbers) as f:
            screens = f.readlines()

        # Keep value before first delim, so that we can parse default detect zones files
        screens = [v.split(delim)[0] for v in screens]

        # str to int
        screens = [int(x.strip()) for x in screens]

    elif isinstance(frame_numbers, list):
        screens = frame_numbers

    elif frame_numbers is None:
        screens = lazylist(clip)

    else:
        raise TypeError(
            "frame_numbers must be a a list of frames, a file path, or None"
        )

    if not os.path.isdir(folder_path):
        os.mkdir(folder_path)

    for i, num in enumerate(screens, start=start):
        filename = "{path}/{prefix}{:03d}.png".format(
            i, path=folder_path, prefix=prefix
        )

        matrix = clip.get_frame(0).props._Matrix

        if matrix == 2:
            matrix = 1

        print(f"Saving Frame {i}/{len(screens)} from {prefix}", end="\r")
        core.imwri.Write(
            clip.resize.Spline36(
                format=vs.RGB24, matrix_in=matrix, dither_type="error_diffusion"
            ),
            "PNG",
            filename,
            overwrite=True,
        ).get_frame(num)
