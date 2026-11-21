import logging
import json
from datetime import datetime, timezone
from request_context import request_id_var


class JSONFormatter(logging.Formatter):

    def format(self, record):
        log = {
        "request_id": request_id_var.get(),
        "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
        "level": record.levelname,
        "logger": record.name,
        "event": record.getMessage(),
        "kpi_id": getattr(record, "kpi_id", None),
        "model": getattr(record, "model", None),
        "latency_ms": getattr(record, "latency_ms", None),
        "input_tokens": getattr(record, "input_tokens", None),
        "output_tokens": getattr(record, "output_tokens", None),
        "thinking_tokens": getattr(record, "thinking_tokens", None),
        "total_tokens": getattr(record, "total_tokens", None),
        "http_status": getattr(record, "http_status", None),
        "status": getattr(record, "status", None)
        }

        return json.dumps(log)

def configure_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("google_genai").setLevel(logging.WARNING)
    handler = logging.StreamHandler()
    
    formatter = JSONFormatter()

    handler.setFormatter(formatter)

    root_logger.addHandler(handler)
    
    #return logger.info(json_stream_handler)

    