import os
import warnings
import tempfile
import time
from utils.files import filename, write_srt
from utils.ffmpeg import get_audio, add_subs_new
from utils.bazarr import get_wanted_episodes, get_episode_details, sync_series
from utils.sonarr import update_show_in_soarr
from utils.whisper import WhisperAI


def process(args: dict):
    model_name: str = args.pop("model")
    output_dir: str = args.pop("output_dir")
    output_srt: bool = args.pop("output_srt")
    srt_only: bool = args.pop("srt_only")
    language: str = args.pop("language")
    sample_interval: str = args.pop("sample_interval")
    audio_channel: str = args.pop('audio_channel')

    os.makedirs(output_dir, exist_ok=True)

    if model_name.endswith(".en"):
        warnings.warn(
            f"{model_name} is an English-only model, forcing English detection.")
        args["language"] = "en"
    # if translate task used and language argument is set, then use it
    elif language != "auto":
        args["language"] = language

    model_args = {}
    model_args["model_size_or_path"] = model_name
    model_args["device"] = args.pop("device")
    model_args["compute_type"] = args.pop("compute_type")
        
    list_of_episodes_needing_subtitles = get_wanted_episodes()
    print(f"Found {list_of_episodes_needing_subtitles['total']} episodes needing subtitles.")
    for episode in list_of_episodes_needing_subtitles['data']:
        print(f"Processing {episode['seriesTitle']} - {episode['episode_number']}")
        episode_data = get_episode_details(episode['sonarrEpisodeId'])
        audios = get_audio([episode_data['path']], audio_channel, sample_interval)
        srt_output_dir = output_dir if output_srt or srt_only else tempfile.gettempdir()
        subtitles = get_subtitles(audios, srt_output_dir, model_args, args)

        if srt_only:
            return

        add_subs_new(subtitles)
        update_show_in_soarr(episode['sonarrSeriesId'])
        time.sleep(5)
        sync_series()
        


def get_subtitles(audio_paths: list, output_dir: str,
                  model_args: dict, transcribe_args: dict):
    model = WhisperAI(model_args, transcribe_args)

    subtitles_path = {}

    for path, audio_path in audio_paths.items():
        print(
            f"Generating subtitles for {filename(path)}... This might take a while."
        )
        srt_path = os.path.join(output_dir, f"{filename(path)}.srt")

        segments = model.transcribe(audio_path)

        with open(srt_path, "w", encoding="utf-8") as srt:
            write_srt(segments, file=srt)

        subtitles_path[path] = srt_path

    return subtitles_path
