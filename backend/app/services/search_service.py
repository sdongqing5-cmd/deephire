"""Candidate search service using OpenSearch"""

from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from opensearchpy import OpenSearch
from opensearchpy.exceptions import NotFoundError

from app.db.opensearch import opensearch_client


class CandidateSearchService:
    """Candidate search service with hybrid search capabilities"""

    def __init__(self):
        self.client: OpenSearch = opensearch_client
        self.index_name = "candidates"
        self.embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        self.embedding_dim = 384

    def create_index(self):
        """
        Create candidates index with mappings for text and vector fields
        """
        index_body = {
            "settings": {
                "index": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "knn": True,
                    "knn.algo_param.ef_search": 100,
                },
                "analysis": {
                    "analyzer": {
                        "ik_analyzer": {
                            "type": "standard"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "text", "analyzer": "ik_analyzer"},
                    "email": {"type": "keyword"},
                    "phone": {"type": "keyword"},
                    "current_company": {"type": "text", "analyzer": "ik_analyzer"},
                    "current_title": {"type": "text", "analyzer": "ik_analyzer"},
                    "years_of_experience": {"type": "integer"},
                    "location": {"type": "keyword"},
                    "status": {"type": "keyword"},
                    "tags": {"type": "keyword"},
                    "skills": {"type": "text", "analyzer": "ik_analyzer"},
                    "summary": {"type": "text", "analyzer": "ik_analyzer"},
                    "full_text": {"type": "text", "analyzer": "ik_analyzer"},
                    "embedding": {
                        "type": "knn_vector",
                        "dimension": self.embedding_dim,
                        "method": {
                            "name": "hnsw",
                            "space_type": "cosinesimil",
                            "engine": "nmslib",
                        }
                    },
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                }
            }
        }

        try:
            # Delete index if exists
            if self.client.indices.exists(index=self.index_name):
                self.client.indices.delete(index=self.index_name)

            # Create new index
            self.client.indices.create(index=self.index_name, body=index_body)
            print(f"✓ Created index: {self.index_name}")

        except Exception as e:
            print(f"✗ Failed to create index: {e}")
            raise

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def index_candidate(self, candidate_data: Dict[str, Any]):
        """
        Index a candidate document

        Args:
            candidate_data: Candidate data dictionary
        """
        # Build full text for embedding
        full_text_parts = [
            candidate_data.get("name", ""),
            candidate_data.get("current_company", ""),
            candidate_data.get("current_title", ""),
            candidate_data.get("location", ""),
            " ".join(candidate_data.get("tags", [])),
            candidate_data.get("summary", ""),
        ]
        full_text = " ".join(filter(None, full_text_parts))

        # Generate embedding
        embedding = self.generate_embedding(full_text)

        # Prepare document
        doc = {
            "id": candidate_data.get("id"),
            "name": candidate_data.get("name"),
            "email": candidate_data.get("email"),
            "phone": candidate_data.get("phone"),
            "current_company": candidate_data.get("current_company"),
            "current_title": candidate_data.get("current_title"),
            "years_of_experience": candidate_data.get("years_of_experience"),
            "location": candidate_data.get("location"),
            "status": candidate_data.get("status"),
            "tags": candidate_data.get("tags", []),
            "skills": " ".join(candidate_data.get("tags", [])),
            "summary": candidate_data.get("summary", ""),
            "full_text": full_text,
            "embedding": embedding,
            "created_at": candidate_data.get("created_at"),
            "updated_at": candidate_data.get("updated_at"),
        }

        # Index document
        self.client.index(
            index=self.index_name,
            id=candidate_data.get("id"),
            body=doc,
            refresh=True,
        )

    def bm25_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        size: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        BM25 full-text search

        Args:
            query: Search query
            filters: Optional filters (status, location, etc.)
            size: Number of results

        Returns:
            List of search results with scores
        """
        # Build query
        must_clauses = [
            {
                "multi_match": {
                    "query": query,
                    "fields": [
                        "name^3",
                        "current_company^2",
                        "current_title^2",
                        "skills^2",
                        "full_text",
                    ],
                    "type": "best_fields",
                }
            }
        ]

        # Add filters
        filter_clauses = []
        if filters:
            if "status" in filters:
                filter_clauses.append({"term": {"status": filters["status"]}})
            if "location" in filters:
                filter_clauses.append({"term": {"location": filters["location"]}})
            if "min_experience" in filters:
                filter_clauses.append(
                    {"range": {"years_of_experience": {"gte": filters["min_experience"]}}}
                )

        search_body = {
            "query": {
                "bool": {
                    "must": must_clauses,
                    "filter": filter_clauses if filter_clauses else [],
                }
            },
            "size": size,
        }

        # Execute search
        response = self.client.search(index=self.index_name, body=search_body)

        # Format results
        results = []
        for hit in response["hits"]["hits"]:
            result = hit["_source"]
            result["score"] = hit["_score"]
            result["search_type"] = "bm25"
            results.append(result)

        return results

    def vector_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        size: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Vector semantic search

        Args:
            query: Search query
            filters: Optional filters
            size: Number of results

        Returns:
            List of search results with scores
        """
        # Generate query embedding
        query_embedding = self.generate_embedding(query)

        # Build filter
        filter_clauses = []
        if filters:
            if "status" in filters:
                filter_clauses.append({"term": {"status": filters["status"]}})
            if "location" in filters:
                filter_clauses.append({"term": {"location": filters["location"]}})

        # Build search body
        search_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "knn": {
                                "embedding": {
                                    "vector": query_embedding,
                                    "k": size,
                                }
                            }
                        }
                    ],
                    "filter": filter_clauses if filter_clauses else [],
                }
            },
            "size": size,
        }

        # Execute search
        response = self.client.search(index=self.index_name, body=search_body)

        # Format results
        results = []
        for hit in response["hits"]["hits"]:
            result = hit["_source"]
            result["score"] = hit["_score"]
            result["search_type"] = "vector"
            results.append(result)

        return results

    def hybrid_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        size: int = 20,
        bm25_weight: float = 0.5,
        vector_weight: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search combining BM25 and vector search

        Args:
            query: Search query
            filters: Optional filters
            size: Number of results
            bm25_weight: Weight for BM25 scores
            vector_weight: Weight for vector scores

        Returns:
            List of search results with combined scores
        """
        # Get results from both methods
        bm25_results = self.bm25_search(query, filters, size * 2)
        vector_results = self.vector_search(query, filters, size * 2)

        # Normalize scores
        def normalize_scores(results):
            if not results:
                return results
            max_score = max(r["score"] for r in results)
            if max_score > 0:
                for r in results:
                    r["normalized_score"] = r["score"] / max_score
            return results

        bm25_results = normalize_scores(bm25_results)
        vector_results = normalize_scores(vector_results)

        # Combine results
        combined = {}
        for result in bm25_results:
            candidate_id = result["id"]
            combined[candidate_id] = result.copy()
            combined[candidate_id]["bm25_score"] = result.get("normalized_score", 0)
            combined[candidate_id]["vector_score"] = 0
            combined[candidate_id]["combined_score"] = (
                result.get("normalized_score", 0) * bm25_weight
            )

        for result in vector_results:
            candidate_id = result["id"]
            if candidate_id in combined:
                combined[candidate_id]["vector_score"] = result.get("normalized_score", 0)
                combined[candidate_id]["combined_score"] += (
                    result.get("normalized_score", 0) * vector_weight
                )
            else:
                combined[candidate_id] = result.copy()
                combined[candidate_id]["bm25_score"] = 0
                combined[candidate_id]["vector_score"] = result.get("normalized_score", 0)
                combined[candidate_id]["combined_score"] = (
                    result.get("normalized_score", 0) * vector_weight
                )

        # Sort by combined score
        results = sorted(
            combined.values(),
            key=lambda x: x["combined_score"],
            reverse=True
        )[:size]

        # Add search type
        for r in results:
            r["search_type"] = "hybrid"

        return results


# Global search service instance
search_service = CandidateSearchService()
