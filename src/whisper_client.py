import requests

class WhisperClient:
    def __init__(self, url, timeout=120, logger=None):
        self.url = url
        self.timeout = timeout
        self.logger = logger

    def transcribe(self, audio_data):
        # Send as ('voice.ogg', audio_data, 'audio/ogg') for FastAPI Whisper servers
        files = {"file": ("voice.ogg", audio_data, "audio/ogg")}
        data = {"beam_size": "5"}
        if self.logger:
            self.logger.debug(f"[SEND to Whisper] URL: {self.url}, Files: {list(files.keys())}, Data: {data}")
        try:
            resp = requests.post(self.url, files=files, data=data, timeout=self.timeout)
            resp.raise_for_status()
            text = resp.json().get("text")
            if self.logger:
                self.logger.debug(f"[REPLY from Whisper] {text}")
            return text
        except Exception as e:
            if self.logger:
                self.logger.info(f"Failed to transcribe audio with Whisper: {e}")
            return None
