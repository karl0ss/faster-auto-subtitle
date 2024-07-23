import argparse
from faster_whisper import available_models
from utils.constants import LANGUAGE_CODES
from main import process
from utils.convert import str2bool, str2timeinterval


def main():
    """
    Main entry point for the script.

    Parses command line arguments, processes the inputs using the specified options,
    and performs transcription or translation based on the specified task.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--model",
        default="small",
        choices=available_models(),
        help="name of the Whisper model to use",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="auto",
        choices=["cpu", "cuda", "auto"],
        help='Device to use for computation ("cpu", "cuda", "auto")',
    )
    # parser.add_argument(
    #     "--compute_type",
    #     type=str,
    #     default="default",
    #     choices=[
    #         "int8",
    #         "int8_float32",
    #         "int8_float16",
    #         "int8_bfloat16",
    #         "int16",
    #         "float16",
    #         "bfloat16",
    #         "float32",
    #     ],
    #     help="Type to use for computation. \
    #                           See https://opennmt.net/CTranslate2/quantization.html.",
    # )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Process a single file"
    )
    parser.add_argument(
        "--folder",
        type=str,
        default=None,
        help="Process all videos in folder"
    )
    parser.add_argument(
        "--show",
        type=str,
        default=None,
        help="whether to perform X->X speech recognition ('transcribe') \
                              or X->English translation ('translate')",
    )
    parser.add_argument(
        "--language",
        type=str,
        default="auto",
        choices=LANGUAGE_CODES,
        help="What is the origin language of the video? \
                              If unset, it is detected automatically.",
    )
    parser.add_argument(
        "--backend",
        type=str,
        default="whisper",
        choices=["whisper", "faster_whisper"],
    )
    args = parser.parse_args().__dict__

    process(args)


if __name__ == "__main__":
    main()
