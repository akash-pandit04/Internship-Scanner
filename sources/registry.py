import logging
from typing import Dict, Type
from sources.base import BaseSource

logger = logging.getLogger(__name__)

class SourceRegistry:
    _sources: Dict[str, Type[BaseSource]] = {}

    @classmethod
    def register(cls, name: str, source_cls: Type[BaseSource]):
        cls._sources[name] = source_cls

    @classmethod
    def get_sources(cls, global_config: dict) -> Dict[str, BaseSource]:
        """
        Instantiate all enabled sources based on the config.
        """
        instances = {}
        sources_cfg = global_config.get("sources", {})
        
        for name, source_cls in cls._sources.items():
            cfg = sources_cfg.get(name, {})
            if cfg.get("enabled", True):
                # Pass global config for store_max_age_hours access if needed
                cfg_copy = cfg.copy()
                cfg_copy['global'] = global_config 
                try:
                    instances[name] = source_cls(cfg_copy)
                except Exception as e:
                    logger.error(f"Failed to instantiate source {name}: {e}")
        return instances


