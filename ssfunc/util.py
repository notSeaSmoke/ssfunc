import vapoursynth as vs
import random
from typing import Union, List, Tuple
from functools import partial
from lvsfunc.render import clip_async_render

core = vs.core


def lazylist(
    clip: vs.VideoNode,
    dark_frames: int = 8,
    light_frames: int = 4,
    seed: int = 20202020,
    diff_thr: int = 15,
):
    """
    A function for generating a list of frames for comparison purposes.
    Works by running `core.std.PlaneStats()` on the input clip,
    iterating over all frames, and sorting all frames into 2 lists
    based on the PlaneStatsAverage value of the frame.
    Randomly picks frames from both lists, 8 from `dark` and 4
    from `light` by default.

    :param clip:          Input clip
    :param dark_frame:    Number of dark frames
    :param light_frame:   Number of light frames
    :param seed:          seed for `random.sample()`
    :return:              List of dark and light frames
    """
    dark = []
    light = []

    def checkclip(n, f, clip):

        avg = f.props["PlaneStatsAverage"]

        if 0.062746 <= avg <= 0.380000:
            dark.append(n)

        elif 0.450000 <= avg <= 0.800000:
            light.append(n)

        return clip

    s_clip = clip.std.PlaneStats()

    eval_frames = core.std.FrameEval(
        clip, partial(checkclip, clip=s_clip), prop_src=s_clip
    )
    clip_async_render(eval_frames, progress="Evaluating Clip: ")

    dark.sort()
    light.sort()

    dark_dedupe = [dark[0]]
    light_dedupe = [light[0]]

    thr = round(clip.fps_num / clip.fps_den * diff_thr)
    lastvald = dark[0]
    lastvall = light[0]

    for i in range(1, len(dark)):

        checklist = dark[0:i]
        x = dark[i]

        for y in checklist:
            if x >= y + thr and x >= lastvald + thr:
                dark_dedupe.append(x)
                lastvald = x
                break

    for i in range(1, len(light)):

        checklist = light[0:i]
        x = light[i]

        for y in checklist:
            if x >= y + thr and x >= lastvall + thr:
                light_dedupe.append(x)
                lastvall = x
                break

    if len(dark_dedupe) > dark_frames:
        random.seed(seed)
        dark_dedupe = random.sample(dark_dedupe, dark_frames)

    if len(light_dedupe) > light_frames:
        random.seed(seed)
        light_dedupe = random.sample(light_dedupe, light_frames)

    return dark_dedupe + light_dedupe


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


