import requests
from .config import Config
from .logger import Logger
from src.dedup import Deduplicator
from src.whisper_client import WhisperClient
from src.whatsapp_media import WhatsAppMediaClient

class WhatsAppManager:
    def __init__(self):
        self.config = Config.load()
        self.logger = Logger(self.config.LOG_LEVEL)
        self.timeout = self.config.TIMEOUT_SECONDS
        self.sentimetor_url = self.config.SENTIMETOR_PROXY_URL
        self.whisper_url = self.config.WHISPER_SERVER_URL
        self.dedup = Deduplicator()
        self.whisper_client = WhisperClient(self.whisper_url, timeout=self.timeout, logger=self.logger)
        self.media_client = WhatsAppMediaClient(
            getattr(self.config, 'WA_WABA_TOKEN', None),
            timeout=self.timeout,
            logger=self.logger
        )

    def handle_message(self, data):
        # Extract message ID for deduplication
        msg_id = self._extract_message_id(data)
        if msg_id and self.dedup.is_duplicate(msg_id):
            self.logger.info(f"Duplicate message detected: {msg_id}, skipping.")
            return {"status": "duplicate"}
        if msg_id:
            self.dedup.mark_processed(msg_id)

        # Extract phone number and message type
        user_id = self._extract_user_id(data)
        msg_type, message = self._extract_message(data)
        self.logger.info(f"[RECEIVED from WhatsApp] {msg_type} message from {user_id}: {message}")
        if msg_type == "text":
            return self._handle_text(user_id, message)
        elif msg_type == "audio":
            return self._handle_audio(user_id, message)
        elif msg_type == "image":
            return self._handle_image(user_id, message)
        else:
            self.logger.info("Unsupported message type")
            return None

    def _extract_message_id(self, data):
        # Extract message id from nested WhatsApp webhook structure
        try:
            return data['entry'][0]['changes'][0]['value']['messages'][0]['id']
        except (KeyError, IndexError, TypeError):
            return None

    # Deduplication logic moved to Deduplicator class

    def _extract_user_id(self, data):
        # Extract user_id from nested WhatsApp webhook structure
        try:
            return data['entry'][0]['changes'][0]['value']['messages'][0]['from']
        except (KeyError, IndexError, TypeError):
            return None

    def _extract_message(self, data):
        # Extract message type and content from nested WhatsApp webhook structure
        try:
            msg = data['entry'][0]['changes'][0]['value']['messages'][0]
            msg_type = msg.get('type')
            if msg_type == 'text':
                return 'text', msg['text']['body']
            elif msg_type == 'audio':
                return 'audio', msg['audio']
            elif msg_type == 'image':
                return 'image', msg['image']
            else:
                return msg_type, None
        except (KeyError, IndexError, TypeError):
            return None, None

    def _handle_text(self, user_id, message):
        payload = {"user_id": user_id, "message": message}
        self.logger.debug(f"[SEND to sentimetor] URL: {self.sentimetor_url}, Payload: {payload}")
        resp = requests.post(self.sentimetor_url, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        reply = resp.json().get("message")
        self.logger.debug(f"[REPLY from sentimetor] {reply}")
        return self._assemble_reply(user_id, reply)

    def _handle_audio(self, user_id, audio_data):
        # Use WhatsAppMediaClient to download audio, then WhisperClient to transcribe
        media_id = audio_data.get('id') if isinstance(audio_data, dict) else None
        if not media_id:
            self.logger.info("No media ID found in audio message.")
            return self._handle_text(user_id, None)
        audio_bytes = self.media_client.download_media(media_id)
        if not audio_bytes:
            return self._handle_text(user_id, None)
        text = self.whisper_client.transcribe(audio_bytes)
        return self._handle_text(user_id, text)

    def _handle_image(self, user_id, image_data):
        # Placeholder for future image support
        self.logger.info("Image support not implemented yet.")
        return None

    def _assemble_reply(self, user_id, message):
        # Send reply to WhatsApp using Cloud API
        phone_id = getattr(self.config, 'WA_WABA_PHONE_ID', None)
        token = getattr(self.config, 'WA_WABA_TOKEN', None)
        if not phone_id or not token:
            self.logger.info("WA_WABA_PHONE_ID or WA_WABA_TOKEN not set in config. Skipping WhatsApp reply.")
            return {"to": user_id, "text": message}

        url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": user_id,
            "type": "text",
            "text": {"body": message}
        }
        self.logger.debug(f"[SEND to WhatsApp] URL: {url}, Payload: {payload}")
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            self.logger.info(f"[REPLY sent to WhatsApp user {user_id}]")
        except Exception as e:
            self.logger.info(f"Failed to send reply to WhatsApp: {e}")
        # Return the payload for logging/testing
        return {"to": user_id, "text": message}
