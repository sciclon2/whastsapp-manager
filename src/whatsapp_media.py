import requests

class WhatsAppMediaClient:
    def __init__(self, token, timeout=120, logger=None):
        self.token = token
        self.timeout = timeout
        self.logger = logger
        self.api_base = "https://graph.facebook.com/v19.0/"

    def download_media(self, media_id):
        headers = {"Authorization": f"Bearer {self.token}"}
        # Step 1: Get media URL
        media_url_endpoint = f"{self.api_base}{media_id}"
        try:
            resp = requests.get(media_url_endpoint, headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            media_url = resp.json().get('url')
            if not media_url:
                if self.logger:
                    self.logger.info("No media URL found in WhatsApp API response.")
                return None
        except Exception as e:
            if self.logger:
                self.logger.info(f"Failed to get media URL from WhatsApp: {e}")
            return None
        # Step 2: Download the media file
        try:
            audio_resp = requests.get(media_url, headers=headers, timeout=self.timeout)
            audio_resp.raise_for_status()
            return audio_resp.content
        except Exception as e:
            if self.logger:
                self.logger.info(f"Failed to download media file from WhatsApp: {e}")
            return None
