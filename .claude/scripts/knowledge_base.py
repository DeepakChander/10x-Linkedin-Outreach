#!/usr/bin/env python3
"""
Knowledge Base for 10x-Outreach-Skill
Search KB before composing replies for IT Operations Support

Features:
- Semantic search using sentence-transformers (optional)
- Keyword fallback when embeddings unavailable
- Category and tag filtering
- Response template suggestions
- Multi-tenant isolation

Cross-platform compatible (Windows, macOS, Linux)
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict, field
import uuid

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
except ImportError as e:
    print(f"[X] Missing dependency: {e}")
    sys.exit(1)

# Try to import sentence-transformers for semantic search
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False

load_dotenv(Path(__file__).parent.parent / '.env')


@dataclass
class KBArticle:
    """Knowledge base article."""
    id: str
    title: str
    content: str
    category: str
    tags: List[str]
    created_at: str
    updated_at: str
    author: str
    tenant_id: Optional[str] = None
    response_template: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    views: int = 0
    helpful_count: int = 0
    embedding: Optional[List[float]] = None

    @classmethod
    def create(
        cls,
        title: str,
        content: str,
        category: str,
        tags: List[str],
        author: str,
        response_template: Optional[str] = None,
        tenant_id: Optional[str] = None
    ):
        """Create a new KB article."""
        now = datetime.utcnow().isoformat() + 'Z'
        article_id = f"KB-{str(uuid.uuid4())[:8].upper()}"

        # Extract keywords from title and content
        keywords = cls._extract_keywords(title + ' ' + content)

        return cls(
            id=article_id,
            title=title,
            content=content,
            category=category,
            tags=tags,
            created_at=now,
            updated_at=now,
            author=author,
            tenant_id=tenant_id,
            response_template=response_template,
            keywords=keywords
        )

    @staticmethod
    def _extract_keywords(text: str) -> List[str]:
        """Extract keywords from text."""
        # Common stop words
        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'to', 'of',
            'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through',
            'during', 'before', 'after', 'above', 'below', 'between', 'under',
            'and', 'or', 'but', 'if', 'then', 'else', 'when', 'where', 'why', 'how',
            'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some',
            'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
            'very', 'just', 'also', 'now', 'your', 'you', 'this', 'that', 'these',
            'those', 'it', 'its', 'they', 'them', 'their', 'we', 'us', 'our', 'i', 'me'
        }

        # Extract words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

        # Filter and get unique
        keywords = list(set(w for w in words if w not in stop_words))

        return keywords[:50]  # Limit to 50 keywords


class KnowledgeBase:
    """
    Knowledge Base manager with semantic and keyword search.

    Provides:
    - Article storage and retrieval
    - Semantic search (when sentence-transformers available)
    - Keyword-based fallback search
    - Category and tag filtering
    - Response template suggestions
    """

    # Model for semantic search
    EMBEDDING_MODEL = 'all-MiniLM-L6-v2'

    def __init__(self, base_dir: Optional[Path] = None, tenant_id: Optional[str] = None):
        """
        Initialize knowledge base.

        Args:
            base_dir: Base directory for KB storage
            tenant_id: Tenant ID for multi-tenant isolation
        """
        self.base_dir = base_dir or Path(__file__).parent.parent
        self.tenant_id = tenant_id

        # Set up KB directory
        if tenant_id:
            self.kb_dir = self.base_dir / 'tenants' / tenant_id / 'knowledge_base'
        else:
            self.kb_dir = self.base_dir / 'knowledge_base'

        self.kb_dir.mkdir(parents=True, exist_ok=True)
        self.articles_dir = self.kb_dir / 'articles'
        self.articles_dir.mkdir(exist_ok=True)

        # Initialize embedding model if available
        self.model = None
        if SEMANTIC_AVAILABLE:
            try:
                self.model = SentenceTransformer(self.EMBEDDING_MODEL)
            except Exception as e:
                print(f"[!] Could not load embedding model: {e}")

        # Load article index
        self._index_path = self.kb_dir / 'index.json'
        self._index = self._load_index()

    def _load_index(self) -> Dict[str, Dict]:
        """Load article index."""
        if self._index_path.exists():
            try:
                with open(self._index_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def _save_index(self):
        """Save article index."""
        with open(self._index_path, 'w', encoding='utf-8') as f:
            json.dump(self._index, f, indent=2)

    def _compute_embedding(self, text: str) -> Optional[List[float]]:
        """Compute embedding for text."""
        if not self.model:
            return None

        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except:
            return None

    def add_article(self, article: KBArticle) -> bool:
        """
        Add article to knowledge base.

        Args:
            article: KBArticle object

        Returns:
            True if successful
        """
        # Compute embedding if model available
        if self.model and not article.embedding:
            embedding_text = f"{article.title} {article.content}"
            article.embedding = self._compute_embedding(embedding_text)

        # Save article
        article_path = self.articles_dir / f"{article.id}.json"
        article_dict = asdict(article)

        with open(article_path, 'w', encoding='utf-8') as f:
            json.dump(article_dict, f, indent=2)

        # Update index
        self._index[article.id] = {
            'title': article.title,
            'category': article.category,
            'tags': article.tags,
            'keywords': article.keywords,
            'created_at': article.created_at
        }
        self._save_index()

        return True

    def get_article(self, article_id: str) -> Optional[KBArticle]:
        """Get article by ID."""
        article_path = self.articles_dir / f"{article_id}.json"

        if not article_path.exists():
            return None

        try:
            with open(article_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Increment view count
            data['views'] = data.get('views', 0) + 1
            with open(article_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            return KBArticle(**data)
        except Exception as e:
            print(f"[!] Error loading article {article_id}: {e}")
            return None

    def update_article(self, article_id: str, updates: Dict[str, Any]) -> Optional[KBArticle]:
        """Update article fields."""
        article = self.get_article(article_id)
        if not article:
            return None

        # Apply updates
        for key, value in updates.items():
            if hasattr(article, key):
                setattr(article, key, value)

        article.updated_at = datetime.utcnow().isoformat() + 'Z'

        # Recompute keywords if content changed
        if 'content' in updates or 'title' in updates:
            article.keywords = KBArticle._extract_keywords(
                f"{article.title} {article.content}"
            )
            # Recompute embedding
            if self.model:
                article.embedding = self._compute_embedding(
                    f"{article.title} {article.content}"
                )

        # Save
        self.add_article(article)
        return article

    def delete_article(self, article_id: str) -> bool:
        """Delete article."""
        article_path = self.articles_dir / f"{article_id}.json"

        if article_path.exists():
            article_path.unlink()
            if article_id in self._index:
                del self._index[article_id]
                self._save_index()
            return True

        return False

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge base.

        Uses semantic search if available, falls back to keyword matching.

        Args:
            query: Search query
            category: Filter by category
            tags: Filter by tags
            limit: Maximum results

        Returns:
            List of matching articles with scores
        """
        # Try semantic search first
        if self.model:
            results = self._semantic_search(query, category, tags, limit)
            if results:
                return results

        # Fallback to keyword search
        return self._keyword_search(query, category, tags, limit)

    def _semantic_search(
        self,
        query: str,
        category: Optional[str],
        tags: Optional[List[str]],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Semantic search using embeddings."""
        query_embedding = self._compute_embedding(query)
        if not query_embedding:
            return []

        results = []
        query_np = np.array(query_embedding)

        for article_id in self._index:
            # Category filter
            if category and self._index[article_id].get('category') != category:
                continue

            # Tag filter
            if tags:
                article_tags = set(self._index[article_id].get('tags', []))
                if not article_tags.intersection(set(tags)):
                    continue

            # Load article for embedding
            article_path = self.articles_dir / f"{article_id}.json"
            if not article_path.exists():
                continue

            try:
                with open(article_path, 'r', encoding='utf-8') as f:
                    article_data = json.load(f)

                embedding = article_data.get('embedding')
                if not embedding:
                    continue

                # Cosine similarity
                article_np = np.array(embedding)
                similarity = np.dot(query_np, article_np) / (
                    np.linalg.norm(query_np) * np.linalg.norm(article_np)
                )

                results.append({
                    'id': article_id,
                    'title': article_data['title'],
                    'category': article_data['category'],
                    'snippet': article_data['content'][:200] + '...',
                    'score': float(similarity),
                    'response_template': article_data.get('response_template')
                })

            except:
                continue

        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)

        return results[:limit]

    def _keyword_search(
        self,
        query: str,
        category: Optional[str],
        tags: Optional[List[str]],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Keyword-based search fallback."""
        query_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', query.lower()))
        results = []

        for article_id, meta in self._index.items():
            # Category filter
            if category and meta.get('category') != category:
                continue

            # Tag filter
            if tags:
                article_tags = set(meta.get('tags', []))
                if not article_tags.intersection(set(tags)):
                    continue

            # Keyword matching
            article_keywords = set(meta.get('keywords', []))
            matches = query_words.intersection(article_keywords)

            if not matches:
                # Check title
                title_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', meta['title'].lower()))
                matches = query_words.intersection(title_words)

            if matches:
                score = len(matches) / len(query_words) if query_words else 0

                # Load full article for snippet
                article_path = self.articles_dir / f"{article_id}.json"
                snippet = meta['title']
                response_template = None

                if article_path.exists():
                    try:
                        with open(article_path, 'r', encoding='utf-8') as f:
                            article_data = json.load(f)
                        snippet = article_data['content'][:200] + '...'
                        response_template = article_data.get('response_template')
                    except:
                        pass

                results.append({
                    'id': article_id,
                    'title': meta['title'],
                    'category': meta['category'],
                    'snippet': snippet,
                    'score': score,
                    'response_template': response_template,
                    'matched_keywords': list(matches)
                })

        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)

        return results[:limit]

    def get_categories(self) -> List[str]:
        """Get all unique categories."""
        categories = set()
        for meta in self._index.values():
            if meta.get('category'):
                categories.add(meta['category'])
        return sorted(list(categories))

    def get_tags(self) -> List[str]:
        """Get all unique tags."""
        tags = set()
        for meta in self._index.values():
            for tag in meta.get('tags', []):
                tags.add(tag)
        return sorted(list(tags))

    def list_articles(
        self,
        category: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """List articles with optional category filter."""
        articles = []

        for article_id, meta in self._index.items():
            if category and meta.get('category') != category:
                continue

            articles.append({
                'id': article_id,
                'title': meta['title'],
                'category': meta['category'],
                'tags': meta.get('tags', []),
                'created_at': meta.get('created_at')
            })

        # Sort by creation date
        articles.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        return articles[:limit]

    def get_stats(self) -> Dict[str, Any]:
        """Get KB statistics."""
        stats = {
            'total_articles': len(self._index),
            'by_category': {},
            'total_views': 0,
            'semantic_enabled': self.model is not None
        }

        for article_id in self._index:
            category = self._index[article_id].get('category', 'uncategorized')
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1

            # Count views
            article_path = self.articles_dir / f"{article_id}.json"
            if article_path.exists():
                try:
                    with open(article_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    stats['total_views'] += data.get('views', 0)
                except:
                    pass

        return stats


# Factory function
def get_knowledge_base(
    base_dir: Optional[Path] = None,
    tenant_id: Optional[str] = None
) -> KnowledgeBase:
    """Get knowledge base instance."""
    return KnowledgeBase(base_dir, tenant_id)


# CLI
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Knowledge Base CLI')
    parser.add_argument('--search', metavar='QUERY', help='Search knowledge base')
    parser.add_argument('--list', action='store_true', help='List all articles')
    parser.add_argument('--stats', action='store_true', help='Show KB statistics')
    parser.add_argument('--add-sample', action='store_true', help='Add sample articles')
    parser.add_argument('--category', help='Filter by category')

    args = parser.parse_args()

    kb = KnowledgeBase()

    if args.search:
        results = kb.search(args.search, category=args.category)
        print(f"\nSearch results for '{args.search}':\n")
        for r in results:
            print(f"  [{r['score']:.2f}] {r['title']}")
            print(f"        Category: {r['category']}")
            print(f"        {r['snippet'][:100]}...")
            if r.get('response_template'):
                print(f"        [Has response template]")
            print()

    elif args.list:
        articles = kb.list_articles(category=args.category)
        print(f"\nKnowledge Base Articles ({len(articles)}):\n")
        for a in articles:
            print(f"  {a['id']}: {a['title']}")
            print(f"        Category: {a['category']}, Tags: {', '.join(a['tags'])}")

    elif args.stats:
        stats = kb.get_stats()
        print(f"\nKnowledge Base Statistics:")
        print(f"  Total articles: {stats['total_articles']}")
        print(f"  Total views: {stats['total_views']}")
        print(f"  Semantic search: {'enabled' if stats['semantic_enabled'] else 'disabled'}")
        print(f"\n  By category:")
        for cat, count in stats['by_category'].items():
            print(f"    {cat}: {count}")

    elif args.add_sample:
        print("Adding sample KB articles...")

        # Password reset
        article1 = KBArticle.create(
            title="How to Reset Your Password",
            content="""
            To reset your password, follow these steps:

            1. Go to the login page
            2. Click "Forgot Password"
            3. Enter your email address
            4. Check your email for the reset link
            5. Click the link and enter your new password

            Password requirements:
            - At least 8 characters
            - One uppercase letter
            - One number
            - One special character

            If you don't receive the email within 5 minutes, check your spam folder.
            """,
            category="Account",
            tags=["password", "login", "security", "self-service"],
            author="system",
            response_template="To reset your password, please visit our login page and click 'Forgot Password'. Enter your email address, and you'll receive a reset link within a few minutes. If you don't see it, please check your spam folder."
        )
        kb.add_article(article1)

        # VPN setup
        article2 = KBArticle.create(
            title="VPN Setup and Troubleshooting",
            content="""
            VPN Setup Instructions:

            1. Download the VPN client from the IT portal
            2. Install using default settings
            3. Open the client and enter your credentials
            4. Select the nearest server
            5. Click Connect

            Common Issues:
            - Connection timeout: Check your internet connection
            - Authentication failed: Verify your credentials
            - Slow connection: Try a different server

            Contact IT if issues persist.
            """,
            category="Network",
            tags=["vpn", "remote", "network", "connectivity"],
            author="system",
            response_template="For VPN issues, please try disconnecting and reconnecting. If the problem persists, try selecting a different server. Make sure your internet connection is stable. For setup instructions, visit the IT portal."
        )
        kb.add_article(article2)

        # Outlook issues
        article3 = KBArticle.create(
            title="Outlook Not Syncing - Resolution Steps",
            content="""
            If Outlook is not syncing emails:

            1. Check internet connection
            2. Restart Outlook
            3. Check for Office updates
            4. Clear Outlook cache:
               - Close Outlook
               - Delete files in %localappdata%/Microsoft/Outlook
               - Restart Outlook

            5. Recreate profile if needed

            For persistent issues, contact IT support.
            """,
            category="Email",
            tags=["outlook", "email", "sync", "office365"],
            author="system",
            response_template="For Outlook sync issues, please try restarting Outlook first. If that doesn't work, check for Office updates. As a last resort, you may need to clear the Outlook cache. I can guide you through these steps if needed."
        )
        kb.add_article(article3)

        print(f"Added {3} sample articles")

    else:
        parser.print_help()
