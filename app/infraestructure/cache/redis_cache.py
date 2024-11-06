from redis import Redis
import json
from typing import Optional, Dict, Any
from datetime import timedelta

class RedisCache:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis = Redis(host=host, port=port, db=db)
        self.default_ttl = timedelta(hours=24)
    
    def cache_document_analysis(
        self, 
        document_id: str, 
        analysis_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Almacena el análisis de un documento en caché"""
        key = f"doc_analysis:{document_id}"
        try:
            self.redis.setex(
                key,
                ttl or self.default_ttl,
                json.dumps(analysis_data)
            )
            return True
        except Exception as e:
            print(f"Error caching document analysis: {e}")
            return False
    
    def get_document_analysis(self, document_id: str) -> Optional[Dict]:
        """Recupera el análisis de un documento de la caché"""
        key = f"doc_analysis:{document_id}"
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return None
    
    def cache_paragraph_info(
        self, 
        document_id: str,
        paragraph_id: str, 
        paragraph_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Almacena información de párrafo individual"""
        key = f"paragraph:{document_id}:{paragraph_id}"
        try:
            self.redis.setex(
                key,
                ttl or self.default_ttl,
                json.dumps(paragraph_data)
            )
            return True
        except Exception as e:
            print(f"Error caching paragraph info: {e}")
            return False