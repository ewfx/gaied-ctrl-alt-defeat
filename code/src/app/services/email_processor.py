import os
import io
import re
import email as email_module  # Renamed the import to avoid conflict
from typing import List, Dict, Any, Tuple
from email.parser import Parser
from email.policy import default
import logging
from datetime import datetime
import socket

# Document processing
import pypdf
from bs4 import BeautifulSoup
from PIL import Image
import numpy as np
import easyocr

logger = logging.getLogger(__name__)

class EmailProcessor:
    """
    Service for processing email content and attachments to extract text
    """
    
    def __init__(self, max_attachment_size_mb: int = 10):
        """
        Initialize the email processor
        """
        self.max_attachment_size = max_attachment_size_mb * 1024 * 1024  # Convert to bytes
    
    def process_email_chain(self,
                           email_chain_content: bytes,
                           email_chain_filename: str,
                           email_chain_content_type: str,
                           attachments: List[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], List[Dict[str, str]]]:
        """
        Process email chain from PDF and separate attachments
        """
        # Extract email chain information from PDF
        email_text = self._extract_text_from_pdf(email_chain_content)
        
        # Try to extract email metadata from the PDF content
        email_info = self._extract_email_metadata_from_text(email_text)
        
        if not email_info.get("subject"):
            # If metadata extraction fails, use filename as subject
            email_info["subject"] = os.path.splitext(email_chain_filename)[0]
        
        # Add additional fields for IntelligentDuplicateDetector
        email_info["content"] = email_text
        email_info["recipient"] = self._extract_recipient_from_text(email_text)
        
        # Add default values for additional IntelligentDuplicateDetector fields
        self._add_default_metadata_fields(email_info)
        
        # Try to extract IP address information (if available)
        email_info["ip_address"] = self._extract_ip_address_from_text(email_text)
        
        # Process attachments if any
        processed_attachments = []
        if attachments:
            for idx, attachment in enumerate(attachments):
                try:
                    logger.info(f"Processing attachment: {attachment['filename']}")
                    # Check attachment size
                    if len(attachment["content"]) > self.max_attachment_size:
                        logger.warning(f"Attachment too large: {attachment['filename']} ({len(attachment['content'])/1024/1024:.2f} MB)")
                        processed_text = f"[Attachment too large: {attachment['filename']}]"
                    else:
                        processed_text = self.process_attachment(
                            attachment["content"],
                            attachment["filename"],
                            attachment["content_type"]
                        )
                    
                    processed_attachments.append({
                        "index": idx + 1,
                        "filename": attachment["filename"],
                        "content_type": attachment["content_type"],
                        "text": processed_text
                    })
                except Exception as e:
                    logger.error(f"Error processing attachment {attachment['filename']}: {str(e)}")
                    processed_attachments.append({
                        "index": idx + 1,
                        "filename": attachment["filename"],
                        "content_type": attachment["content_type"],
                        "text": f"[Error processing attachment: {str(e)}]"
                    })
        
        return email_info, processed_attachments
    
    def process_eml(self, eml_content: bytes) -> Tuple[Dict[str, Any], List[Dict[str, str]]]:
        """
        Process EML file containing email with attachments
        Enhanced to extract detailed metadata for IntelligentDuplicateDetector
        """
        try:
            # Parse the EML content
            eml_text = eml_content.decode('utf-8', errors='ignore')
            email_message = email_module.message_from_string(eml_text, policy=default)  # Use renamed module
            
            # Extract metadata
            email_info = {
                "sender": str(email_message.get("From", "")),
                "subject": str(email_message.get("Subject", "")),
                "received_date": str(email_message.get("Date", "")),
                "content": "",
                "recipient": str(email_message.get("To", "")),
                "message_id": str(email_message.get("Message-ID", "")),
                "in_reply_to": str(email_message.get("In-Reply-To", "")),
                "references": self._parse_references_header(str(email_message.get("References", ""))),
                "thread_id": None  # Will be derived later
            }
            
            # Extract other headers that might contain IP information
            received_headers = email_message.get_all("Received")
            if received_headers:
                email_info["ip_address"] = self._extract_ip_from_received_headers(received_headers)
            else:
                email_info["ip_address"] = None
            
            # Extract additional headers for metadata
            additional_metadata = {}
            for header in ["X-Mailer", "User-Agent", "X-Originating-IP", "X-Forwarded-For"]:
                if email_message.get(header):
                    additional_metadata[header] = str(email_message.get(header))
            
            if additional_metadata:
                email_info["additional_metadata"] = additional_metadata
            
            # Extract email body and attachments
            processed_attachments = []
            attachment_idx = 0
            
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition", ""))
                    
                    # Extract body content
                    if "attachment" not in content_disposition and part.get_payload(decode=True) is not None:
                        if content_type == "text/plain":
                            email_info["content"] += part.get_payload(decode=True).decode('utf-8', errors='ignore') + "\n\n"
                        elif content_type == "text/html":
                            html_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            email_info["content"] += self._extract_text_from_html(html_content) + "\n\n"
                    
                    # Extract attachments
                    elif "attachment" in content_disposition or "inline" in content_disposition:
                        try:
                            attachment_idx += 1
                            filename = part.get_filename()
                            if not filename:
                                filename = f"attachment_{attachment_idx}.{content_type.split('/')[-1]}"
                            
                            attachment_content = part.get_payload(decode=True)
                            if attachment_content and len(attachment_content) <= self.max_attachment_size:
                                # Process the attachment
                                processed_text = self.process_attachment(
                                    attachment_content,
                                    filename,
                                    content_type
                                )
                                
                                processed_attachments.append({
                                    "index": attachment_idx,
                                    "filename": filename,
                                    "content_type": content_type,
                                    "text": processed_text
                                })
                            else:
                                logger.warning(f"Attachment too large or empty: {filename}")
                                processed_attachments.append({
                                    "index": attachment_idx,
                                    "filename": filename,
                                    "content_type": content_type,
                                    "text": f"[Attachment too large or empty: {filename}]"
                                })
                        except Exception as e:
                            logger.error(f"Error processing attachment: {str(e)}")
                            processed_attachments.append({
                                "index": attachment_idx,
                                "filename": f"unknown_attachment_{attachment_idx}",
                                "content_type": content_type,
                                "text": f"[Error processing attachment: {str(e)}]"
                            })
            else:
                # Handle non-multipart email
                content_type = email_message.get_content_type()
                if content_type == "text/plain":
                    email_info["content"] = email_message.get_content()
                elif content_type == "text/html":
                    html_content = email_message.get_content()
                    email_info["content"] = self._extract_text_from_html(html_content)
            
            # Clean the extracted text
            email_info["content"] = self._clean_text(email_info["content"])
            
            # Derive thread_id if available
            if email_info["references"] and len(email_info["references"]) > 0:
                email_info["thread_id"] = email_info["references"][0]  # Use first reference as thread ID
            elif email_info["in_reply_to"]:
                email_info["thread_id"] = email_info["in_reply_to"]
            
            # Normalize received_date to ISO format if possible
            if email_info["received_date"]:
                try:
                    # Try to parse date with email.utils
                    import email.utils
                    parsed_date = email_module.utils.parsedate_to_datetime(email_info["received_date"])
                    if parsed_date:
                        email_info["received_date"] = parsed_date.isoformat()
                except Exception as date_error:
                    logger.warning(f"Could not parse received date: {date_error}")
            
            return email_info, processed_attachments
            
        except Exception as e:
            logger.error(f"Error processing EML: {str(e)}", exc_info=True)
            # Fallback to basic processing
            email_info = {
                "sender": "Unknown",
                "subject": "Unknown",
                "received_date": datetime.now().isoformat(),
                "content": self.process_email_content(eml_content.decode('utf-8', errors='ignore')),
                "recipient": "",
                "message_id": None,
                "references": [],
                "in_reply_to": None,
                "thread_id": None,
                "ip_address": None
            }
            return email_info, []
    
    def _parse_references_header(self, references_header: str) -> List[str]:
        """Parse References header into a list of message IDs"""
        if not references_header:
            return []
        
        # Split by whitespace and filter empty strings
        return [ref.strip() for ref in re.split(r'\s+', references_header) if ref.strip()]
    
    def _extract_ip_from_received_headers(self, received_headers: List[str]) -> str:
        """Extract IP address from Received headers"""
        for header in received_headers:
            # Look for patterns like [ip.address], ip.address, or 'from' ip.address
            ip_patterns = [
                r'\[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]',
                r'from\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
                r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            ]
            
            for pattern in ip_patterns:
                match = re.search(pattern, header)
                if match:
                    ip = match.group(1)
                    # Validate it's a real IP address
                    try:
                        socket.inet_aton(ip)
                        return ip
                    except socket.error:
                        continue
        
        return None
    
    def process_attachment(self, 
                          content: bytes, 
                          filename: str, 
                          content_type: str = None) -> str:
        """
        Process attachment file content based on file type
        """
        file_extension = os.path.splitext(filename.lower())[1]
        
        try:
            # Process by file extension
            if file_extension == '.pdf':
                return self._extract_text_from_pdf(content)
            elif file_extension in ['.doc', '.docx']:
                return self._extract_text_from_docx(content)
            elif file_extension == '.txt':
                return content.decode('utf-8', errors='ignore')
            elif file_extension == '.eml':
                # Process as nested email
                email_info, _ = self.process_eml(content)
                return email_info.get("content", "")
            elif file_extension in ['.htm', '.html']:
                return self._extract_text_from_html(content.decode('utf-8', errors='ignore'))
            elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                # Image files - extract text with OCR
                return self._extract_text_from_image(content)
            else:
                # Check content type as fallback
                if content_type and 'pdf' in content_type:
                    return self._extract_text_from_pdf(content)
                elif content_type and 'html' in content_type:
                    return self._extract_text_from_html(content.decode('utf-8', errors='ignore'))
                elif content_type and 'text/plain' in content_type:
                    return content.decode('utf-8', errors='ignore')
                
                return f"[Unsupported file type: {file_extension}]"
        except Exception as e:
            logger.error(f"Error processing attachment {filename}: {str(e)}")
            return f"[Error processing attachment {filename}: {str(e)}]"
    
    def process_email_content(self, content: str) -> str:
        """
        Process raw email content to extract the text body
        """
        # Basic cleaning
        text = self._clean_text(content)
        
        # Try to parse as email if it contains headers
        if "From:" in text or "Subject:" in text or "To:" in text:
            try:
                email_message = Parser(policy=default).parsestr(content)
                body = ""
                
                # Handle multipart emails
                if email_message.is_multipart():
                    for part in email_message.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        
                        # Skip attachments
                        if "attachment" in content_disposition:
                            continue
                            
                        if content_type == "text/plain":
                            body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        elif content_type == "text/html":
                            # Extract text from HTML
                            html_body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            body += self._extract_text_from_html(html_body)
                else:
                    # Handle plain text emails
                    content_type = email_message.get_content_type()
                    if content_type == "text/plain":
                        body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                    elif content_type == "text/html":
                        html_body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                        body = self._extract_text_from_html(html_body)
                    else:
                        body = email_message.get_payload()
                        
                if body:
                    return self._clean_text(body)
            except Exception as e:
                logger.error(f"Error parsing email: {e}")
                # Fall back to returning the raw content
        
        return text
    
    def _extract_email_metadata_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract email metadata (sender, subject, date, message-id, etc.) from text content
        """
        metadata = {
            "sender": "",
            "subject": "",
            "received_date": "",
            "recipient": "",
            "message_id": None,
            "in_reply_to": None,
            "references": [],
            "thread_id": None,
            "ip_address": None
        }
        
        # Try to extract common email headers
        sender_match = re.search(r'From:\s*([^\n]+)', text, re.IGNORECASE)
        if sender_match:
            metadata["sender"] = sender_match.group(1).strip()
        
        subject_match = re.search(r'Subject:\s*([^\n]+)', text, re.IGNORECASE)
        if subject_match:
            metadata["subject"] = subject_match.group(1).strip()
        
        date_match = re.search(r'Date:\s*([^\n]+)', text, re.IGNORECASE)
        if date_match:
            metadata["received_date"] = date_match.group(1).strip()
            # Try to normalize date format if possible
            try:
                # Use email_module instead of email directly
                parsed_date = email_module.utils.parsedate_to_datetime(metadata["received_date"])
                if parsed_date:
                    metadata["received_date"] = parsed_date.isoformat()
            except Exception:
                pass  # Keep original format if parsing fails
        
        # Extract recipient
        to_match = re.search(r'To:\s*([^\n]+)', text, re.IGNORECASE)
        if to_match:
            metadata["recipient"] = to_match.group(1).strip()
        
        # Extract Message-ID
        msgid_match = re.search(r'Message-ID:\s*([^\n]+)', text, re.IGNORECASE)
        if msgid_match:
            metadata["message_id"] = msgid_match.group(1).strip()
        
        # Extract In-Reply-To
        reply_match = re.search(r'In-Reply-To:\s*([^\n]+)', text, re.IGNORECASE)
        if reply_match:
            metadata["in_reply_to"] = reply_match.group(1).strip()
        
        # Extract References
        ref_match = re.search(r'References:\s*([^\n]+)', text, re.IGNORECASE)
        if ref_match:
            refs = ref_match.group(1).strip()
            metadata["references"] = [r.strip() for r in re.split(r'\s+', refs) if r.strip()]
        
        # Extract thread ID if available, or derive it
        if metadata["references"] and len(metadata["references"]) > 0:
            metadata["thread_id"] = metadata["references"][0]
        elif metadata["in_reply_to"]:
            metadata["thread_id"] = metadata["in_reply_to"]
        
        # Extract IP address
        metadata["ip_address"] = self._extract_ip_address_from_text(text)
        
        return metadata
    
    def _extract_recipient_from_text(self, text: str) -> str:
        """Extract recipient from email text"""
        to_match = re.search(r'To:\s*([^\n]+)', text, re.IGNORECASE)
        if to_match:
            return to_match.group(1).strip()
        
        # Try alternative patterns
        cc_match = re.search(r'Cc:\s*([^\n]+)', text, re.IGNORECASE)
        if cc_match:
            return cc_match.group(1).strip()
        
        # Extract any email address pattern as a last resort
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match and email_match.group(0) not in text.split("From:", 1)[0]:
            return email_match.group(0)
        
        return ""
    
    def _extract_ip_address_from_text(self, text: str) -> str:
        """Extract IP address from email text"""
        # Look for common patterns that contain IP addresses
        ip_patterns = [
            r'Received:.*?\[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]',
            r'X-Originating-IP:\s*\[?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]?',
            r'from\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        ]
        
        for pattern in ip_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                ip = match.group(1)
                # Validate it's a real IP address
                try:
                    socket.inet_aton(ip)
                    return ip
                except socket.error:
                    continue
        
        return None
    
    def _add_default_metadata_fields(self, email_info: Dict[str, Any]) -> None:
        """Add default metadata fields required by IntelligentDuplicateDetector if missing"""
        # Ensure all required fields exist
        if "message_id" not in email_info:
            email_info["message_id"] = None
            
        if "references" not in email_info:
            email_info["references"] = []
            
        if "in_reply_to" not in email_info:
            email_info["in_reply_to"] = None
            
        if "thread_id" not in email_info:
            email_info["thread_id"] = None
            
        if "ip_address" not in email_info:
            email_info["ip_address"] = None
            
        # Set current time as received_date if not present
        if not email_info.get("received_date"):
            email_info["received_date"] = datetime.now().isoformat()
    
    def _extract_text_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF file content"""
        text = ""
        try:
            pdf_file = io.BytesIO(content)
            pdf_reader = pypdf.PdfReader(pdf_file)
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
                
            return self._clean_text(text)
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            return f"[Error extracting PDF text: {str(e)}]"
    
    def _extract_text_from_html(self, html_content: str) -> str:
        """Extract text from HTML content using BeautifulSoup"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
                
            # Get text
            text = soup.get_text(separator=' ')
            
            # Clean text
            return self._clean_text(text)
        except Exception as e:
            logger.error(f"Error extracting HTML text: {str(e)}")
            # Fall back to basic regex approach
            text = re.sub(r'<[^>]+>', ' ', html_content)
            return self._clean_text(text)
    
    def _extract_text_from_image(self, image_content: bytes) -> str:
        """Extract text from image file content using EasyOCR"""
        try:
            reader = easyocr.Reader(['en'])
            
            # Convert bytes to a numpy array
            image = np.array(Image.open(io.BytesIO(image_content)))
            
            # Use EasyOCR to extract text
            result = reader.readtext(image, detail=0)
            text = ' '.join(result)
            return self._clean_text(text)
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            return f"[Error extracting text from image: {str(e)}]"
    
    def _extract_text_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX file content"""
        # Simplified implementation to avoid additional dependencies
        return "[Word document content - text extraction simplified]"
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
            
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove excessive line breaks
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove email forwarding/reply markers
        text = re.sub(r'^>+\s*', '', text, flags=re.MULTILINE)
        
        # Remove common email signature indicators
        text = re.sub(r'--+\s*\n.*$', '', text, flags=re.DOTALL)
        
        # Replace special characters and normalize
        text = text.replace('\r', '\n')
        text = re.sub(r'\t', ' ', text)
        
        return text.strip()