import vapoursynth as vs
import random
from math import floor, ceil

core = vs.core


def lazylist(clip: vs.VideoNode) -> vs.VideoNode:
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

    if len(dark) > 8:
        random.seed(20202020)
        dark = random.sample(dark, 8)

    if len(light) > 4:
        random.seed(20202020)
        light = random.sample(light, 4)

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


def cround(x):
    return floor(x + 0.5) if x > 0 else ceil(x - 0.5)


def m4(x):
    return 16 if x < 16 else cround(x / 4) * 4


def scale(value, peak):
    return cround(value * peak / 255)
