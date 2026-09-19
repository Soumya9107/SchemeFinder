import os
import json
import logging
import urllib.request
import urllib.error

logger = logging.getLogger("scheme_finder.opensearch")

OPENSEARCH_URL = os.environ.get("OPENSEARCH_URL", "http://localhost:9200")
INDEX_NAME = "government_schemes"

class OpenSearchClient:
    def __init__(self, host=OPENSEARCH_URL):
        self.host = host.rstrip("/")
        self.is_connected = False
        self._check_connection()

    def _check_connection(self):
        """Check if OpenSearch Docker container is reachable."""
        try:
            req = urllib.request.Request(f"{self.host}/", method="GET")
            with urllib.request.urlopen(req, timeout=2) as response:
                if response.status == 200:
                    self.is_connected = True
                    logger.info(f"Connected to OpenSearch at {self.host}")
                    return
        except Exception as e:
            logger.info(f"OpenSearch container not available ({e}). Using local fallback search.")
            self.is_connected = False

    def index_schemes(self, schemes_data):
        """Index scheme documents into OpenSearch if connected."""
        if not self.is_connected:
            return False

        try:
            for scheme in schemes_data:
                doc_id = scheme["id"]
                url = f"{self.host}/{INDEX_NAME}/_doc/{doc_id}"
                data = json.dumps(scheme).encode("utf-8")
                req = urllib.request.Request(
                    url,
                    data=data,
                    headers={"Content-Type": "application/json"},
                    method="PUT"
                )
                with urllib.request.urlopen(req, timeout=3) as resp:
                    pass
            logger.info(f"Successfully indexed {len(schemes_data)} schemes into OpenSearch.")
            return True
        except Exception as e:
            logger.warning(f"Failed to index schemes in OpenSearch: {e}")
            return False

    def search(self, query_text):
        """Search OpenSearch index using match query."""
        if not self.is_connected:
            return None

        try:
            url = f"{self.host}/{INDEX_NAME}/_search"
            payload = {
                "query": {
                    "multi_match": {
                        "query": query_text,
                        "fields": ["name.*^3", "objective.*^2", "category", "benefits.*", "documents"]
                    }
                }
            }
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                hits = result.get("hits", {}).get("hits", [])
                return [hit["_source"] for hit in hits]
        except Exception as e:
            logger.warning(f"OpenSearch query failed: {e}")
            return None
