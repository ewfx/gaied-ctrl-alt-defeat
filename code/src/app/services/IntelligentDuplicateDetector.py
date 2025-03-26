import hashlib
import re
from typing import Tuple, Dict, Set, Optional, List, Any, Union
from datetime import datetime, timedelta
import logging
from collections import OrderedDict
import uuid
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json

# Configure logging to show debug messages
logger = logging.getLogger(__name__)

class LRUCache:
    """
    Simple LRU cache implementation
    """
    def __init__(self, capacity: int = 1000):
        self.cache = OrderedDict()
        self.capacity = capacity
        logger.info(f"Initialized LRUCache with capacity {capacity}")
    
    def get(self, key: str) -> Optional[Dict]:
        if key not in self.cache:
            logger.info(f"Cache miss for key: {key}")
            return None
        
        # Move to end (most recently used)
        value = self.cache.pop(key)
        self.cache[key] = value
        logger.info(f"Cache hit for key: {key}")
        return value
    
    def put(self, key: str, value: Dict) -> None:
        if key in self.cache:
            logger.info(f"Updating existing cache entry: {key}")
            self.cache.pop(key)
        elif len(self.cache) >= self.capacity:
            # Remove least recently used
            removed_key, _ = self.cache.popitem(last=False)
            logger.info(f"Cache full, removing LRU entry: {removed_key}")
        else:
            logger.info(f"Adding new cache entry: {key}")
        
        self.cache[key] = value
    
    def items(self):
        return self.cache.items()
    
    def values(self):
        return self.cache.values()
    
    def __len__(self):
        return len(self.cache)
    
    def remove(self, key: str) -> None:
        if key in self.cache:
            logger.info(f"Manually removing cache entry: {key}")
            self.cache.pop(key)


class EmbeddingProvider:
    """
    Abstract base class for embedding providers
    Implementations could use different models/libraries
    """
    def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding vector for text"""
        raise NotImplementedError("Embedding provider must implement get_embedding")


class MockEmbeddingProvider(EmbeddingProvider):
    """
    Mock embedding provider for testing or when no ML libraries are available
    Uses simple TF-IDF like approach to create pseudo-embeddings
    """
    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        self.vocab = {}  # word -> index mapping
        self.vocab_size = 0
        self.max_vocab_size = 10000
        logger.info(f"Initialized MockEmbeddingProvider with dim={embedding_dim}")
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer - split on non-alphanumeric chars and lowercase"""
        tokens = re.findall(r'\w+', text.lower())
        logger.info(f"Tokenized text into {len(tokens)} tokens")
        return tokens
    
    def _update_vocab(self, tokens: List[str]) -> None:
        """Update vocabulary with new tokens"""
        initial_size = self.vocab_size
        for token in tokens:
            if token not in self.vocab and self.vocab_size < self.max_vocab_size:
                self.vocab[token] = self.vocab_size
                self.vocab_size += 1
        
        if self.vocab_size > initial_size:
            logger.info(f"Vocabulary updated from {initial_size} to {self.vocab_size} tokens")
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Create a simple embedding based on word frequencies
        This is not a true semantic embedding but can work for basic similarity
        """
        if not text:
            logger.info("Creating zero embedding for empty text")
            return np.zeros(self.embedding_dim)
        
        tokens = self._tokenize(text)
        self._update_vocab(tokens)
        
        # Create a sparse vector based on token frequencies
        vec = np.zeros(self.max_vocab_size)
        for token in tokens:
            if token in self.vocab:
                vec[self.vocab[token]] += 1
        
        # Normalize and hash to desired dimension
        if np.sum(vec) > 0:
            vec = vec / np.sqrt(np.sum(vec**2))  # L2 normalize
        
        # Project to desired dimension using a deterministic pseudo-random projection
        if len(vec) > self.embedding_dim:
            # Use a deterministic pseudo-random projection
            # For each output dimension, sum a subset of input dimensions
            projection = np.zeros((len(vec), self.embedding_dim))
            for i in range(len(vec)):
                # Use hash of index to deterministically select output indices
                hash_val = int(hashlib.md5(str(i).encode()).hexdigest(), 16)
                idx = hash_val % self.embedding_dim
                projection[i, idx] = 1
            
            result = vec @ projection
            # Normalize again
            if np.sum(result**2) > 0:
                result = result / np.sqrt(np.sum(result**2))
            
            logger.info(f"Created embedding with shape {result.shape}, norm={np.linalg.norm(result):.4f}")
            return result
        else:
            # Pad with zeros
            result = np.zeros(self.embedding_dim)
            result[:len(vec)] = vec
            logger.info(f"Created embedding with shape {result.shape}, norm={np.linalg.norm(result):.4f}")
            return result


class SentenceTransformerProvider(EmbeddingProvider):
    """
    Embedding provider using SentenceTransformers
    Requires sentence-transformers to be installed
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            logger.info(f"Loaded SentenceTransformer model: {model_name}")
        except ImportError:
            logger.error("SentenceTransformers not installed. Using MockEmbeddingProvider as fallback.")
            self.model = None
            self.mock_provider = MockEmbeddingProvider()
            logger.info("Initialized MockEmbeddingProvider as fallback")
    
    def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding using sentence transformer model"""
        if not text:
            if self.model:
                # Get the embedding dimension by encoding an empty string
                empty_embedding = np.zeros(self.model.get_sentence_embedding_dimension())
                logger.info(f"Created empty embedding with shape {empty_embedding.shape}")
                return empty_embedding
            else:
                return self.mock_provider.get_embedding("")
        
        if self.model:
            try:
                logger.info(f"Generating embedding for text of length {len(text)}")
                embedding = self.model.encode(text, convert_to_numpy=True)
                logger.info(f"Created embedding with shape {embedding.shape}, norm={np.linalg.norm(embedding):.4f}")
                return embedding
            except Exception as e:
                logger.error(f"Error generating embedding with SentenceTransformer: {e}")
                logger.info("Falling back to MockEmbeddingProvider")
                return self.mock_provider.get_embedding(text)
        else:
            return self.mock_provider.get_embedding(text)


class IntelligentDuplicateDetector:
    """
    Intelligent email duplicate detection system using semantic embeddings and metadata analysis
    """
    
    def __init__(
        self, 
        cache_duration_days: int = 14, 
        cache_size: int = 10000,
        embedding_provider: Optional[EmbeddingProvider] = None,
        semantic_threshold: float = 0.85,
        metadata_weight: float = 0.6,
        subject_weight: float = 0.3,
        content_weight: float = 0.7,
        time_window_hours: int = 72,
        email_cache: LRUCache = None
    ):
        """
        Initialize the intelligent duplicate detector
        
        Args:
            cache_duration_days: Number of days to keep emails in cache
            cache_size: Maximum number of emails to keep in cache
            embedding_provider: Provider for text embeddings (defaults to mock if None)
            semantic_threshold: Threshold for considering content semantically similar
            metadata_weight: Weight to give metadata vs content (0-1)
            subject_weight: Weight for subject vs body in content similarity
            content_weight: Weight for content in overall similarity
            time_window_hours: Time window to consider for duplicates (in hours)
        """
        # Use LRU cache for storage
        self.email_cache = email_cache
        self.cache_duration = timedelta(days=cache_duration_days)
        
        # Set up embedding provider
        if embedding_provider is None:
            try:
                logger.info("Attempting to initialize SentenceTransformerProvider")
                self.embedding_provider = SentenceTransformerProvider()
            except Exception as e:
                logger.warning(f"Failed to initialize SentenceTransformerProvider: {e}")
                logger.info("Falling back to MockEmbeddingProvider")
                self.embedding_provider = MockEmbeddingProvider()
        else:
            self.embedding_provider = embedding_provider
            logger.info(f"Using provided embedding provider: {type(embedding_provider).__name__}")
        
        # Configuration parameters
        self.semantic_threshold = semantic_threshold
        self.metadata_weight = metadata_weight
        self.subject_weight = subject_weight
        self.content_weight = content_weight
        self.time_window = timedelta(hours=time_window_hours)
        
        logger.info(
            f"Initialized intelligent duplicate detector with {cache_duration_days} days cache duration, "
            f"metadata weight: {metadata_weight}, content weight: {content_weight}"
        )
    
    def check_duplicate(
        self, 
        email_content: str, 
        sender: str, 
        subject: str,
        recipient: str,
        received_date: Optional[Union[datetime, str]] = None,
        message_id: Optional[str] = None,
        references: Optional[List[str]] = None,
        in_reply_to: Optional[str] = None,
        thread_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str], Optional[float], Optional[str]]:
        """
        Check if an email is a duplicate using semantic content similarity and metadata
        
        Args:
            email_content: The body content of the email
            sender: Email address of the sender
            subject: Email subject line
            recipient: Email recipient(s) address
            received_date: When the email was received
            message_id: Email Message-ID header
            references: Email References header (list of message IDs)
            in_reply_to: Email In-Reply-To header
            thread_id: Optional thread identifier
            ip_address: Sender's IP address if available
            additional_metadata: Any additional metadata to consider
            
        Returns:
            Tuple of (is_duplicate, reason, confidence_score, duplicate_id)
        """
        logger.info(f"Checking duplicate for email from {sender} with subject '{subject}'")
        logger.info(f"Email details: message_id={message_id}, thread_id={thread_id}, ip={ip_address}")
        
        # Clean up expired cache entries
        expired_count = self._cleanup_cache()
        logger.info(f"Cleaned up {expired_count} expired entries from cache")
        
        # Set timestamp if not provided
        current_time = datetime.now()
        logger.info(f"Current time: {current_time.isoformat()}")
        
        if received_date is None:
            received_date = current_time
            logger.info(f"No received_date provided, using current time: {received_date.isoformat()}")
        elif isinstance(received_date, str):
            try:
                received_date = datetime.fromisoformat(received_date)
                logger.info(f"Parsed received_date from string: {received_date.isoformat()}")
            except ValueError:
                logger.warning(f"Could not parse received_date: {received_date}, using current time")
                received_date = current_time
        
        # Get message embeddings
        logger.info("Normalizing email content and subject")
        normalized_content = self._normalize_email(email_content)
        normalized_subject = self._normalize_subject(subject)
        
        logger.info(f"Normalized content length: {len(normalized_content)}")
        logger.info(f"Normalized subject: '{normalized_subject}'")
        
        logger.info("Generating content embedding")
        content_embedding = self.embedding_provider.get_embedding(normalized_content)
        logger.info("Generating subject embedding")
        subject_embedding = self.embedding_provider.get_embedding(normalized_subject)
        
        # Get thread identifier if available
        derived_thread_id = thread_id
        if not derived_thread_id and references:
            derived_thread_id = references[0]  # Use first reference as thread ID
            logger.info(f"Using first reference as thread_id: {derived_thread_id}")
        if not derived_thread_id and in_reply_to:
            derived_thread_id = in_reply_to
            logger.info(f"Using in_reply_to as thread_id: {derived_thread_id}")
        
        # Create a unique ID for this email
        email_id = str(uuid.uuid4())
        if message_id:
            # Use hash of message_id as email_id if available
            email_id = self._generate_hash(message_id)
            logger.info(f"Generated email_id from message_id: {email_id}")
        else:
            logger.info(f"Generated random email_id: {email_id}")
        
        # Check for email with the same Message-ID
        if message_id:
            logger.info(f"Checking for duplicate message_id: {message_id}")
            for cache_key, entry in self.email_cache.items():
                if entry.get('message_id') == message_id:
                    match_time = entry.get('received_date', 'unknown time')
                    logger.info(f"Found exact message_id match: {cache_key} from {entry['sender']} ({match_time})")
                    return True, f"Duplicate message ID from {entry['sender']} ({match_time})", 1.0, entry['id']
        
        # Check for potential duplicates within time window
        logger.info("Checking for potential semantic duplicates")
        potential_duplicates = []
        
        for key, entry in self.email_cache.items():
            logger.info(f"Checking cache entry: {key}")
            
            # Skip if entries are too far apart in time
            entry_time = entry.get('received_date')
            if isinstance(entry_time, str):
                try:
                    entry_time = datetime.fromisoformat(entry_time)
                    logger.info(f"Parsed entry time: {entry_time.isoformat()}")
                except ValueError:
                    logger.warning(f"Could not parse entry received_date: {entry_time}")
                    entry_time = None
            
            if entry_time and isinstance(received_date, datetime):
                # Ensure both datetime objects are comparable (both naive or both aware)
                if received_date.tzinfo is not None and entry_time.tzinfo is None:
                    # Convert entry_time to UTC to match received_date
                    from datetime import timezone
                    entry_time = entry_time.replace(tzinfo=timezone.utc)
                elif received_date.tzinfo is None and entry_time.tzinfo is not None:
                    # Convert received_date to UTC to match entry_time
                    from datetime import timezone
                    received_date = received_date.replace(tzinfo=timezone.utc)
                
                # Now they can be safely compared
                time_diff = abs(received_date - entry_time)
                logger.info(f"Time difference: {time_diff.total_seconds()/3600:.2f} hours")
                
                # Skip if emails are outside our time window
                if time_diff > self.time_window:
                    logger.info(f"Skipping entry {key} - outside time window")
                    continue
            
            # Calculate metadata similarity
            logger.info("Calculating metadata similarity")
            metadata_sim = self._calculate_metadata_similarity(
                sender, recipient, entry.get('sender', ''), entry.get('recipient', ''),
                ip_address, entry.get('ip_address'), derived_thread_id, entry.get('thread_id'),
                additional_metadata, entry.get('additional_metadata')
            )
            logger.info(f"Metadata similarity: {metadata_sim:.4f}")
            
            # Calculate content similarity
            content_sim = 0.0
            if 'content_embedding' in entry:
                logger.info("Calculating content similarity")
                content_sim = self._calculate_embedding_similarity(content_embedding, entry['content_embedding'])
                logger.info(f"Content similarity: {content_sim:.4f}")
            else:
                logger.info("No content embedding in cache entry, skipping content similarity")
            
            # Calculate subject similarity
            subject_sim = 0.0
            if 'subject_embedding' in entry:
                logger.info("Calculating subject similarity")
                subject_sim = self._calculate_embedding_similarity(subject_embedding, entry['subject_embedding'])
                logger.info(f"Subject similarity: {subject_sim:.4f}")
            else:
                logger.info("No subject embedding in cache entry, skipping subject similarity")
            
            # Combined similarity score weighted by importance
            combined_content_sim = (self.content_weight * content_sim + 
                                    self.subject_weight * subject_sim) / (self.content_weight + self.subject_weight)
            logger.info(f"Combined content similarity: {combined_content_sim:.4f}")
            
            # Overall score with metadata and content components
            overall_score = (self.metadata_weight * metadata_sim + 
                           (1 - self.metadata_weight) * combined_content_sim)
            logger.info(f"Overall score before time factor: {overall_score:.4f}")
            
            # Add timing factor - emails closer in time are more likely to be duplicates
            time_factor = 1.0
            if entry_time and isinstance(received_date, datetime):
                # Normalize time difference to a factor between 0.7 and 1.0
                # Closer in time = higher factor
                hours_diff = min(self.time_window.total_seconds() / 3600, time_diff.total_seconds() / 3600)
                max_hours = self.time_window.total_seconds() / 3600
                time_factor = 1.0 - (0.3 * hours_diff / max_hours)
                logger.info(f"Time factor: {time_factor:.4f} (diff: {hours_diff:.2f}h, max: {max_hours:.2f}h)")
            
            final_score = overall_score * time_factor
            logger.info(f"Final similarity score: {final_score:.4f}")
            
            # If sufficient similarity, add to potential duplicates
            if final_score >= 0.5:  # Lower threshold for potential candidates
                logger.info(f"Adding to potential duplicates (score: {final_score:.4f})")
                potential_duplicates.append({
                    'id': entry['id'],
                    'sender': entry['sender'],
                    'subject': entry.get('subject', ''),
                    'received_date': entry_time,
                    'score': final_score,
                    'metadata_sim': metadata_sim,
                    'content_sim': content_sim,
                    'subject_sim': subject_sim,
                    'time_factor': time_factor
                })
            else:
                logger.info(f"Score below threshold (0.5), not adding to potential duplicates")
        
        logger.info(f"Found {len(potential_duplicates)} potential duplicates")
        
        # Sort potential duplicates by score (highest first)
        potential_duplicates.sort(key=lambda x: x['score'], reverse=True)
        
        # If we have potential duplicates, evaluate the best match
        if potential_duplicates:
            best_match = potential_duplicates[0]
            logger.info(f"Best match: id={best_match['id']}, score={best_match['score']:.4f}")
            
            # High confidence duplicate
            if best_match['score'] >= self.semantic_threshold:
                reason = self._generate_duplicate_reason(best_match)
                logger.info(f"High confidence duplicate detected: {reason}")
                return True, reason, best_match['score'], best_match['id']
            
            # Medium confidence duplicate
            elif best_match['score'] >= 0.5:
                reason = f"Likely duplicate of email from {best_match['sender']}"
                if best_match['received_date']:
                    reason += f" (received: {best_match['received_date'].isoformat() if isinstance(best_match['received_date'], datetime) else best_match['received_date']})"
                logger.info(f"Medium confidence duplicate detected: {reason}")
                logger.info(f"adding to cache with id {email_id}")
                # medium confidence duplicates also go into cache
                email_data = {
                    'id': email_id,
                    'content_embedding': content_embedding,
                    'subject_embedding': subject_embedding,
                    'normalized_content': normalized_content,
                    'normalized_subject': normalized_subject,
                    'sender': sender,
                    'recipient': recipient,
                    'subject': subject,
                    'message_id': message_id,
                    'thread_id': derived_thread_id,
                    'received_date': received_date.isoformat() if isinstance(received_date, datetime) else received_date,
                    'ip_address': ip_address,
                    'expiry': (current_time + self.cache_duration).isoformat()
                }
                
                # Add any additional metadata
                if additional_metadata:
                    email_data['additional_metadata'] = additional_metadata
                    logger.info(f"Added additional metadata: {len(additional_metadata)} fields")
                
                # Store in cache
                self.email_cache.put(email_id, email_data)
                return True, reason, best_match['score'], best_match['id']
            
            logger.info(f"Best match score {best_match['score']:.4f} below threshold, not treating as duplicate")
        
        # Not a duplicate, add to cache
        logger.info(f"No duplicate found, adding to cache with id {email_id}")
        email_data = {
            'id': email_id,
            'content_embedding': content_embedding,
            'subject_embedding': subject_embedding,
            'normalized_content': normalized_content,
            'normalized_subject': normalized_subject,
            'sender': sender,
            'recipient': recipient,
            'subject': subject,
            'message_id': message_id,
            'thread_id': derived_thread_id,
            'received_date': received_date.isoformat() if isinstance(received_date, datetime) else received_date,
            'ip_address': ip_address,
            'expiry': (current_time + self.cache_duration).isoformat()
        }
        
        # Add any additional metadata
        if additional_metadata:
            email_data['additional_metadata'] = additional_metadata
            logger.info(f"Added additional metadata: {len(additional_metadata)} fields")
        
        # Store in cache
        self.email_cache.put(email_id, email_data)
        logger.info(f"Email added to cache, new cache size: {len(self.email_cache)}")
        
        return False, None, 0.0, None
    
    def _normalize_email(self, content: str) -> str:
        """Normalize email content for semantic comparison"""
        if not content:
            logger.info("Empty content to normalize")
            return ""
            
        # Remove email forwarding/reply markers
        content = re.sub(r'^>+\s*', '', content, flags=re.MULTILINE)
        
        # Remove signatures and footers (simplified)
        content = re.sub(r'--+\s*\n.*', '', content, flags=re.DOTALL)
        content = re.sub(r'^sent\s+from\s+my\s+.*$', '', content, flags=re.MULTILINE | re.IGNORECASE)
        
        # Remove extra whitespace and line breaks
        content = re.sub(r'\s+', ' ', content).strip()
        
        logger.info(f"Normalized email content from {len(content)} characters")
        return content
    
    def _normalize_subject(self, subject: str) -> str:
        """Normalize email subject for comparison"""
        if not subject:
            logger.info("Empty subject to normalize")
            return ""
            
        original_subject = subject
        
        # Remove reply/forward prefixes
        subject = re.sub(r'^(re|fwd|fw):\s*', '', subject, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        subject = re.sub(r'\s+', ' ', subject).strip()
        
        if subject != original_subject:
            logger.info(f"Normalized subject: '{original_subject}' -> '{subject}'")
        
        return subject
    
    def _generate_hash(self, text: str) -> str:
        """Generate a hash for the text"""
        if not text:
            hash_val = hashlib.md5(b"empty").hexdigest()
            logger.info(f"Generated hash for empty text: {hash_val}")
            return hash_val
            
        hash_val = hashlib.md5(text.encode('utf-8')).hexdigest()
        logger.info(f"Generated hash: {hash_val}")
        return hash_val
    
    def _calculate_embedding_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        if embedding1 is None or embedding2 is None:
            logger.info("Null embedding provided, returning 0 similarity")
            return 0.0
            
        # Reshape for sklearn
        v1 = embedding1.reshape(1, -1)
        v2 = embedding2.reshape(1, -1)
        
        try:
            similarity = float(cosine_similarity(v1, v2)[0][0])
            logger.info(f"Embedding similarity: {similarity:.4f}")
            return similarity
        except Exception as e:
            logger.error(f"Error calculating embedding similarity: {e}")
            return 0.0
    
    def _calculate_metadata_similarity(
        self, 
        sender1: str, 
        recipient1: str, 
        sender2: str, 
        recipient2: str,
        ip1: Optional[str] = None,
        ip2: Optional[str] = None,
        thread_id1: Optional[str] = None,
        thread_id2: Optional[str] = None,
        meta1: Optional[Dict] = None,
        meta2: Optional[Dict] = None
    ) -> float:
        """Calculate similarity between email metadata"""
        logger.info(f"Calculating metadata similarity between {sender1} and {sender2}")
        score = 0.0
        total_weight = 0.0
        
        # Sender match (high weight)
        if sender1 and sender2:
            sender_weight = 0.4
            norm_sender1 = self._normalize_email_address(sender1)
            norm_sender2 = self._normalize_email_address(sender2)
            
            logger.info(f"Normalized senders: '{norm_sender1}' vs '{norm_sender2}'")
            
            if norm_sender1 == norm_sender2:
                score += sender_weight
                logger.info("Exact sender match")
            elif self._get_email_domain(sender1) == self._get_email_domain(sender2):
                # Same domain partial match
                score += sender_weight * 0.5
                logger.info("Same sender domain match")
            total_weight += sender_weight
        
        # Recipient match
        if recipient1 and recipient2:
            recipient_weight = 0.2
            # Normalize and split recipients (could be multiple)
            recip1_set = {self._normalize_email_address(r.strip()) for r in recipient1.split(',') if r.strip()}
            recip2_set = {self._normalize_email_address(r.strip()) for r in recipient2.split(',') if r.strip()}
            
            logger.info(f"Recipients: {recip1_set} vs {recip2_set}")
            
            if recip1_set and recip2_set:
                # Calculate overlap between recipient sets
                overlap = len(recip1_set.intersection(recip2_set))
                total = len(recip1_set.union(recip2_set))
                if total > 0:
                    recipient_score = recipient_weight * (overlap / total)
                    score += recipient_score
                    logger.info(f"Recipient overlap: {overlap}/{total} = {recipient_score:.4f}")
                else:
                    score += 0
                total_weight += recipient_weight
        
        # IP address match (if available)
        if ip1 and ip2:
            ip_weight = 0.1
            logger.info(f"IP addresses: {ip1} vs {ip2}")
            if ip1 == ip2:
                score += ip_weight
                logger.info("IP address match")
            total_weight += ip_weight
        
        # Thread ID match
        if thread_id1 and thread_id2:
            thread_weight = 0.3
            logger.info(f"Thread IDs: {thread_id1} vs {thread_id2}")
            if thread_id1 == thread_id2:
                score += thread_weight
                logger.info("Thread ID match")
            total_weight += thread_weight
        
        # Additional metadata matches
        if meta1 and meta2:
            meta_weight = 0.1
            meta_matches = 0
            meta_total = 0
            
            # Compare common keys
            common_keys = set(meta1.keys()).intersection(set(meta2.keys()))
            logger.info(f"Common metadata keys: {common_keys}")
            
            for key in common_keys:
                meta_total += 1
                if meta1[key] == meta2[key]:
                    meta_matches += 1
                    logger.info(f"Metadata match for key '{key}': {meta1[key]}")
            
            if meta_total > 0:
                meta_score = meta_weight * (meta_matches / meta_total)
                score += meta_score
                logger.info(f"Metadata matches: {meta_matches}/{meta_total} = {meta_score:.4f}")
                total_weight += meta_weight
        
        # Normalize score
        final_score = score / max(total_weight, 0.001)
        logger.info(f"Final metadata similarity: {final_score:.4f} (score={score:.4f}, weight={total_weight:.4f})")
        return final_score
    
    def _normalize_email_address(self, email: str) -> str:
        """Normalize email address for comparison"""
        if not email:
            return ""
        
        # Extract just the email if it's in "Display Name <email>" format
        match = re.search(r'<(.+@.+)>', email)
        if match:
            email = match.group(1)
            logger.info(f"Extracted email from display name format: {email}")
        
        normalized = email.strip().lower()
        return normalized
    
    def _get_email_domain(self, email: str) -> str:
        """Extract domain from email address"""
        email = self._normalize_email_address(email)
        if '@' in email:
            domain = email.split('@')[-1]
            logger.info(f"Extracted domain from {email}: {domain}")
            return domain
        return ""
    
    def _generate_duplicate_reason(self, match: Dict) -> str:
        """Generate a descriptive reason for why this is a duplicate"""
        logger.info(f"Generating duplicate reason for match: {match['id']}")
        reason = f"Duplicate email from {match['sender']}"
        
        if match['received_date']:
            if isinstance(match['received_date'], datetime):
                time_str = match['received_date'].strftime("%Y-%m-%d %H:%M")
            else:
                time_str = str(match['received_date'])
            reason += f" (received: {time_str})"
        
        if match.get('subject'):
            reason += f" with subject '{match['subject']}'"
        
        # Add information about the match criteria
        details = []
        if match.get('metadata_sim', 0) > 0.8:
            details.append("matching metadata")
        if match.get('content_sim', 0) > 0.8:
            details.append("similar content")
        if match.get('subject_sim', 0) > 0.8:
            details.append("similar subject")
            
        if details:
            reason += f" ({', '.join(details)})"
        
        logger.info(f"Generated duplicate reason: {reason}")
        return reason
    
    def _cleanup_cache(self) -> int:
        """Remove expired entries from the cache"""
        now = datetime.now()
        expired_keys = []
        
        logger.info(f"Cleaning up cache with {len(self.email_cache)} entries")
        
        for key, entry in self.email_cache.items():
            if 'expiry' in entry:
                try:
                    if isinstance(entry['expiry'], str):
                        expiry = datetime.fromisoformat(entry['expiry'])
                    else:
                        expiry = entry['expiry']
                    
                    if expiry < now:
                        expired_keys.append(key)
                        logger.info(f"Found expired entry: {key}, expiry: {expiry}")
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid expiry format in cache entry {key}: {e}")
        
        for key in expired_keys:
            self.email_cache.remove(key)
            
        if expired_keys:
            logger.info(f"Removed {len(expired_keys)} expired entries from email cache")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the detector state"""
        stats = {
            "cache_size": len(self.email_cache),
            "configuration": {
                "semantic_threshold": self.semantic_threshold,
                "metadata_weight": self.metadata_weight,
                "subject_weight": self.subject_weight,
                "content_weight": self.content_weight,
                "time_window_hours": self.time_window.total_seconds() / 3600
            }
        }
        
        logger.info(f"Current detector stats: cache_size={stats['cache_size']}")
        return stats
    
    def save_state(self, file_path: str) -> bool:
        """Save detector state to a file"""
        try:
            logger.info(f"Saving detector state to {file_path}")
            state = {
                "configuration": {
                    "semantic_threshold": self.semantic_threshold,
                    "metadata_weight": self.metadata_weight,
                    "subject_weight": self.subject_weight,
                    "content_weight": self.content_weight,
                    "time_window_hours": self.time_window.total_seconds() / 3600
                },
                "cache": {}
            }
            
            # Convert cache entries to serializable format
            for key, entry in self.email_cache.items():
                serializable_entry = {}
                for k, v in entry.items():
                    if isinstance(v, np.ndarray):
                        serializable_entry[k] = v.tolist()
                        logger.info(f"Converted numpy array to list for key {k}")
                    else:
                        serializable_entry[k] = v
                state["cache"][key] = serializable_entry
            
            with open(file_path, 'w') as f:
                json.dump(state, f)
            
            logger.info(f"Successfully saved state with {len(state['cache'])} cache entries")
            return True
        except Exception as e:
            logger.error(f"Error saving state to {file_path}: {e}")
            return False
    
    def load_state(self, file_path: str) -> bool:
        """Load detector state from a file"""
        try:
            logger.info(f"Loading detector state from {file_path}")
            with open(file_path, 'r') as f:
                state = json.load(f)
            
            # Restore configuration
            if "configuration" in state:
                config = state["configuration"]
                logger.info(f"Loaded configuration: {config}")
                self.semantic_threshold = config.get("semantic_threshold", self.semantic_threshold)
                self.metadata_weight = config.get("metadata_weight", self.metadata_weight)
                self.subject_weight = config.get("subject_weight", self.subject_weight)
                self.content_weight = config.get("content_weight", self.content_weight)
                
                time_window_hours = config.get("time_window_hours")
                if time_window_hours:
                    self.time_window = timedelta(hours=time_window_hours)
            
            # Restore cache
            if "cache" in state:
                cache_count = 0
                for key, entry in state["cache"].items():
                    # Convert array lists back to numpy arrays
                    for k, v in entry.items():
                        if k.endswith('_embedding') and isinstance(v, list):
                            entry[k] = np.array(v)
                            logger.info(f"Converted list back to numpy array for {k}")
                    
                    self.email_cache.put(key, entry)
                    cache_count += 1
                
                logger.info(f"Restored {cache_count} cache entries")
            
            logger.info(f"Successfully loaded state from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading state from {file_path}: {e}")
            return False