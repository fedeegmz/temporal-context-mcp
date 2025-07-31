from pathlib import Path
from unittest.mock import MagicMock

import pytest

from temporal_context_mcp.core import Settings


@pytest.fixture
def mock_settings(tmp_path: Path) -> Settings:
    settings = MagicMock(spec=Settings)
    settings.data_dir = str(tmp_path)
    settings.contexts_file_name = "context.json"
    settings.recommendations_file_name = "recommendations.json"
    return settings
