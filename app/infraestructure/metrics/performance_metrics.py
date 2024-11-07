import time
import threading

class PerformanceMetrics:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        if PerformanceMetrics._instance is not None:
            raise Exception("This class is a singleton!")
        self.total_documents = 0
        self.total_processing_time = 0.0
        self.lock = threading.Lock()

    @staticmethod
    def get_instance():
        if PerformanceMetrics._instance is None:
            with PerformanceMetrics._lock:
                if PerformanceMetrics._instance is None:
                    PerformanceMetrics._instance = PerformanceMetrics()
        return PerformanceMetrics._instance

    def start_timer(self):
        return time.time()

    def end_timer(self, start_time):
        return time.time() - start_time

    def record_document(self, processing_time: float):
        with self.lock:
            self.total_documents += 1
            self.total_processing_time += processing_time

    def get_metrics(self) -> dict:
        with self.lock:
            average_time = (self.total_processing_time / self.total_documents) if self.total_documents else 0.0
            return {
                "total_documents_processed": self.total_documents,
                "total_processing_time_seconds": self.total_processing_time,
                "average_processing_time_seconds": average_time
            }