import hashlib
import re
from typing import Tuple, Dict, Set, Optional, List
import time
from datetime import datetime, timedelta
import logging
from collections import OrderedDict

logger = logging.getLogger(__name__)

class LRUCache:
    """
    Simple LRU cache implementation
    """
    def __init__(self, capacity: int = 1000):
        self.cache = OrderedDict()
        self.capacity = capacity
    
    def get(self, key: str) -> Optional[Dict]:
        if key not in self.cache:
            return None
        
        # Move to end (most recently used)
        value = self.cache.pop(key)
        self.cache[key] = value
        return value
    
    def put(self, key: str, value: Dict) -> None:
        if key in self.cache:
            self.cache.pop(key)
        elif len(self.cache) >= self.capacity:
            # Remove least recently used
            self.cache.popitem(last=False)
        
        self.cache[key] = value
    
    def items(self):
        return self.cache.items()
    
    def __len__(self):
        return len(self.cache)
    
    def remove(self, key: str) -> None:
        if key in self.cache:
            self.cache.pop(key)

class DuplicateDetector:
    """
    Service for detecting duplicate emails based on content similarity
    """
    
    def __init__(self, cache_duration_days: int = 7, cache_size: int = 10000):
        """
        Initialize the duplicate detector
        
        Args:
            cache_duration_days: Number of days to keep emails in cache for duplicate checking
            cache_size: Maximum number of emails to keep in cache
        """
        # Use LRU cache for storage
        self.email_cache = LRUCache(capacity=cache_size)
        self.cache_duration = timedelta(days=cache_duration_days)
        logger.info(f"Initialized duplicate detector with {cache_duration_days} days cache duration")
    
    def check_duplicate(self, 
                       email_content: str, 
                       sender: str, 
                       subject: str,
                       thread_id: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Check if an email is a duplicate of a previously seen email
        
        Args:
            email_content: The body content of the email
            sender: Email address of the sender
            subject: Email subject line
            thread_id: Optional thread identifier
            
        Returns:
            Tuple of (is_duplicate, reason)
        """
        # Clean up expired cache entries
        self._cleanup_cache()
        
        # Normalize the email content
        normalized_content = self._normalize_email(email_content)
        
        # Generate a fingerprint for the email
        content_hash = self._generate_hash(normalized_content)
        subject_hash = self._generate_hash(self._normalize_subject(subject))
        
        # If thread_id is provided, check for duplicate within same thread
        if thread_id:
            # Check for exact content match within thread
            thread_matches = []
            for hash_key, entry in self.email_cache.items():
                if entry.get('thread_id') == thread_id:
                    thread_matches.append(entry)
            
            if thread_matches:
                # Sort by timestamp (most recent first)
                thread_matches.sort(key=lambda x: x['timestamp'], reverse=True)
                
                # Check for similar content
                for match in thread_matches:
                    similarity = self._calculate_similarity(normalized_content, match['normalized_content'])
                    if similarity > 0.9:  # High threshold for thread duplicates
                        return True, f"Duplicate of email in same thread from {match['timestamp']}"
        
        # Check for exact content match
        exact_match = self.email_cache.get(content_hash)
        if exact_match:
            return True, f"Exact duplicate of email from {exact_match['sender']} on {exact_match['timestamp']}"
        
        # Check for subject + sender match with similar content
        for hash_key, entry in self.email_cache.items():
            if (entry['subject_hash'] == subject_hash and 
                entry['sender'] == sender and
                self._calculate_similarity(normalized_content, entry['normalized_content']) > 0.8):
                
                return True, f"Similar to email from {entry['sender']} on {entry['timestamp']} with same subject"
        
        # Not a duplicate, add to cache
        self.email_cache.put(content_hash, {
            'sender': sender,
            'subject_hash': subject_hash,
            'normalized_content': normalized_content,
            'timestamp': datetime.now().isoformat(),
            'expiry': datetime.now() + self.cache_duration,
            'thread_id': thread_id
        })
        
        return False, None
    
    def _normalize_email(self, content: str) -> str:
        """Normalize email content for comparison"""
        # Remove email forwarding/reply markers
        content = re.sub(r'^>+\s*', '', content, flags=re.MULTILINE)
        
        # Remove signatures and footers
        content = re.sub(r'--+\s*\n.*', '', content, flags=re.DOTALL)
        
        # Remove URLs and email addresses
        content = re.sub(r'https?://\S+', '', content)
        content = re.sub(r'\S+@\S+\.\S+', '', content)
        
        # Remove timestamps and dates (common in email headers)
        content = re.sub(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', '', content)
        content = re.sub(r'\d{1,2}:\d{2}(:\d{2})?(\s*[AP]M)?', '', content)
        
        # Remove whitespace and convert to lowercase
        content = re.sub(r'\s+', ' ', content).strip().lower()
        
        return content
    
    def _normalize_subject(self, subject: str) -> str:
        """Normalize email subject for comparison"""
        # Remove reply/forward prefixes
        subject = re.sub(r'^(re|fwd|fw):\s*', '', subject, flags=re.IGNORECASE)
        
        # Remove whitespace and convert to lowercase
        return subject.strip().lower()
    
    def _generate_hash(self, text: str) -> str:
        """Generate a hash for the text"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using a simple approach"""
        # For production, consider using more sophisticated NLP techniques
        
        # Convert to sets of words
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        if union == 0:
            return 0
        
        return intersection / union
    
    def _cleanup_cache(self) -> None:
        """Remove expired entries from the cache"""
        now = datetime.now()
        expired_keys = []
        
        for key, entry in self.email_cache.items():
            if entry['expiry'] < now:
                expired_keys.append(key)
        
        for key in expired_keys:
            self.email_cache.remove(key)
            
        if expired_keys:
            logger.debug(f"Removed {len(expired_keys)} expired entries from duplicate cache")