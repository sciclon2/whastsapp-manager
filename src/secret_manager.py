import hmac
import hashlib
import importlib.util
import os

class SecretManager:
    _config_cache = None

    @classmethod
    def load_config(cls):
        if cls._config_cache is not None:
            return cls._config_cache
        config_path = os.path.join(os.path.dirname(__file__), '../configs/whatsapp-manager.py')
        spec = importlib.util.spec_from_file_location("whatsapp_manager_config", config_path)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        cls._config_cache = config
        return config

    @classmethod
    def get_app_secret(cls):
        config = cls.load_config()
        return getattr(config, 'WA_APP_SECRET', None)

    @classmethod
    def validate_signature(cls, flask_request, logger=None):
        """
        Validates the signature of a Flask request using the app secret.
        Returns True if valid, False otherwise.
        Optionally logs reasons for failure if logger is provided.
        """
        app_secret = cls.get_app_secret()
        signature = flask_request.headers.get('X-Hub-Signature-256')
        payload = flask_request.get_data()
        if not app_secret or not signature:
            if logger:
                logger.info("Missing app secret or signature header.")
            return False
        expected_signature = 'sha256=' + hmac.new(app_secret.encode(), payload, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_signature):
            if logger:
                logger.info("Invalid signature.")
            return False
        return True
