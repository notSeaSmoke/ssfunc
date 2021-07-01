import vapoursynth as vs
import random
from math import floor, ceil

core = vs.core


def lazylist(
    clip: vs.VideoNode,
    dark_frames: int = 8,
    light_frames: int = 4,
    seed: int = 20202020,
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

    stats = clip.std.PlaneStats()
    for i, f in enumerate(stats.frames()):
        print(f"Checking Frames: {i}/{stats.num_frames} frames", end="\r")
        avg = f.props["PlaneStatsDiff"]
        if 0.062746 <= avg <= 0.380000:
            dark.append(i)
        elif 0.450000 <= avg <= 0.800000:
            light.append(i)

    if len(dark) > dark_frames:
        random.seed(seed)
        dark = random.sample(dark, dark_frames)

    if len(light) > light_frames:
        random.seed(seed)
        light = random.sample(light, light_frames)

    return dark + light


def get_episode_number(infile: str = None, zfill: int = 2, final: int = None):
    """
    Extract episode number from file name.

    :param path:    Path to the episode, in the form of a string
    :param zfill:   Number of digits in output
    :param final:   Last episode number of the show
    :return:        Episode number
    :rtype:         string

    """
    import re
    from __init__ import EpisodeNotFound

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



def scale(value, peak):
    return cround(value * peak / 255)
