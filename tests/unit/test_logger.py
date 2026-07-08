import io
import logging

from src.core.logger import get_logger, initialize_logging


def test_get_logger_returns_configured_logger() -> None:
    initialize_logging()
    logger = get_logger("test.module")

    assert isinstance(logger, logging.Logger)
    assert logger.name == "test.module"
    assert logger.level == logging.INFO
    assert logger.propagate is False
    assert len(logger.handlers) == 1
    assert logger.handlers[0].level == logging.INFO
    assert logger.handlers[0].formatter is not None


def test_logger_respects_logging_config_and_emits_output(caplog) -> None:
    initialize_logging()
    logger = get_logger("test.module")

    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
    logger.addHandler(handler)

    logger.info("configured output")

    assert "INFO:test.module:configured output" in stream.getvalue()
    assert logger.level == logging.INFO
