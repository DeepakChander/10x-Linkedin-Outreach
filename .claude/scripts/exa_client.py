#!/usr/bin/env python3
"""
Exa AI REST API Client
Official API wrapper for all Exa endpoints.

Endpoints covered:
  POST /search       — Neural/keyword/auto/deep web search
  POST /contents     — Get clean parsed content for URLs
  POST /findsimilar  — Find pages similar to a given URL
  POST /answer       — LLM-powered answer with citations
  POST /research     — Automated deep research with structured output

Docs: https://docs.exa.ai/reference/search
API Base: https://api.exa.ai

Usage:
  python exa_client.py search "AI startup founders in SF"
  python exa_client.py search "AI founders" --type neural --num-results 20 --category company
  python exa_client.py contents URL1 URL2 --text --summary
  python exa_client.py similar "https://anthropic.com" --num-results 10
  python exa_client.py answer "What is Anthropic's latest model?"
  python exa_client.py research "AI safety landscape 2026"

Requires EXA_API_KEY in environment or .env file.
"""

import json
import os
import sys
import argparse
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional
from pathlib import Path

BASE_URL = "https://api.exa.ai"


def get_api_key() -> str:
    """Get Exa API key from environment or .env file."""
    key = os.environ.get("EXA_API_KEY")
    if key:
        return key

    # Try .env files
    for env_file in [".env", ".env.local"]:
        env_path = Path(env_file)
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line.startswith("EXA_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")

    print("ERROR: EXA_API_KEY not found. Set it in environment or .env file.", file=sys.stderr)
    sys.exit(1)


def api_request(endpoint: str, body: Dict[str, Any], api_key: str) -> Dict:
    """Make a POST request to Exa API."""
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        print(f"API Error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)


# ─── Search ──────────────────────────────────────────────────────────────────

def search(
    query: str,
    *,
    search_type: str = "auto",
    category: Optional[str] = None,
    num_results: int = 10,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    start_published_date: Optional[str] = None,
    end_published_date: Optional[str] = None,
    include_text: Optional[List[str]] = None,
    exclude_text: Optional[List[str]] = None,
    include_contents: bool = True,
    livecrawl: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Dict:
    """
    POST /search — Perform a semantic or keyword search.

    Args:
        query: Search query string.
        search_type: "neural" | "keyword" | "auto" | "deep" (default: "auto")
        category: Optional filter — "company", "research paper", "news", "pdf",
                  "github", "tweet", "personal site", "financial report", "people"
        num_results: Number of results (max 100, default 10).
        include_domains: Only include results from these domains (max 1200).
        exclude_domains: Exclude results from these domains (max 1200).
        start_published_date: ISO 8601 date — only results published after.
        end_published_date: ISO 8601 date — only results published before.
        include_text: Only include results containing ALL these strings.
        exclude_text: Exclude results containing ANY of these strings.
        include_contents: If True, returns text/highlights/summary inline.
        livecrawl: "always" | "fallback" | "never" — live crawl behavior.
    """
    key = api_key or get_api_key()

    body: Dict[str, Any] = {
        "query": query,
        "type": search_type,
        "numResults": num_results,
    }

    if category:
        body["category"] = category
    if include_domains:
        body["includeDomains"] = include_domains
    if exclude_domains:
        body["excludeDomains"] = exclude_domains
    if start_published_date:
        body["startPublishedDate"] = start_published_date
    if end_published_date:
        body["endPublishedDate"] = end_published_date
    if include_text:
        body["includeText"] = include_text
    if exclude_text:
        body["excludeText"] = exclude_text

    if include_contents:
        body["contents"] = {
            "text": {"maxCharacters": 3000},
            "highlights": {"numSentences": 3},
            "summary": {"query": query},
        }

    if livecrawl:
        body.setdefault("contents", {})["livecrawl"] = livecrawl

    return api_request("/search", body, key)


# ─── Get Contents ────────────────────────────────────────────────────────────

def get_contents(
    urls: List[str],
    *,
    text: bool = True,
    highlights: bool = False,
    summary: bool = False,
    summary_query: Optional[str] = None,
    livecrawl: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Dict:
    """
    POST /contents — Get clean, parsed content for specific URLs.

    Args:
        urls: List of URLs to get content for.
        text: Include full text content.
        highlights: Include highlighted sentences.
        summary: Include AI summary.
        summary_query: Custom query for summary generation.
        livecrawl: "always" | "fallback" | "never".
    """
    key = api_key or get_api_key()

    contents: Dict[str, Any] = {}
    if text:
        contents["text"] = {"maxCharacters": 10000}
    if highlights:
        contents["highlights"] = {"numSentences": 5}
    if summary:
        contents["summary"] = {"query": summary_query or ""}

    if livecrawl:
        contents["livecrawl"] = livecrawl

    body = {
        "ids": urls,
        "contents": contents,
    }

    return api_request("/contents", body, key)


# ─── Find Similar ────────────────────────────────────────────────────────────

def find_similar(
    url: str,
    *,
    num_results: int = 10,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    include_contents: bool = True,
    category: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Dict:
    """
    POST /findsimilar — Find pages similar to a given URL.

    Args:
        url: The reference URL to find similar pages for.
        num_results: Number of results (max 100).
        include_domains: Only include results from these domains.
        exclude_domains: Exclude results from these domains.
        include_contents: Return text/highlights/summary inline.
        category: Optional category filter.
    """
    key = api_key or get_api_key()

    body: Dict[str, Any] = {
        "url": url,
        "numResults": num_results,
    }

    if include_domains:
        body["includeDomains"] = include_domains
    if exclude_domains:
        body["excludeDomains"] = exclude_domains
    if category:
        body["category"] = category

    if include_contents:
        body["contents"] = {
            "text": {"maxCharacters": 3000},
            "highlights": {"numSentences": 3},
        }

    return api_request("/findsimilar", body, key)


# ─── Answer ──────────────────────────────────────────────────────────────────

def answer(
    query: str,
    *,
    num_results: int = 5,
    search_type: str = "auto",
    include_domains: Optional[List[str]] = None,
    api_key: Optional[str] = None,
) -> Dict:
    """
    POST /answer — Get an LLM-generated answer with source citations.

    Args:
        query: The question to answer.
        num_results: Number of sources to use.
        search_type: "neural" | "keyword" | "auto".
        include_domains: Only use sources from these domains.
    """
    key = api_key or get_api_key()

    body: Dict[str, Any] = {
        "query": query,
        "type": search_type,
        "numResults": num_results,
    }

    if include_domains:
        body["includeDomains"] = include_domains

    return api_request("/answer", body, key)


# ─── Research ────────────────────────────────────────────────────────────────

def research(
    query: str,
    *,
    api_key: Optional[str] = None,
) -> Dict:
    """
    POST /research — Automated in-depth web research with structured output.

    Returns a comprehensive research report with citations.

    Args:
        query: The research topic/question.
    """
    key = api_key or get_api_key()

    body = {"query": query}
    return api_request("/research", body, key)


# ─── LinkedIn Search (via /search with category) ────────────────────────────

def linkedin_search(
    query: str,
    *,
    num_results: int = 20,
    api_key: Optional[str] = None,
) -> Dict:
    """
    Search LinkedIn profiles using Exa's /search with LinkedIn domain filter.

    Args:
        query: Search query describing the people you want to find.
        num_results: Number of results.
    """
    return search(
        query,
        search_type="neural",
        num_results=num_results,
        include_domains=["linkedin.com/in"],
        include_contents=True,
        api_key=api_key,
    )


# ─── Company Research (via /search with category) ───────────────────────────

def company_research(
    company_name: str,
    *,
    num_results: int = 10,
    api_key: Optional[str] = None,
) -> Dict:
    """
    Research a company using Exa's search with company category.

    Args:
        company_name: Name of the company to research.
        num_results: Number of results.
    """
    return search(
        company_name,
        search_type="neural",
        category="company",
        num_results=num_results,
        include_contents=True,
        api_key=api_key,
    )


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Exa AI REST API Client")
    subparsers = parser.add_subparsers(dest="command", help="API endpoint")

    # search
    sp = subparsers.add_parser("search", help="Search the web")
    sp.add_argument("query", help="Search query")
    sp.add_argument("--type", dest="search_type", default="auto",
                    choices=["neural", "keyword", "auto", "deep"])
    sp.add_argument("--category", choices=[
        "company", "research paper", "news", "pdf", "github",
        "tweet", "personal site", "financial report", "people"])
    sp.add_argument("--num-results", type=int, default=10)
    sp.add_argument("--include-domains", nargs="+")
    sp.add_argument("--exclude-domains", nargs="+")
    sp.add_argument("--start-date", help="ISO 8601 start published date")
    sp.add_argument("--end-date", help="ISO 8601 end published date")
    sp.add_argument("--include-text", nargs="+")
    sp.add_argument("--exclude-text", nargs="+")
    sp.add_argument("--no-contents", action="store_true")
    sp.add_argument("--livecrawl", choices=["always", "fallback", "never"])

    # contents
    sp = subparsers.add_parser("contents", help="Get content for URLs")
    sp.add_argument("urls", nargs="+", help="URLs to fetch")
    sp.add_argument("--text", action="store_true", default=True)
    sp.add_argument("--highlights", action="store_true")
    sp.add_argument("--summary", action="store_true")
    sp.add_argument("--summary-query", help="Custom summary query")
    sp.add_argument("--livecrawl", choices=["always", "fallback", "never"])

    # findsimilar
    sp = subparsers.add_parser("similar", help="Find similar pages")
    sp.add_argument("url", help="Reference URL")
    sp.add_argument("--num-results", type=int, default=10)
    sp.add_argument("--include-domains", nargs="+")
    sp.add_argument("--exclude-domains", nargs="+")
    sp.add_argument("--category")

    # answer
    sp = subparsers.add_parser("answer", help="Get LLM answer with citations")
    sp.add_argument("query", help="Question to answer")
    sp.add_argument("--num-results", type=int, default=5)
    sp.add_argument("--type", dest="search_type", default="auto")
    sp.add_argument("--include-domains", nargs="+")

    # research
    sp = subparsers.add_parser("research", help="Deep research on a topic")
    sp.add_argument("query", help="Research topic")

    # linkedin
    sp = subparsers.add_parser("linkedin", help="Search LinkedIn profiles")
    sp.add_argument("query", help="Search query for people")
    sp.add_argument("--num-results", type=int, default=20)

    # company
    sp = subparsers.add_parser("company", help="Research a company")
    sp.add_argument("name", help="Company name")
    sp.add_argument("--num-results", type=int, default=10)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    result: Dict = {}

    if args.command == "search":
        result = search(
            args.query,
            search_type=args.search_type,
            category=args.category,
            num_results=args.num_results,
            include_domains=args.include_domains,
            exclude_domains=args.exclude_domains,
            start_published_date=args.start_date,
            end_published_date=args.end_date,
            include_text=args.include_text,
            exclude_text=args.exclude_text,
            include_contents=not args.no_contents,
            livecrawl=args.livecrawl,
        )

    elif args.command == "contents":
        result = get_contents(
            args.urls,
            text=args.text,
            highlights=args.highlights,
            summary=args.summary,
            summary_query=args.summary_query,
            livecrawl=args.livecrawl,
        )

    elif args.command == "similar":
        result = find_similar(
            args.url,
            num_results=args.num_results,
            include_domains=args.include_domains,
            exclude_domains=args.exclude_domains,
            category=args.category,
        )

    elif args.command == "answer":
        result = answer(
            args.query,
            num_results=args.num_results,
            search_type=args.search_type,
            include_domains=args.include_domains,
        )

    elif args.command == "research":
        result = research(args.query)

    elif args.command == "linkedin":
        result = linkedin_search(args.query, num_results=args.num_results)

    elif args.command == "company":
        result = company_research(args.name, num_results=args.num_results)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
