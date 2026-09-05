import os
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class Neo4jConnection:
    def __init__(self):
        self._uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self._user = os.getenv("NEO4J_USER", "neo4j")
        self._password = os.getenv("NEO4J_PASSWORD", "password")
        self._driver = None
        try:
            self.connect()
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")

    def connect(self):
        if not self._driver:
            self._driver = GraphDatabase.driver(
                self._uri, auth=(self._user, self._password)
            )

    def close(self):
        if self._driver:
            self._driver.close()

    def query(self, query, parameters=None, db=None):
        assert self._driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self._driver.session(database=db) if db else self._driver.session()
            response = list(session.run(query, parameters))
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise e
        finally:
            if session:
                session.close()
        return response

neo4j_conn = Neo4jConnection()
