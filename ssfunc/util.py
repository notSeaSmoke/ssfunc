import vapoursynth as vs
from typing import Union, List, Tuple, cast


core = vs.core


def get_episode_number(infile: str = None, zfill: int = 2, final: int = None):
    """
    Determine episode number from file path.

    :param path:    Path to the episode, in the form of a string
    :param zfill:   Number of digits in output
    :param final:   Last episode number of the show
    :return:        Episode number
    :rtype:         str

    """
    import re
    from . import EpisodeNotFound

    if infile is None:
        raise TypeError("`get_episode_number` requires a string input")
    partial = re.search(r"(\b|E|_)([0-9]{1,3})(\b|_|v)", infile).group(0)
    episode = re.search(r"([0-9]{1,3})", partial).group(0)

    if final is not None:
        episode_int = int(episode)
        if episode_int <= final:
            return episode.zfill(zfill)
        else:
            raise EpisodeNotFound
    else:
        return episode.zfill(zfill)


def betterround(input: float, base: int = 1):
    """
    Helper function to round input to nearest base.\\
    Can be used for mod2/4/16 rounding.\\
    default behaviour is the same as python's `round()`,
    so it can be used as a `round()` replacement.

    :param input:   Height/Width
    :param base:    integer to round to
    :rtype:         int

    """
    return base * round(input / base)


def peak(clip: vs.VideoNode):
    """
    Function to return peak value of a clip.

    :param clip: input clip
    :rtype: int
    """
    return (1 << clip.format.bits_per_sample) - 1


def scale(value: float, peak: int):
    """
    havsfunc's scale function.

    :param value:   Input to scale
    :param peak:    Peak to scale to
    :rtype:         int

    """
    return betterround(value * peak / 255)


def midval(val=Union[List, List[Tuple]]):
    from statistics import median

    return median(val) if median(val) % 2 == 0 else betterround(median(val))


def get_uv(clip: vs.VideoNode):
    """
    Converts clip to 32 bit float, creates a blank luma clip,
    and returns the UV planes merged with the blank luma.
    Output clip is converted to input format.

    :param clip:    Input clip
    :rtype:         vs.VideoNode
    :returns:       Merge of Chroma planes from input clip

    """

    clip = clip.fmtc.bitdepth(bits=32)
    t_y = core.std.BlankClip(clip, 960, 540)

    return core.std.ShufflePlanes([t_y, clip], planes=[0, 1, 2]).resize.Point(
        format="vs." + clip.format.name
    )


def desync(clipa: vs.VideoNode, clipb: vs.VideoNode, start: int = 0):
    """
    Function to check the `PlaneStatsDiff` value of two clips
    in order to find desync points between the clips.
    Written to help with syncing Wakanim/BiliBili sources
    to Funimation video.

    Clip prints first desync point it finds to stderr, then breaks.
    Sync clips up as it finds desync points and run it again, until
    it runs through the whole clip without breaking. To speed things
    up, you can manually specify a `start` point. For eg. if you've
    fixed desyncs upto frame 8100, set `start=8100`. That'll save time
    since the function won't run on frames which have already been checked.

    :param clipa:   Master clip
    :type clipa:    vs.VideoNode
    :param clipb:   Desynced clip
    :type clipb:    vs.VideNode
    :param start:   Frame to start checking from
    :rtype:         None

    """
    stats = core.std.PlaneStats(clipa, clipb)

    for i in range(start, stats.num_frames):
        print(f"Checking Frames: {i}/{stats.num_frames} frames", end="\r")
        diff = stats.get_frame(i).props["PlaneStatsDiff"]
        if diff > 0.150000:
            print(f"desync detected at >>{i}<<")
            break
