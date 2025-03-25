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
from app.schemas.request_types import request_type_collection
from app.schemas.analytics import analytics_collection
from datetime import datetime

logger = logging.getLogger(__name__)

class ClassificationService:
    """
    Service for orchestrating the email classification workflow
    """
    
    def __init__(self, 
                llm_handler: LLMHandler,
                email_processor: EmailProcessor,
                duplicate_detector: DuplicateDetector,
                data_extractor: DataExtractor):
        """
        Initialize the classification service
        """
        self.llm_handler = llm_handler
        self.email_processor = email_processor
        self.duplicate_detector = duplicate_detector
        self.data_extractor = data_extractor
        logger.info("Classification service initialized")
    
    async def process_email_chain(self,
                              email_chain_file: bytes,
                              email_chain_filename: str,
                              email_chain_content_type: str,
                              attachments: List[Dict[str, Any]] = None,
                              thread_id: Optional[str] = None) -> ClassificationResponse:
        """
        Process an email chain from a PDF file with separate attachments
        """
        start_time = time.time()
        
        try:
            # Check file size once at the service level
            if len(email_chain_file) > self.email_processor.max_attachment_size:
                raise ValueError(f"Email chain file exceeds maximum size of {self.email_processor.max_attachment_size_mb}MB")
            
            # Check attachment size and throw early if any exceeds
            if attachments:
                for attachment in attachments:
                    if len(attachment["content"]) > self.email_processor.max_attachment_size:
                        raise ValueError(f"Attachment {attachment['filename']} exceeds maximum size of {self.email_processor.max_attachment_size_mb}MB")
                    
            # Process email chain file and attachments
            logger.info(f"Processing email chain from file: {email_chain_filename}")
            email_info, processed_attachments = self.email_processor.process_email_chain(
                email_chain_file,
                email_chain_filename,
                email_chain_content_type,
                attachments
            )
            
            # Extract metadata
            sender = email_info.get("sender", "Unknown")
            subject = email_info.get("subject", "Unknown")
            received_date = email_info.get("received_date", "")
            processed_email = email_info.get("content", "")
            
            # Check for duplicates
            is_duplicate, duplicate_reason = self.duplicate_detector.check_duplicate(
                processed_email, sender, subject, thread_id
            )
            
            if is_duplicate:
                logger.info(f"Duplicate email detected: {duplicate_reason}")
                return ClassificationResponse(
                    request_types=[],
                    extracted_fields=[],
                    is_duplicate=True,
                    duplicate_reason=duplicate_reason,
                    processing_time_ms=(time.time() - start_time) * 1000
                )
            
            # Get request types from MongoDB
            request_types = await self._get_request_types_from_db()
            
            # Identify request types
            request_type_results = await self._identify_request_types(
                processed_email,
                processed_attachments,
                sender,
                subject,
                received_date,
                request_types
            )
            
            # Extract fields based on identified request types
            extracted_fields = []
            support_group = ""
            
            if request_type_results:
                # Find primary request type
                primary_request = next(
                    (r for r in request_type_results if r.is_primary), 
                    request_type_results[0] if request_type_results else None
                )
                
                if primary_request:
                    # Get required attributes for the sub-request type
                    required_attributes, support_group = await self._get_required_attributes(
                        primary_request.request_type,
                        primary_request.sub_request_type
                    )
                    
                    extracted_fields = await self.data_extractor.extract_fields(
                        processed_email,
                        processed_attachments,
                        primary_request.request_type,
                        primary_request.sub_request_type,
                        required_attributes
                    )
            
            processing_time = (time.time() - start_time) * 1000
            logger.info(f"Email chain processing completed in {processing_time:.2f}ms")
            
            if not request_types:
                raise Exception("No request type found")
            
            if not primary_request:
                primary_request = request_types[0]
            
            
            await analytics_collection.insert_one(
                {
                    "request_type": primary_request.request_type,
                    "sub_request_type": primary_request.sub_request_type,
                    "support_group": support_group,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            
            return ClassificationResponse(
                request_types=request_type_results,
                extracted_fields=extracted_fields,
                support_group=support_group,
                is_duplicate=False,
                duplicate_reason=None,
                processing_time_ms=processing_time
            )
                
        except Exception as e:
            logger.error(f"Error processing email chain: {str(e)}")
            processing_time = (time.time() - start_time) * 1000
            
            return ClassificationResponse(
                request_types=[],
                extracted_fields=[],
                support_group="",
                is_duplicate=False,
                duplicate_reason=None,
                processing_time_ms=processing_time,
                error=f"Error processing email chain: {str(e)}"
            )
    
    async def process_eml(self,
                        eml_content: bytes,
                        thread_id: Optional[str] = None) -> ClassificationResponse:
        """
        Process an email from an EML file
        """
        start_time = time.time()
        
        try:
            # Check file size once at the service level
            if len(eml_content) > self.email_processor.max_attachment_size:
                raise ValueError(f"EML file exceeds maximum size of {self.email_processor.max_attachment_size_mb}MB")
            
            # Process EML file
            logger.info("Processing email from EML file")
            email_info, processed_attachments = self.email_processor.process_eml(eml_content)
            
            # Extract metadata
            sender = email_info.get("sender", "Unknown")
            subject = email_info.get("subject", "Unknown")
            received_date = email_info.get("received_date", "")
            processed_email = email_info.get("content", "")
            
            # Check for duplicates
            is_duplicate, duplicate_reason = self.duplicate_detector.check_duplicate(
                processed_email, sender, subject, thread_id
            )
            
            if is_duplicate:
                logger.info(f"Duplicate email detected: {duplicate_reason}")
                return ClassificationResponse(
                    request_types=[],
                    extracted_fields=[],
                    is_duplicate=True,
                    duplicate_reason=duplicate_reason,
                    processing_time_ms=(time.time() - start_time) * 1000
                )
            
            # Get request types from MongoDB
            request_types = await self._get_request_types_from_db()
            
            # Identify request types
            request_type_results = await self._identify_request_types(
                processed_email,
                processed_attachments,
                sender,
                subject,
                received_date,
                request_types
            )
            
            # Extract fields based on identified request types
            extracted_fields = []
            support_group = ""
            if request_type_results:
                # Find primary request type
                primary_request = next(
                    (r for r in request_type_results if r.is_primary), 
                    request_type_results[0] if request_type_results else None
                )
                
                if primary_request:
                    # Get required attributes for the sub-request type
                    required_attributes, support_group = await self._get_required_attributes(
                        primary_request.request_type,
                        primary_request.sub_request_type
                    )
                    
                    extracted_fields = await self.data_extractor.extract_fields(
                        processed_email,
                        processed_attachments,
                        primary_request.request_type,
                        primary_request.sub_request_type,
                        required_attributes
                    )
            
            processing_time = (time.time() - start_time) * 1000
            logger.info(f"EML processing completed in {processing_time:.2f}ms")
            
            if not request_types:
                raise Exception("No request type found")
            
            if not primary_request:
                primary_request = request_types[0]
            
            
            await analytics_collection.insert_one(
                {
                    "request_type": primary_request.request_type,
                    "sub_request_type": primary_request.sub_request_type,
                    "support_group": support_group,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            
            
            return ClassificationResponse(
                request_types=request_type_results,
                extracted_fields=extracted_fields,
                support_group=support_group,
                is_duplicate=False,
                duplicate_reason=None,
                processing_time_ms=processing_time
            )
                
        except Exception as e:
            logger.error(f"Error processing EML: {str(e)}")
            processing_time = (time.time() - start_time) * 1000
            
            return ClassificationResponse(
                request_types=[],
                extracted_fields=[],
                support_group="",
                is_duplicate=False,
                duplicate_reason=None,
                processing_time_ms=processing_time,
                error=f"Error processing EML: {str(e)}"
            )
    
    async def _get_request_types_from_db(self) -> List[Dict[str, Any]]:
        """
        Get request types from MongoDB
        """
        try:
            # Fetch all request types from the database
            request_types = await request_type_collection.find().to_list(length=None)
            
            # Convert database ObjectIds to strings for JSON serialization
            for request_type in request_types:
                request_type["_id"] = str(request_type["_id"])
            
            return request_types
        except Exception as e:
            logger.error(f"Error retrieving request types from database: {str(e)}")
            return []
    
    async def _get_required_attributes(self, request_type_name: str, sub_request_type_name: str) -> List[str]:
        """
        Get required attributes and support group for a specific request type and sub-request type
        """
        try:
            # Find request type by name
            request_type = await request_type_collection.find_one({"name": request_type_name})
            
            if not request_type:
                logger.warning(f"Request type not found: {request_type_name}")
                return ([], "Not found")
            
            # Find support group
            support_group = request_type.get("support_group", "Not found")
            
            # Find sub-request type
            for sub_type in request_type.get("sub_request_types", []):
                if sub_type.get("name") == sub_request_type_name:
                    return (sub_type.get("required_attributes", []), support_group)
            
            logger.warning(f"Sub-request type not found: {sub_request_type_name} in {request_type_name}")
            return ([], support_group)
            
        except Exception as e:
            logger.error(f"Error retrieving required attributes: {str(e)}")
            return ([], support_group)
            
    async def _identify_request_types(self,
                                    email_content: str,
                                    attachments: List[Dict[str, str]],
                                    sender: str,
                                    subject: str,
                                    received_date: str,
                                    request_types: List[Dict[str, Any]]) -> List[RequestTypeResult]:
        """
        Identify request types from email content and attachments
        
        Args:
            email_content: Processed email content
            attachments: List of processed attachments
            sender: Email sender
            subject: Email subject
            received_date: Email received date
            request_types: List of available request types from MongoDB
            
        Returns:
            List of request type results
        """
        try:
            # Format request types for prompt (include name and definition for sub-types)
            formatted_request_types = []
            for rt in request_types:
                # Format sub-types to include both name and definition
                sub_types = [
                    {
                        "name": st.get("name"),
                        "definition": st.get("definition", "")
                    } 
                    for st in rt.get("sub_request_types", [])
                ]
                
                # Add the main request type with its sub-types
                formatted_request_types.append({
                    "request_type": rt.get("name"),
                    "definition": rt.get("definition", ""),
                    "sub_request_types": sub_types
                })
                
            request_types_str = json.dumps(formatted_request_types, indent=2)
            
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
                    - IMPORTANT: Prioritize the email content over attachments for determining request type and sub request type
                    - The primary request should represent the sender's main intent
                    - Provide confidence scores between 0 and 1 (higher = more confident)
                    - Include detailed reasoning for each classification
                    - Only one request type should be marked as primary (is_primary: true)
                    - If multiple request types are present, rank them by relevance
                    - If you're unsure, use a lower confidence score
                    - Match request types exactly as provided in the available types
                    - ONLY RETURN THE JSON. Avoid adding any other text in your response like explanation, reasoning etc.
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
                Remember to prioritize email content over attachments when determining request type and sub request type.
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
                logger.debug(f"Raw response: {str(response_content)}")
                
                # Try to fix JSON with OutputFixingParser
                from langchain.output_parsers import OutputFixingParser
                from langchain_core.output_parsers import JsonOutputParser

                
                # Create a JsonOutputParser first as the base parser
                base_parser = JsonOutputParser()
                
                # Then create the OutputFixingParser with both the LLM and the base parser
                fixing_parser = OutputFixingParser.from_llm(
                    llm=llm,
                    parser=base_parser
                )
                
                try:
                    # Check if the response is empty
                    if not response_content.strip():
                        logger.error("Empty response from LLM")
                        return []
                        
                    # Try to fix and parse the JSON
                    fixed_json = fixing_parser.parse(response_content)
                    result_types = []
                    
                    # Validate the fixed JSON
                    if not isinstance(fixed_json, list):
                        logger.error(f"Fixed JSON is not a list: {fixed_json}")
                        return []
                    
                    for item in fixed_json:
                        # Ensure all required fields are present
                        if not all(k in item for k in ["request_type", "sub_request_type", "confidence", "reasoning"]):
                            logger.warning(f"Skipping item missing required fields: {item}")
                            continue
                            
                        try:
                            result_types.append(RequestTypeResult(
                                request_type=item["request_type"],
                                sub_request_type=item["sub_request_type"],
                                confidence=float(item["confidence"]),
                                reasoning=item["reasoning"],
                                is_primary=bool(item.get("is_primary", False))
                            ))
                        except (ValueError, TypeError) as e:
                            logger.warning(f"Error converting item to RequestTypeResult: {str(e)}")
                            continue
                    
                    # Ensure one primary request type
                    if not any(r.is_primary for r in result_types) and result_types:
                        result_types[0].is_primary = True
                    
                    logger.info(f"Fixed JSON and identified {len(result_types)} request types")
                    return result_types
                    
                except Exception as e2:
                    logger.error(f"Error fixing JSON: {str(e2)}")
                    # Return an empty list as a fallback
                    return []
                
        except Exception as e:
            logger.error(f"Error identifying request types: {str(e)}")
            return []