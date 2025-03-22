import json
import time
import logging
from typing import Dict, List, Any, Optional

from langchain.schema.messages import SystemMessage, HumanMessage

from app.core.llm_handler import LLMHandler
from app.services.email_processor import EmailProcessor
from app.services.duplicate_detector import DuplicateDetector
from app.services.data_extractor import DataExtractor
from app.models.response_models import ClassificationResponse, RequestTypeResult

logger = logging.getLogger(__name__)

class ClassificationService:
    """
    Service for orchestrating the email classification workflow
    """
    
    def __init__(self, 
                llm_handler: LLMHandler,
                email_processor: EmailProcessor,
                duplicate_detector: DuplicateDetector,
                data_extractor: DataExtractor,
                request_types: List[Dict[str, Any]],
                extraction_rules: Dict[str, Any]):
        """
        Initialize the classification service
        
        Args:
            llm_handler: LLM handler for LLM interactions
            email_processor: Service for processing emails and attachments
            duplicate_detector: Service for detecting duplicate emails
            data_extractor: Service for extracting data from emails
            request_types: List of request type definitions
            extraction_rules: Dictionary of extraction rules by request type
        """
        self.llm_handler = llm_handler
        self.email_processor = email_processor
        self.duplicate_detector = duplicate_detector
        self.data_extractor = data_extractor
        self.request_types = request_types
        self.extraction_rules = extraction_rules
        logger.info("Classification service initialized")
    
    async def process_email(self, 
                          email_content: str,
                          sender: str,
                          subject: str,
                          received_date: str,
                          attachments: List[Dict[str, Any]] = None,
                          thread_id: Optional[str] = None) -> ClassificationResponse:
        """
        Process an email through the full classification workflow
        
        Args:
            email_content: Raw email content
            sender: Email sender
            subject: Email subject
            received_date: Date when email was received (ISO format)
            attachments: List of attachment objects
            thread_id: Optional thread ID for duplicate detection
            
        Returns:
            ClassificationResponse with results
        """
        start_time = time.time()
        
        try:
            # Process email and attachments
            logger.info(f"Processing email from {sender} with subject: {subject}")
            processed_email, processed_attachments = self.email_processor.process_email(
                email_content, attachments
            )
            
            # Check for duplicates
            is_duplicate, duplicate_reason = self.duplicate_detector.check_duplicate(
                processed_email, sender, subject, thread_id
            )
            
            if is_duplicate:
                logger.info(f"Duplicate email detected: {duplicate_reason}")
                # Return early for duplicates
                return ClassificationResponse(
                    request_types=[],
                    extracted_fields=[],
                    is_duplicate=True,
                    duplicate_reason=duplicate_reason,
                    processing_time_ms=(time.time() - start_time) * 1000
                )
            
            # Identify request types
            request_type_results = await self._identify_request_types(
                processed_email,
                processed_attachments,
                sender,
                subject,
                received_date
            )
            
            # Extract fields based on identified request types
            extracted_fields = []
            if request_type_results:
                # Find primary request type
                primary_request = next(
                    (r for r in request_type_results if r.is_primary), 
                    request_type_results[0] if request_type_results else None
                )
                
                if primary_request:
                    extracted_fields = await self.data_extractor.extract_fields(
                        processed_email,
                        processed_attachments,
                        primary_request.request_type,
                        primary_request.sub_request_type,
                        self.extraction_rules
                    )
            
            processing_time = (time.time() - start_time) * 1000
            logger.info(f"Email processing completed in {processing_time:.2f}ms")
            
            return ClassificationResponse(
                request_types=request_type_results,
                extracted_fields=extracted_fields,
                is_duplicate=False,
                duplicate_reason=None,
                processing_time_ms=processing_time
            )
                
        except Exception as e:
            logger.error(f"Error processing email: {str(e)}")
            processing_time = (time.time() - start_time) * 1000
            
            return ClassificationResponse(
                request_types=[],
                extracted_fields=[],
                is_duplicate=False,
                duplicate_reason=None,
                processing_time_ms=processing_time,
                error=f"Error processing email: {str(e)}"
            )
    
    async def _identify_request_types(self,
                                    email_content: str,
                                    attachments: List[Dict[str, str]],
                                    sender: str,
                                    subject: str,
                                    received_date: str) -> List[RequestTypeResult]:
        """
        Identify request types from email content and attachments
        
        Args:
            email_content: Processed email content
            attachments: List of processed attachments
            sender: Email sender
            subject: Email subject
            received_date: Email received date
            
        Returns:
            List of request type results
        """
        try:
            # Format request types for prompt
            request_types_str = json.dumps(self.request_types, indent=2)
            
            # Format attachments for prompt
            attachments_str = ""
            for attachment in attachments:
                # Truncate very long attachments
                text = attachment["text"]
                attachments_str += f"\n\nATTACHMENT {attachment['index']}: {attachment['filename']}\n{text}"
            
            # Create system prompt
            system_prompt = f"""You are an AI assistant specializing in classifying banking service emails.

TASK:
Analyze the provided email and attachments to identify all request types and sub-request types based on the sender's intent.
Determine which request is the primary intent if multiple are present.

AVAILABLE REQUEST TYPES:
{request_types_str}

YOUR RESPONSE MUST BE A VALID JSON ARRAY of objects with this structure:
[
  {{
    "request_type": "Main request type",
    "sub_request_type": "Sub-request type",
    "confidence": 0.95,
    "reasoning": "Detailed explanation for why this classification was chosen",
    "is_primary": true
  }},
  ...
]

RULES:
- Prioritize the email content over attachments for determining request type
- The primary request should represent the sender's main intent
- Provide confidence scores between 0 and 1 (higher = more confident)
- Include detailed reasoning for each classification
- Only one request type should be marked as primary (is_primary: true)
- If multiple request types are present, rank them by relevance
- If you're unsure, use a lower confidence score
- Match request types exactly as provided in the available types
"""
            
            # Create human prompt
            human_prompt = f"""EMAIL METADATA:
- Sender: {sender}
- Subject: {subject}
- Received Date: {received_date}

EMAIL CONTENT:
{email_content}
{attachments_str}

Based on the above email content and attachments, identify all request types and sub-request types.
"""
            
            # Get LLM for classification
            llm = self.llm_handler.get_llm("email_classification")
            
            # Get response from LLM
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = await llm.ainvoke(messages)
            response_content = response.content
            
            # Parse the response
            try:
                identified_types = json.loads(response_content)
                
                # Validate and convert to model objects
                result_types = []
                for item in identified_types:
                    # Ensure required fields are present
                    if all(k in item for k in ["request_type", "sub_request_type", "confidence", "reasoning"]):
                        result_types.append(RequestTypeResult(
                            request_type=item["request_type"],
                            sub_request_type=item["sub_request_type"],
                            confidence=float(item["confidence"]),
                            reasoning=item["reasoning"],
                            is_primary=bool(item.get("is_primary", False))
                        ))
                
                # Ensure one primary request type
                primary_found = False
                for item in result_types:
                    if item.is_primary:
                        primary_found = True
                        break
                
                # If no primary type was marked, mark the first one
                if not primary_found and result_types:
                    result_types[0].is_primary = True
                
                logger.info(f"Identified {len(result_types)} request types")
                return result_types
                
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing LLM response: {str(e)}")
                logger.debug(f"Raw response: {response_content}")
                
                # Try to fix JSON with OutputFixingParser
                from langchain.output_parsers import OutputFixingParser
                fixing_parser = OutputFixingParser.from_llm(llm=llm)
                
                try:
                    fixed_json = fixing_parser.parse(response_content)
                    result_types = []
                    
                    for item in fixed_json:
                        result_types.append(RequestTypeResult(
                            request_type=item["request_type"],
                            sub_request_type=item["sub_request_type"],
                            confidence=float(item["confidence"]),
                            reasoning=item["reasoning"],
                            is_primary=bool(item.get("is_primary", False))
                        ))
                    
                    # Ensure one primary request type
                    if not any(r.is_primary for r in result_types) and result_types:
                        result_types[0].is_primary = True
                    
                    logger.info(f"Fixed JSON and identified {len(result_types)} request types")
                    return result_types
                    
                except Exception as e2:
                    logger.error(f"Error fixing JSON: {str(e2)}")
                    return []
                
        except Exception as e:
            logger.error(f"Error identifying request types: {str(e)}")
            return []