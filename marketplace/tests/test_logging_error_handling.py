"""Tests for error handling in logging module."""

import pytest
import logging
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.shared.infrastructure.logging import (
    setup_logging,
    get_logger,
    configure_file_handler,
    configure_console_handler,
    setup_log_rotation,
)


class TestLoggingErrorHandling:
    """Test error handling scenarios in logging module."""

    @pytest.fixture
    def temp_log_dir(self, tmp_path):
        """Create temporary log directory."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        return log_dir

    def test_setup_logging_inaccessible_log_file(self, temp_log_dir):
        """Test setting up logging with inaccessible log file."""
        # Arrange
        log_file = temp_log_dir / "inaccessible.log"
        
        # Make directory read-only
        os.chmod(temp_log_dir, 0o444)
        
        # Act & Assert
        with pytest.raises(PermissionError):
            setup_logging(log_file=str(log_file))

    def test_setup_logging_full_disk(self, temp_log_dir):
        """Test setting up logging when disk is full."""
        # Arrange
        log_file = temp_log_dir / "test.log"
        
        # Mock disk space check to simulate full disk
        with patch('shutil.disk_usage') as mock_disk_usage:
            mock_disk_usage.return_value = (0, 0, 0)  # No free space
            
            # Act & Assert
            with pytest.raises(OSError, match="Insufficient disk space"):
                setup_logging(log_file=str(log_file))

    def test_setup_logging_invalid_log_level(self):
        """Test setting up logging with invalid log level."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid log level"):
            setup_logging(log_level="INVALID_LEVEL")

    def test_setup_logging_invalid_format(self):
        """Test setting up logging with invalid format."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid log format"):
            setup_logging(log_format="INVALID_FORMAT")

    def test_configure_file_handler_invalid_path(self):
        """Test configuring file handler with invalid path."""
        # Arrange
        invalid_path = "/invalid/path/to/log/file.log"
        
        # Act & Assert
        with pytest.raises(OSError, match="Cannot create log file"):
            configure_file_handler(invalid_path)

    def test_configure_file_handler_permission_denied(self, temp_log_dir):
        """Test configuring file handler with permission denied."""
        # Arrange
        log_file = temp_log_dir / "test.log"
        
        # Make directory read-only
        os.chmod(temp_log_dir, 0o444)
        
        # Act & Assert
        with pytest.raises(PermissionError):
            configure_file_handler(str(log_file))

    def test_configure_file_handler_unicode_error(self, temp_log_dir):
        """Test configuring file handler with Unicode error in filename."""
        # Arrange
        unicode_filename = "test\u0000file.log"  # Null character in filename
        log_file = temp_log_dir / unicode_filename
        
        # Act & Assert
        with pytest.raises(OSError, match="Invalid filename"):
            configure_file_handler(str(log_file))

    def test_configure_console_handler_encoding_error(self):
        """Test configuring console handler with encoding error."""
        # Arrange
        with patch('sys.stdout') as mock_stdout:
            mock_stdout.encoding = 'ascii'
            
            # Act & Assert
            with pytest.raises(UnicodeEncodeError):
                configure_console_handler()

    def test_setup_log_rotation_invalid_max_bytes(self):
        """Test setting up log rotation with invalid max bytes."""
        # Act & Assert
        with pytest.raises(ValueError, match="max_bytes must be positive"):
            setup_log_rotation(max_bytes=0)

    def test_setup_log_rotation_invalid_backup_count(self):
        """Test setting up log rotation with invalid backup count."""
        # Act & Assert
        with pytest.raises(ValueError, match="backup_count must be non-negative"):
            setup_log_rotation(backup_count=-1)

    def test_setup_log_rotation_invalid_rotation_when(self):
        """Test setting up log rotation with invalid rotation when."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid rotation_when"):
            setup_log_rotation(rotation_when="INVALID")

    def test_get_logger_invalid_name(self):
        """Test getting logger with invalid name."""
        # Act & Assert
        with pytest.raises(ValueError, match="Logger name cannot be empty"):
            get_logger("")

    def test_get_logger_none_name(self):
        """Test getting logger with None name."""
        # Act & Assert
        with pytest.raises(ValueError, match="Logger name cannot be None"):
            get_logger(None)

    def test_setup_logging_rotation_error(self, temp_log_dir):
        """Test setting up logging with rotation error."""
        # Arrange
        log_file = temp_log_dir / "test.log"
        
        # Mock RotatingFileHandler to raise error
        with patch('logging.handlers.RotatingFileHandler') as mock_handler:
            mock_handler.side_effect = OSError("Rotation failed")
            
            # Act & Assert
            with pytest.raises(OSError, match="Rotation failed"):
                setup_logging(log_file=str(log_file), enable_rotation=True)

    def test_setup_logging_handler_creation_error(self, temp_log_dir):
        """Test setting up logging with handler creation error."""
        # Arrange
        log_file = temp_log_dir / "test.log"
        
        # Mock FileHandler to raise error
        with patch('logging.FileHandler') as mock_handler:
            mock_handler.side_effect = OSError("Handler creation failed")
            
            # Act & Assert
            with pytest.raises(OSError, match="Handler creation failed"):
                setup_logging(log_file=str(log_file))

    def test_setup_logging_formatter_error(self):
        """Test setting up logging with formatter error."""
        # Arrange
        with patch('logging.Formatter') as mock_formatter:
            mock_formatter.side_effect = ValueError("Invalid format string")
            
            # Act & Assert
            with pytest.raises(ValueError, match="Invalid format string"):
                setup_logging(log_format="%invalid_format%")

    def test_setup_logging_level_setting_error(self):
        """Test setting up logging with level setting error."""
        # Arrange
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_logger.setLevel.side_effect = ValueError("Invalid level")
            mock_get_logger.return_value = mock_logger
            
            # Act & Assert
            with pytest.raises(ValueError, match="Invalid level"):
                setup_logging(log_level="DEBUG")

    def test_setup_logging_handler_add_error(self):
        """Test setting up logging with handler add error."""
        # Arrange
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_logger.addHandler.side_effect = RuntimeError("Handler add failed")
            mock_get_logger.return_value = mock_logger
            
            # Act & Assert
            with pytest.raises(RuntimeError, match="Handler add failed"):
                setup_logging()

    def test_setup_logging_filter_error(self):
        """Test setting up logging with filter error."""
        # Arrange
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_logger.addFilter.side_effect = RuntimeError("Filter add failed")
            mock_get_logger.return_value = mock_logger
            
            # Act & Assert
            with pytest.raises(RuntimeError, match="Filter add failed"):
                setup_logging()

    def test_setup_logging_propagate_error(self):
        """Test setting up logging with propagate setting error."""
        # Arrange
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_logger.propagate = False
            mock_logger.__setattr__ = Mock(side_effect=AttributeError("Cannot set propagate"))
            mock_get_logger.return_value = mock_logger
            
            # Act & Assert
            with pytest.raises(AttributeError, match="Cannot set propagate"):
                setup_logging()

    def test_setup_logging_unicode_format_error(self):
        """Test setting up logging with Unicode format error."""
        # Arrange
        unicode_format = "%(message)s\u0000"  # Null character in format
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid format string"):
            setup_logging(log_format=unicode_format)

    def test_setup_logging_date_format_error(self):
        """Test setting up logging with date format error."""
        # Arrange
        invalid_date_format = "%Y-%m-%d %H:%M:%S\u0000"  # Null character in date format
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid date format"):
            setup_logging(date_format=invalid_date_format)

    def test_setup_logging_encoding_error(self, temp_log_dir):
        """Test setting up logging with encoding error."""
        # Arrange
        log_file = temp_log_dir / "test.log"
        
        # Mock open to raise encoding error
        with patch('builtins.open') as mock_open:
            mock_open.side_effect = UnicodeEncodeError("utf-8", "test", 0, 1, "encoding error")
            
            # Act & Assert
            with pytest.raises(UnicodeEncodeError):
                setup_logging(log_file=str(log_file))

    def test_setup_logging_memory_error(self):
        """Test setting up logging with memory error."""
        # Arrange
        with patch('logging.getLogger') as mock_get_logger:
            mock_get_logger.side_effect = MemoryError("Out of memory")
            
            # Act & Assert
            with pytest.raises(MemoryError, match="Out of memory"):
                setup_logging()

    def test_setup_logging_threading_error(self):
        """Test setting up logging with threading error."""
        # Arrange
        with patch('threading.Lock') as mock_lock:
            mock_lock.side_effect = RuntimeError("Threading error")
            
            # Act & Assert
            with pytest.raises(RuntimeError, match="Threading error"):
                setup_logging()

    def test_setup_logging_configuration_error(self):
        """Test setting up logging with configuration error."""
        # Arrange
        with patch('logging.config.dictConfig') as mock_dict_config:
            mock_dict_config.side_effect = ValueError("Configuration error")
            
            # Act & Assert
            with pytest.raises(ValueError, match="Configuration error"):
                setup_logging(use_dict_config=True)

    def test_setup_logging_environment_error(self):
        """Test setting up logging with environment error."""
        # Arrange
        with patch('os.environ.get') as mock_environ:
            mock_environ.side_effect = OSError("Environment error")
            
            # Act & Assert
            with pytest.raises(OSError, match="Environment error"):
                setup_logging()

    def test_setup_logging_signal_error(self):
        """Test setting up logging with signal error."""
        # Arrange
        with patch('signal.signal') as mock_signal:
            mock_signal.side_effect = OSError("Signal error")
            
            # Act & Assert
            with pytest.raises(OSError, match="Signal error"):
                setup_logging(enable_signal_handling=True) 