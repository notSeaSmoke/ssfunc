import ass
import subdigest
import subprocess
import os


def dump_subs(subsfile: str, subsdata: subdigest.Subtitles):
    """
    Exports subsdata to subsfile manually over using dump_file() to avoid the utf-8 encode warning.
    """
    with open(subsfile, "w", encoding="utf_8_sig") as f:
        for section in subsdata.sections.values():
            f.write("\n".join(section.dump()))
            f.write("\n\n")


def load_subs(subsfile: str):
    """
    Loads up and parses subtitles from subsfile and returns subsdigest object.
    """
    with open(subsfile, encoding="utf_8_sig") as f:
        subsdata = subdigest.Subtitles(ass.parse(f), subsfile)
    return subsdata


def crunchy_unroll(infile: str = None, styles: str = None):

    """
    Restyles Crunchyroll subtitles using an external `styles` file.
    """
    from util import get_episode_number

    if infile.endswith(".ass"):
        print("Processing subtitles.")
    elif infile.endswith(".mkv"):
        print("Demuxing subtitles")
        subprocess.run(["mkvextract", "-q", "tracks", infile, f"2:{infile}.ass"])
        infile += ".ass"
        print("Processing subtitles.")

    subs = load_subs(infile)

    # Crunchyroll bad
    subs.selection_set("style", "Top$")
    subs.modify_field("text", "^", r"{\\an8}")
    subs.modify_field("text", "}{", "")

    subs.selection_set("style", "^Italics")
    subs.modify_field("text", "^", r"{\\i1}")
    subs.modify_field("text", "}{", "")

    subs.selection_set("style", "^Main")
    subs.modify_field("style", "^.*", "Dialogue")

    subs.selection_set("style", "^Flashback")
    subs.modify_field("style", "^.*", "Flashback")

    subs.selection_set("style", "Top$")
    subs.modify_field("style", "^.*", "Alt")

    subs.selection_set("style", "^Italics")
    subs.modify_field("style", "^.*", "Dialogue")

    # nuke \N tags
    subs.modify_field("text", r"\s*{\\i0}\s*\\N\s*{\\i1}\s*", " ")
    subs.modify_field("text", r"\s*\\[Nn]\s*", " ")
    subs.modify_field("text", r"\s*\\[Nn]", " ")
    subs.modify_field("text", r"\\[Nn]\s*", " ")
    subs.modify_field("text", r"\\[Nn]", " ")

    # misc
    subs.modify_field("text", "--", "—")
    subs.use_styles()
    subs.set_script_info("YCbCr Matrix", "TV.709")
    subs.set_script_info("Script Updated By", "SeaSmoke")

    # dump subs to temp file
    ep = get_episode_number(infile)
    temp = f"{ep}_temp.ass"
    dump_subs(temp, subs)

    # Loading video for resampling
    video = infile.replace(".ass", "")

    # Resampling subs using aegisub-cli
    subprocess.run(["aegisub-cli", "--video", video, temp, temp, "tool/resampleres"])

    # Copying styles from `styles` using prass
    subprocess.run(
        [
            "python",
            "-m",
            "prass",
            "copy-styles",
            "--from",
            styles,
            "--to",
            temp,
            "-o",
            temp,
        ]
    )

    # export subs file
    subs = load_subs(temp)
    dump_subs(infile.replace(".ass", "_fixed.ass"), subs)

    # mux subs back into video
    subprocess.run(
        [
            "mkvmerge",
            "-o",
            infile.replace(".ass", "").replace(".mkv", "_fixed.mkv"),
            "-S",
            "-A",
            "--language",
            "0:und",
            video,
            "-D",
            "-S",
            "--language",
            "1:jpn",
            video,
            "-D",
            "-A",
            "--language",
            "0:en",
            "--track-name",
            "0:[Smoke]",
            infile.replace(".ass", "_fixed.ass"),
        ]
    )

    # Removing temporary files
    os.remove(temp)
    os.remove(infile)
    os.remove(infile.replace(".ass", "_fixed.ass"))

    print("Done!")
