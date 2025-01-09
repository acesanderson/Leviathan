"""https://huggingface.co/pyannote/speaker-diarization-3.1"""

from pyannote.audio import Pipeline
import os
import torch

MP3_FILE = "processed/dr_visit_12-16-2024.mp3"
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if not HUGGINGFACE_API_KEY:
    print("API KEY not found")

# instantiate the pipeline
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=HUGGINGFACE_API_KEY,
)

pipeline.to(torch.device("cuda"))

# run the pipeline on an audio file
diarization = pipeline(MP3_FILE)

# dump the diarization output to disk using RTTM format
with open("audio.rttm", "w") as rttm:
    diarization.write_rttm(rttm)
