import os
import warnings
import tempfile
import time
from utils.files import filename, write_srt
from utils.ffmpeg import get_audio, add_subtitles_to_mp4
from utils.bazarr import get_wanted_episodes, get_episode_details, sync_series
from utils.sonarr import update_show_in_sonarr
from utils.faster_whisper import WhisperAI as fasterWhisperAI
from utils.whisper import WhisperAI
from utils.decorator import measure_time



def folder_flow(folder, model_args, args, backend):
        print(f"Processing {folder}")
        files = os.listdir(folder)
        for file in files:
            print(f"processing {file}")
            path = folder+file
            try:
                audios = get_audio([path], 0, None)
                subtitles = get_subtitles(audios, tempfile.gettempdir(), model_args, args, backend)

                add_subtitles_to_mp4(subtitles)
                time.sleep(5)
            except Exception as ex:
                print(f"skipping file due to - {ex}")

def file_flow(show, model_args, args, backend):
        print(f"Processing {show}")
        try:
            audios = get_audio([show], 0, None)
            subtitles = get_subtitles(audios, tempfile.gettempdir(), model_args, args, backend)

            add_subtitles_to_mp4(subtitles)
            time.sleep(5)
        except Exception as ex:
            print(f"skipping file due to - {ex}")

def bazzar_flow(show, model_args, args, backend):
    list_of_episodes_needing_subtitles = get_wanted_episodes(show)
    print(
        f"Found {list_of_episodes_needing_subtitles['total']} episodes needing subtitles."
    )
    for episode in list_of_episodes_needing_subtitles["data"]:
        print(f"Processing {episode['seriesTitle']} - {episode['episode_number']}")
        episode_data = get_episode_details(episode["sonarrEpisodeId"])
        try:
            audios = get_audio([episode_data["path"]], 0, None)
            subtitles = get_subtitles(audios, tempfile.gettempdir(), model_args, args, backend)

            add_subtitles_to_mp4(subtitles)
            update_show_in_sonarr(episode["sonarrSeriesId"])
            time.sleep(5)
            sync_series()
        except Exception as ex:
            print(f"skipping file due to - {ex}")


@measure_time
def get_subtitles(
    audio_paths: list, output_dir: str, model_args: dict, transcribe_args: dict, backend: str
):
    if backend == 'whisper':
        model = WhisperAI(model_args, transcribe_args)
    else:
        model = fasterWhisperAI(model_args, transcribe_args)
    subtitles_path = {}

    for path, audio_path in audio_paths.items():
        print(f"Generating subtitles for {filename(path)}... This might take a while.")
        srt_path = os.path.join(output_dir, f"{filename(path)}.srt")

        segments = model.transcribe(audio_path)

        with open(srt_path, "w", encoding="utf-8") as srt:
            write_srt(segments, file=srt)

        subtitles_path[path] = srt_path

    return subtitles_path


def process(args: dict):

    model_name: str = args.pop("model")
    language: str = args.pop("language")
    show: str = args.pop("show")
    file: str = args.pop("file")
    folder: str = args.pop("folder")
    backend: str = args.pop("backend")

    if model_name.endswith(".en"):
        warnings.warn(
            f"{model_name} is an English-only model, forcing English detection."
        )
        args["language"] = "en"
    # if translate task used and language argument is set, then use it
    elif language != "auto":
        args["language"] = language

    model_args = {}
    model_args["device"] = args.pop("device")

    if file:
        file_flow(file, model_args, args, backend)
    elif folder:
        folder_flow(folder, model_args, args, backend)
    else:
        bazzar_flow(show, model_args, args, backend)
