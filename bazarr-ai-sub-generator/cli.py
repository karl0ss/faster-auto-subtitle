import argparse
from faster_whisper import available_models
from utils.constants import LANGUAGE_CODES
from main import process

def main():
    """
    Main entry point for the script.

    Parses command line arguments, processes the inputs using the specified options,
    and performs transcription or translation based on the specified task.
    """
    # Create an ArgumentParser object with a specific formatter for default values
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Add argument for selecting the Whisper model
    parser.add_argument(
        "--model",
        default="small",
        choices=available_models(),
        help="name of the Whisper model to use",
    )
    
    # Add argument for specifying the device to use (CPU, CUDA, or auto-detect)
    parser.add_argument(
        "--device",
        type=str,
        default="auto",
        choices=["cpu", "cuda", "auto"],
        help='Device to use for computation ("cpu", "cuda", "auto")',
    )
    
    # Add argument for processing a single file
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Process a single file"
    )
    
    # Add argument for processing all videos in a folder
    parser.add_argument(
        "--folder",
        type=str,
        default=None,
        help="Process all videos in folder"
    )
    
    # Add argument for specifying the task: transcribe or translate
    parser.add_argument(
        "--show",
        type=str,
        default=None,
        help="whether to perform X->X speech recognition ('transcribe') \
                              or X->English translation ('translate')",
    )
    
    # Add argument for setting the origin language of the video, with auto-detection as default
    parser.add_argument(
        "--language",
        type=str,
        default="auto",
        choices=LANGUAGE_CODES,
        help="What is the origin language of the video? \
                              If unset, it is detected automatically.",
    )
    
    # Add argument for selecting the backend: whisper or faster_whisper
    parser.add_argument(
        "--backend",
        type=str,
        default="whisper",
        choices=["whisper", "faster_whisper"],
    )
    
    # Parse the command line arguments into a dictionary
    args = parser.parse_args().__dict__
    
    # Call the process function with the parsed arguments
    process(args)

if __name__ == "__main__":
    main()
