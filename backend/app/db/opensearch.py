"""OpenSearch client configuration"""

from opensearchpy import OpenSearch
from app.core.config import settings


def get_opensearch_client() -> OpenSearch:
    """
    Get OpenSearch client instance

    Returns:
        OpenSearch client
    """
    client = OpenSearch(
        hosts=[{"host": settings.OPENSEARCH_HOST, "port": settings.OPENSEARCH_PORT}],
        http_auth=(settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD),
        use_ssl=False,
        verify_certs=False,
        ssl_show_warn=False,
    )

    return client


# Global client instance
opensearch_client = get_opensearch_client()
