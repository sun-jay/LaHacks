import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import pyaudio
import wave

import threading
import os
import time
import audioop


# class that can start two threads, one that records and one that transcibres

class Transcriber():
    def __init__(self, constant_print = False, verbose = False ,chunk_time=2.5,quiet_threshold=1000, frame_size=8000):
        self.constant_print = constant_print
        self.verbose = verbose
        self.chunk_time = chunk_time

        self.chunk_time = chunk_time
        self.quiet_threshold = quiet_threshold  # RMS threshold to consider a frame as quiet
        self.frame_size = frame_size  # Number of samples per frame
        self.sample_rate = 16000  # Sample rate in Hz


        self.device =  "mps"
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        self.model_id = "distil-whisper/distil-small.en"

        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            self.model_id, torch_dtype=self.torch_dtype, low_cpu_mem_usage=False, use_safetensors=True
        )
        self.model.to(self.device)

        processor = AutoProcessor.from_pretrained(self.model_id)

        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            max_new_tokens=128,
            torch_dtype=self.torch_dtype,
            device=self.device,
        )

        self.full_text = ""

        self.current_command = None

    def record(self, ind, p, stream, seconds, silent_seconds = 0.5):
        frames = []
        # Calculating the number of frames for the minimum recording time and silence time
        min_frames = int(self.sample_rate / self.frame_size * seconds)
        silent_frames_required = int(self.sample_rate / self.frame_size * silent_seconds)

        frame_count = 0
        quiet_frame_count = 0
        min_time_reached = False

        while not min_time_reached or quiet_frame_count < silent_frames_required:
            data = stream.read(self.frame_size, exception_on_overflow=False)
            frames.append(data)
            frame_count += 1

            # Calculate the RMS of this frame
            rms = audioop.rms(data, 2)  # Assuming the format is 16 bits per sample
            if rms < self.quiet_threshold:
                quiet_frame_count += 1
            else:
                quiet_frame_count = 0  # Reset if a loud frame is detected

            # Check if minimum recording time has been met
            if frame_count >= min_frames:
                min_time_reached = True

            # Debug output (optional, can be commented out in production)
            if frame_count % 2 == 0 and self.verbose:
                print(f"Frame {frame_count}: RMS={rms}, Quiet Frames Count={quiet_frame_count}")

        # Save the recorded audio to a file
        audio_file = f"./audios/{ind}.wav"
        wf = wave.open(audio_file, "wb")
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        if self.verbose:
            print(f"Recording saved to {audio_file}. Total frames recorded: {frame_count}")



    def record_thread(self):
        ind = 0
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        while True:
            self.record(ind,p, stream, self.chunk_time)
            ind += 1

    def transcribe_thread(self):
        prev_ind = -1
        while True:
            time.sleep(0.5)

            # temp = self.full_text.lower()
            # if "assistant" in temp:
            #     print("Listening...")

            available_inds = [int(i.split(".")[0]) for i in os.listdir("./audios") if i.split(".")[0].isdigit()]
            # print(available_inds)
            if prev_ind + 1 in available_inds:
                audio_file = "./audios/" + str(prev_ind + 1) + ".wav"
                # audio_file = "./audios/" + "0"+ ".wav"
                result = self.pipe(audio_file)
                # self.full_text += result["text"]
                if self.constant_print:
                    print(result["text"])

                self.full_text += result["text"]

                temp = self.full_text.lower()
                if "assistant" in temp and "over" in temp:
                    # set the current command to the text in between assistant and over
                    self.current_command = temp[temp.index("assistant")+len("assistant"):temp.index("over")]
                    self.full_text = ""


                prev_ind += 1

        # while True:
        #     time.sleep(0.5)
        #     print("bruh")
        #     start = time.time()
        #     print(self.pipe("/Users/sunnyjay/Documents/vscode/Hackathon/LaHacks/Python Interface/audios/0.wav"))
        #     print(time.time()-start)

    def start(self):
        threading.Thread(target=self.record_thread).start()
        threading.Thread(target=self.transcribe_thread).start()   


if __name__ == "__main__":
    # clear ./audios
    transcriber = Transcriber(constant_print=True, quiet_threshold=2000, verbose=True)

    for i in os.listdir("./audios"):
        os.remove("./audios/" + i)
    transcriber.start()

    prev = None
    while True:
        time.sleep(0.5)
        print("Current command:", transcriber.current_command)
        # if prev != transcriber.current_command:
        #     print("Current command:", transcriber.current_command)
        #     prev = transcriber.current_command
        
    # transcriber.record_thread()



    # transcriber.transcribe()


    # while True:
    #     pass

    # res = transcriber.pipe("./audios/0.wav")

    # print(res["text"])  


# p = pyaudio.PyAudio()
# stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
# frames = []
# for i in range(0, int(16000 / 8000 * 5)):
#     data = stream.read(8000)
#     frames.append(data)
# stream.stop_stream()
# stream.close()
# p.terminate()

# print("Processing...")

# audio_file = "./audios/recording.wav"
# wf = wave.open(audio_file, "wb")
# wf.setnchannels(1)
# wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
# wf.setframerate(16000)
# wf.writeframes(b"".join(frames))
# wf.close()
