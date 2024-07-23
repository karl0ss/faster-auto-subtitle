import os
import warnings
import tempfile
import time
from typing import List, Dict, Any
from utils.files import filename, write_srt
from utils.ffmpeg import get_audio, add_subtitles_to_mp4
from utils.bazarr import get_wanted_episodes, get_episode_details, sync_series
from utils.sonarr import update_show_in_sonarr
from utils.faster_whisper import WhisperAI as fasterWhisperAI
from utils.whisper import WhisperAI
from utils.decorator import measure_time


def process_audio_and_subtitles(file_path: str, model_args: Dict[str, Any], args: Dict[str, Any], backend: str) -> None:
    """Processes audio extraction and subtitle generation for a given file.

    Args:
        file_path (str): Path to the video file.
        model_args (Dict[str, Any]): Model arguments for subtitle generation.
        args (Dict[str, Any]): Additional arguments for subtitle generation.
        backend (str): Backend to use ('whisper' or 'faster_whisper').

    Returns:
        None
    """
    try:
        audios = get_audio([file_path], 0, None)
        subtitles = get_subtitles(audios, tempfile.gettempdir(), model_args, args, backend)
        add_subtitles_to_mp4(subtitles)
        time.sleep(5)
    except Exception as ex:
        print(f"Skipping file {file_path} due to - {ex}")


def folder_flow(folder: str, model_args: Dict[str, Any], args: Dict[str, Any], backend: str) -> None:
    """Processes all files within a specified folder.

    Args:
        folder (str): Path to the folder containing video files.
        model_args (Dict[str, Any]): Model arguments for subtitle generation.
        args (Dict[str, Any]): Additional arguments for subtitle generation.
        backend (str): Backend to use ('whisper' or 'faster_whisper').

    Returns:
        None
    """
    print(f"Processing folder {folder}")
    files = os.listdir(folder)
    for file in files:
        path = os.path.join(folder, file)
        print(f"Processing file {path}")
        process_audio_and_subtitles(path, model_args, args, backend)


def file_flow(file_path: str, model_args: Dict[str, Any], args: Dict[str, Any], backend: str) -> None:
    """Processes a single specified file.

    Args:
        file_path (str): Path to the video file.
        model_args (Dict[str, Any]): Model arguments for subtitle generation.
        args (Dict[str, Any]): Additional arguments for subtitle generation.
        backend (str): Backend to use ('whisper' or 'faster_whisper').

    Returns:
        None
    """
    print(f"Processing file {file_path}")
    process_audio_and_subtitles(file_path, model_args, args, backend)


def bazzar_flow(show: str, model_args: Dict[str, Any], args: Dict[str, Any], backend: str) -> None:
    """Processes episodes needing subtitles from Bazarr API.

    Args:
        show (str): The show name.
        model_args (Dict[str, Any]): Model arguments for subtitle generation.
        args (Dict[str, Any]): Additional arguments for subtitle generation.
        backend (str): Backend to use ('whisper' or 'faster_whisper').

    Returns:
        None
    """
    list_of_episodes_needing_subtitles = get_wanted_episodes(show)
    print(f"Found {list_of_episodes_needing_subtitles['total']} episodes needing subtitles.")
    for episode in list_of_episodes_needing_subtitles["data"]:
        print(f"Processing {episode['seriesTitle']} - {episode['episode_number']}")
        episode_data = get_episode_details(episode["sonarrEpisodeId"])
        process_audio_and_subtitles(episode_data["path"], model_args, args, backend)
        update_show_in_sonarr(episode["sonarrSeriesId"])
        sync_series()


@measure_time
def get_subtitles(audio_paths: List[str], output_dir: str, model_args: Dict[str, Any], transcribe_args: Dict[str, Any], backend: str) -> Dict[str, str]:
    """Generates subtitles for given audio files using the specified model.

    Args:
        audio_paths (List[str]): List of paths to the audio files.
        output_dir (str): Directory to save the generated subtitle files.
        model_args (Dict[str, Any]): Model arguments for subtitle generation.
        transcribe_args (Dict[str, Any]): Transcription arguments for subtitle generation.
        backend (str): Backend to use ('whisper' or 'faster_whisper').

    Returns:
        Dict[str, str]: A dictionary mapping audio file paths to generated subtitle file paths.
    """
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


def process(args: Dict[str, Any]) -> None:
    """Main entry point to determine which processing flow to use.

    Args:
        args (Dict[str, Any]): Dictionary of arguments including model, language, show, file, folder, and backend.

    Returns:
        None
    """
    model_name: str = args.pop("model")
    language: str = args.pop("language")
    show: str = args.pop("show")
    file: str = args.pop("file")
    folder: str = args.pop("folder")
    backend: str = args.pop("backend")

    if model_name.endswith(".en"):
        warnings.warn(f"{model_name} is an English-only model, forcing English detection.")
        args["language"] = "en"
    elif language != "auto":
        args["language"] = language

    model_args = {"device": args.pop("device")}

    if file:
        file_flow(file, model_args, args, backend)
    elif folder:
        folder_flow(folder, model_args, args, backend)
    else:
        bazzar_flow(show, model_args, args, backend)
