import warnings
import torch
import whisper
from tqdm import tqdm


class WhisperAI:
    """
    Wrapper class for the Whisper speech recognition model with additional functionality.

    This class provides a high-level interface for transcribing audio files using the Whisper
    speech recognition model. It encapsulates the model instantiation and transcription process,
    allowing users to easily transcribe audio files and iterate over the resulting segments.

    Usage:
    ```python
    whisper = WhisperAI(model_args, transcribe_args)

    # Transcribe an audio file and iterate over the segments
    for segment in whisper.transcribe(audio_path):
        # Process each transcription segment
        print(segment)
    ```

    Args:
    - model_args (dict): Arguments to pass to Whisper model initialization
        - model_size (str): The name of the Whisper model to use.
        - device (str): The device to use for computation ("cpu" or "cuda").
    - transcribe_args (dict): Additional arguments to pass to the transcribe method.

    Attributes:
    - model (whisper.Whisper): The underlying Whisper speech recognition model.
    - device (torch.device): The device to use for computation.
    - transcribe_args (dict): Additional arguments used for transcribe method.

    Methods:
    - transcribe(audio_path: str): Transcribes an audio file and yields the resulting segments.
    """

    def __init__(self, model_args: dict, transcribe_args: dict):
        """
        Initializes the WhisperAI instance.

        Args:
        - model_args (dict): Arguments to initialize the Whisper model.
        - transcribe_args (dict): Additional arguments for the transcribe method.
        """
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(device)
        # Set device for computation
        self.device = torch.device(device)
        # Load the Whisper model with the specified size
        self.model = whisper.load_model("base").to(self.device)
        # Store the additional transcription arguments
        self.transcribe_args = transcribe_args

    def transcribe(self, audio_path: str):
        """
        Transcribes the specified audio file and yields the resulting segments.

        Args:
        - audio_path (str): The path to the audio file for transcription.

        Yields:
        - dict: An individual transcription segment.
        """
        # Suppress warnings during transcription
        warnings.filterwarnings("ignore")
        # Load and transcribe the audio file
        result = self.model.transcribe(audio_path, **self.transcribe_args)
        # Restore default warning behavior
        warnings.filterwarnings("default")

        # Calculate the total duration from the segments
        total_duration = max(segment["end"] for segment in result["segments"])

        # Create a progress bar with the total duration of the audio file
        with tqdm(total=total_duration, unit=" seconds") as pbar:
            for segment in result["segments"]:
                # Yield each transcription segment
                yield segment
                # Update the progress bar with the duration of the current segment
                pbar.update(segment["end"] - segment["start"])
            # Ensure the progress bar reaches 100% upon completion
            pbar.update(0)
