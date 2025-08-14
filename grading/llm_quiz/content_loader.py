"""
Content loading utilities for LLM Quiz Challenge.

This module handles fetching and combining content from various URL sources
to provide context for quiz questions.
"""

import logging
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ContentSource:
    """Represents a single content source with metadata."""
    url: str
    content: str
    filename: str
    success: bool
    error: Optional[str] = None


class ContentLoader:
    """Handles loading and combining content from various URL sources."""
    
    def __init__(self, timeout: int = 30, user_agent: str = "llm-quiz-challenge"):
        """Initialize the content loader.
        
        Args:
            timeout: Request timeout in seconds
            user_agent: User agent string for requests
        """
        self.timeout = timeout
        self.user_agent = user_agent
    
    def load_from_urls_file(self, urls_file: str) -> Optional[str]:
        """Load and concatenate content from URLs listed in a file.
        
        Args:
            urls_file: Path to file containing URLs (one per line)
            
        Returns:
            Combined content from all successfully loaded URLs, or None if no content loaded
        """
        try:
            urls = self._read_urls_from_file(urls_file)
            if not urls:
                logger.warning(f"No URLs found in {urls_file}")
                return None
            
            return self.load_from_urls(urls)
            
        except FileNotFoundError:
            logger.error(f"URLs file not found: {urls_file}")
            return None
        except Exception as e:
            logger.error(f"Error loading context from URLs file {urls_file}: {e}")
            return None
    
    def load_from_urls(self, urls: List[str]) -> Optional[str]:
        """Load and concatenate content from a list of URLs.
        
        Args:
            urls: List of URLs to fetch content from
            
        Returns:
            Combined content from all successfully loaded URLs, or None if no content loaded
        """
        logger.info(f"Loading content from {len(urls)} URLs")
        
        sources = []
        for i, url in enumerate(urls, 1):
            logger.info(f"Fetching content from URL {i}/{len(urls)}: {url}")
            source = self._fetch_single_url(url)
            sources.append(source)
        
        # Combine successful sources
        successful_sources = [s for s in sources if s.success]
        
        if not successful_sources:
            logger.warning("No content successfully loaded from any URLs")
            return None
        
        combined_content = self._combine_sources(successful_sources)
        logger.info(f"Successfully combined content from {len(successful_sources)}/{len(urls)} URLs")
        
        return combined_content
    
    def get_load_summary(self, urls: List[str]) -> Dict[str, Any]:
        """Get detailed summary of loading results for analysis.
        
        Args:
            urls: List of URLs to fetch and analyze
            
        Returns:
            Dictionary with detailed loading results and statistics
        """
        sources = []
        for url in urls:
            source = self._fetch_single_url(url)
            sources.append(source)
        
        successful = [s for s in sources if s.success]
        failed = [s for s in sources if not s.success]
        
        return {
            "total_urls": len(urls),
            "successful_loads": len(successful),
            "failed_loads": len(failed),
            "success_rate": len(successful) / len(urls) if urls else 0,
            "sources": sources,
            "combined_content": self._combine_sources(successful) if successful else None,
            "total_content_length": sum(len(s.content) for s in successful)
        }
    
    def _read_urls_from_file(self, urls_file: str) -> List[str]:
        """Read URLs from a file, filtering out comments and empty lines."""
        with open(urls_file, 'r') as f:
            urls = []
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    urls.append(line)
            return urls
    
    def _fetch_single_url(self, url: str) -> ContentSource:
        """Fetch content from a single URL."""
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', self.user_agent)

            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                content = response.read().decode('utf-8')
                filename = self._extract_filename_from_url(url)
                
                logger.info(f"Successfully loaded {len(content)} characters from {url}")
                
                return ContentSource(
                    url=url,
                    content=content,
                    filename=filename,
                    success=True
                )
                
        except urllib.error.HTTPError as e:
            error_msg = f"HTTP error {e.code}: {e.reason}"
            if e.code == 404:
                logger.warning(f"URL not found (404): {url}")
            else:
                logger.error(f"HTTP error {e.code} fetching {url}: {e.reason}")
            
            return ContentSource(
                url=url,
                content="",
                filename=self._extract_filename_from_url(url),
                success=False,
                error=error_msg
            )
            
        except urllib.error.URLError as e:
            error_msg = f"URL error: {e.reason}"
            logger.error(f"URL error fetching {url}: {e.reason}")
            
            return ContentSource(
                url=url,
                content="",
                filename=self._extract_filename_from_url(url),
                success=False,
                error=error_msg
            )
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Error loading content from {url}: {e}")
            
            return ContentSource(
                url=url,
                content="",
                filename=self._extract_filename_from_url(url),
                success=False,
                error=error_msg
            )
    
    def _extract_filename_from_url(self, url: str) -> str:
        """Extract a reasonable filename from a URL."""
        try:
            # Get the last path component
            path_parts = url.rstrip('/').split('/')
            if path_parts:
                filename = path_parts[-1]
                # If it's empty or looks like a directory, create a generic name
                if not filename or '.' not in filename:
                    # Use domain + path hash for uniqueness
                    domain = url.split('/')[2] if '//' in url else 'unknown'
                    return f"content_from_{domain}"
                return filename
            else:
                return "content"
        except:
            return "content"
    
    def _combine_sources(self, sources: List[ContentSource]) -> str:
        """Combine multiple content sources into a single string."""
        if not sources:
            return ""
        
        combined_parts = []
        for source in sources:
            header = f"# {source.filename} (from {source.url})"
            combined_parts.append(f"{header}\n\n{source.content}")
        
        return "\n\n" + "="*80 + "\n\n".join(combined_parts)