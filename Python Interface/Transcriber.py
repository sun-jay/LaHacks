import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import pyaudio
import wave

import threading
import os

# class that can start two threads, one that records and one that transcibres

class Transcriber():
    def __init__(self, chunk_time=2.5):
        self.chunk_time = chunk_time


        self.device = "cuda:0" if torch.cuda.is_available() else "mps"
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        self.model_id = "distil-whisper/distil-small.en"

        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            self.model_id, torch_dtype=self.torch_dtype,  use_safetensors=True
        )
        self.model.to(self.device)

        self.processor = AutoProcessor.from_pretrained(self.model_id)

        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            max_new_tokens=128,
            torch_dtype=self.torch_dtype,
            device=self.device,
        )

        self.full_text = ""

        self.current_command = None

    def record(self, ind, stream, seconds):
        frames = []
        for i in range(0, int(16000 / 8000 * seconds)):
            data = stream.read(8000)
            frames.append(data)
        stream.stop_stream()
        stream.close()
        p.terminate()

        audio_file = "./audios/" + ind + ".wav"
        wf = wave.open(audio_file, "wb")
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b"".join(frames))
        wf.close()

    def record_thread(self):
        ind = 0
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        while True:
            print("Say something...")
            self.record(ind, stream, self.chunk_time)
            ind += 1

    def transcribe_thread(self):
        prev_ind = 0
        while True:
            available_inds = [int(i.split(".")[0]) for i in os.listdir("./audios")]



    

device = "cuda:0" if torch.cuda.is_available() else "mps"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model_id = "distil-whisper/distil-small.en"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype,  use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)


pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=128,
    torch_dtype=torch_dtype,
    device=device,
)


print("Say something...")
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
frames = []
for i in range(0, int(16000 / 8000 * 5)):
    data = stream.read(8000)
    frames.append(data)
stream.stop_stream()
stream.close()
p.terminate()

print("Processing...")

audio_file = "./audios/recording.wav"
wf = wave.open(audio_file, "wb")
wf.setnchannels(1)
wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
wf.setframerate(16000)
wf.writeframes(b"".join(frames))
wf.close()


result = pipe("./audios/recording.wav")
print(result["text"])