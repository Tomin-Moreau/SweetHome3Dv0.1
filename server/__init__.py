import pytest
from .authenticator import Authenticator
from .database import Database
from .database_thread import DatabaseThread
from .parser import Parser
from .search_engine import SearchEngine
from .server import Server

@pytest.fixture(scope='module', autouse=True)
def setup_module():
    pass