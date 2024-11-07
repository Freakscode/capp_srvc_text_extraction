import time
import threading
from typing import Dict, List, Optional
from statistics import mean, median

class PerformanceMetrics:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        if PerformanceMetrics._instance is not None:
            raise Exception("Esta clase es un singleton!")
        
        self.document_times: Dict[str, float] = {}
        self.document_sizes: Dict[str, int] = {}
        self.document_stats: Dict[str, Dict] = {}
        self.total_documents = 0
        self.total_processing_time = 0.0
        self.lock = threading.Lock()
        self.processing_history: List[float] = []
        self.timers: Dict[str, float] = {}

    def start_timer(self, timer_id: str = "default") -> float:
        self.timers[timer_id] = time.time()
        return self.timers[timer_id]

    def end_timer(self, timer_id: str = "default") -> float:
        start_time = self.timers.pop(timer_id, None)
        if start_time is None:
            raise ValueError(f"No se encontró inicio del temporizador '{timer_id}'.")
        return time.time() - start_time

    def record_document_metrics(self, 
                                document_id: str, 
                                processing_time: float,
                                file_size: int,
                                stats: Optional[Dict] = None):
        with self.lock:
            self.total_documents += 1
            self.total_processing_time += processing_time
            self.processing_history.append(processing_time)
            self.document_times[document_id] = processing_time
            self.document_sizes[document_id] = file_size
            if stats:
                self.document_stats[document_id] = stats

    def get_document_metrics(self, document_id: str) -> Dict:
        with self.lock:
            if document_id not in self.document_times:
                return None
            
            doc_time = self.document_times[document_id]
            doc_size = self.document_sizes.get(document_id, 0)
            doc_stats = self.document_stats.get(document_id, {})
            times = list(self.document_times.values())
            percentile = len([t for t in times if t <= doc_time]) / len(times) * 100
            
            return {
                "document_id": document_id,
                "processing_metrics": {
                    "processing_time_seconds": doc_time,
                    "file_size_bytes": doc_size,
                    "processing_speed_mbps": (doc_size / 1024 / 1024) / doc_time if doc_time > 0 else 0
                },
                "comparison": {
                    "vs_average": doc_time - mean(times),
                    "vs_median": doc_time - median(times),
                    "percentile": percentile
                },
                "document_stats": doc_stats
            }

    def get_global_metrics(self) -> Dict:
        with self.lock:
            times = list(self.document_times.values())
            return {
                "total_documents": self.total_documents,
                "total_processing_time": self.total_processing_time,
                "average_processing_time": mean(times) if times else 0,
                "median_processing_time": median(times) if times else 0,
                "min_processing_time": min(times) if times else 0,
                "max_processing_time": max(times) if times else 0,
                "total_data_processed_mb": sum(self.document_sizes.values()) / 1024 / 1024
            }