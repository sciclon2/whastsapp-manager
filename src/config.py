import importlib.util
import os

class Config:
    _cache = None

    @classmethod
    def load(cls):
        if cls._cache is not None:
            return cls._cache
        config_path = os.path.join(os.path.dirname(__file__), '../configs/whatsapp-manager.py')
        spec = importlib.util.spec_from_file_location("whatsapp_manager_config", config_path)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        cls._cache = config
        return config
