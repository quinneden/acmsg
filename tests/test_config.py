import os
import pytest
import yaml
from acmsg.config import Config

@pytest.fixture
def temp_home(tmp_path):
    original_home = os.environ.get('HOME')
    os.environ['HOME'] = str(tmp_path)
    yield tmp_path
    if original_home:
        os.environ['HOME'] = original_home

def test_config_initialization(temp_home):
    config = Config()
    assert os.path.exists(f"{temp_home}/.config/acmsg/config.yaml")

def test_set_and_get_param(temp_home):
    config = Config()
    test_token = "test-token-123"
    config.set_param('api_token', test_token)
    assert config.get_param('api_token') == test_token

def test_default_model_value(temp_home):
    config = Config()
    assert config.get_param('model') == "deepseek/deepseek-r1:free"
