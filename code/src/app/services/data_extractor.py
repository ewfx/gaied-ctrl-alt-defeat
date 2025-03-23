import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple, Union

from langchain.schema.messages import SystemMessage, HumanMessage

from app.core.llm_handler import LLMHandler
from app.models.response_models import ExtractedField

logger = logging.getLogger(__name__)

class DataExtractor:
    """
    Service for extracting structured data from email content based on request type
    """
    
    def __init__(self, llm_handler: LLMHandler):
        """
        Initialize the data extractor
        
        Args:
            llm_handler: LLM handler for LLM interactions
        """
        self.llm_handler = llm_handler
        logger.info("Data extractor initialized")
    
    async def extract_fields(self,
                           email_content: str,
                           attachments: List[Dict[str, str]],
                           request_type: str,
                           sub_request_type: str,
                           extraction_rules: Dict[str, Any]) -> List[ExtractedField]:
        """
        Extract fields from email content based on request type
        
        Args:
            email_content: Processed email content
            attachments: List of processed attachments
            request_type: Identified request type
            sub_request_type: Identified sub-request type
            extraction_rules: Dictionary of extraction rules by request type
            
        Returns:
            List of extracted fields
        """
        try:
            # Get extraction rules for the request type
            rules = extraction_rules.get(request_type, extraction_rules.get("default", {}))
            
            # Get priority sources and fields to extract
            priority_sources = rules.get("priority_sources", ["email_body", "attachment"])
            fields_to_extract = rules.get("fields", [])
            
            # Format attachments for prompt
            attachments_str = ""
            for attachment in attachments:
                # Truncate very long attachments
                text = attachment["text"]
                attachments_str += f"\n\nATTACHMENT {attachment['index']}: {attachment['filename']}\n{text}"
            
            # Create system prompt
            system_prompt = f"""You are an AI assistant specializing in extracting data from banking service emails.

                TASK:
                Extract relevant fields based on the identified request type: {request_type} - {sub_request_type}

                YOUR RESPONSE MUST BE A VALID JSON ARRAY of objects with this structure:
                [
                {{
                    "field_name": "amount",
                    "value": 50000,
                    "confidence": 0.98,
                    "source": "email_body"
                }},
                ...
                ]

                FIELDS TO EXTRACT:
                {json.dumps(fields_to_extract, indent=2)}

                PRIORITY SOURCES (in order of preference):
                {json.dumps(priority_sources, indent=2)}

                RULES:
                - Source should be "email_body" or "attachment_1", "attachment_2", etc.
                - Only extract fields you are confident about (provide confidence score 0-1)
                - For numerical values, provide them as numbers not strings when appropriate
                - Format dates in ISO format (YYYY-MM-DD) when possible
                - Look for specific evidence within the text to support your extraction
                - Prefer sources in the priority order provided above
                - Don't include fields where you couldn't find any relevant information (confidence < 0.5)
                - If the same field is found in multiple sources, choose the highest priority source
                """
            
            # Create human prompt
            human_prompt = f"""REQUEST TYPE: {request_type} - {sub_request_type}

                EMAIL CONTENT:
                {email_content}
                {attachments_str}

                Based on the above email content and attachments, extract all relevant fields.
                """
            
            # Get LLM for data extraction
            llm = self.llm_handler.get_llm("data_extraction")
            
            # Get response from LLM
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = await llm.ainvoke(messages)
            response_content = response.content
            
            # Parse the response
            try:
                extracted_data = json.loads(response_content)
                
                # Validate and convert to model objects
                result_fields = []
                for item in extracted_data:
                    # Ensure required fields are present
                    if all(k in item for k in ["field_name", "value", "confidence", "source"]):
                        # Skip low confidence extractions
                        if float(item["confidence"]) < 0.5:
                            continue
                            
                        # Normalize field names
                        field_name = self._normalize_field_name(item["field_name"])
                        
                        # Add to results
                        result_fields.append(ExtractedField(
                            field_name=field_name,
                            value=item["value"],
                            confidence=float(item["confidence"]),
                            source=item["source"]
                        ))
                
                logger.info(f"Extracted {len(result_fields)} fields")
                return result_fields
                
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing LLM response: {str(e)}")
                logger.debug(f"Raw response: {response_content}")
                
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
                    fixed_json = fixing_parser.parse(response_content)
                    result_fields = []
                    
                    for item in fixed_json:
                        # Skip low confidence extractions
                        if float(item.get("confidence", 0)) < 0.5:
                            continue
                            
                        # Normalize field names
                        field_name = self._normalize_field_name(item["field_name"])
                        
                        result_fields.append(ExtractedField(
                            field_name=field_name,
                            value=item["value"],
                            confidence=float(item["confidence"]),
                            source=item["source"]
                        ))
                    
                    logger.info(f"Fixed JSON and extracted {len(result_fields)} fields")
                    return result_fields
                    
                except Exception as e2:
                    logger.error(f"Error fixing JSON: {str(e2)}")
                    return []
                
        except Exception as e:
            logger.error(f"Error extracting fields: {str(e)}")
            return []
    
    def _normalize_field_name(self, field_name: str) -> str:
        """
        Normalize field names to a consistent format
        
        Args:
            field_name: Raw field name
            
        Returns:
            Normalized field name
        """
        # Convert to lowercase
        field = field_name.lower()
        
        # Replace spaces with underscores
        field = re.sub(r'\s+', '_', field)
        
        # Remove special characters
        field = re.sub(r'[^\w_]', '', field)
        
        # Map common variations
        field_mapping = {
            "dollar_amount": "amount",
            "payment_amount": "amount",
            "transfer_amount": "amount",
            "funding_amount": "amount",
            "acct_number": "account_number",
            "acc_number": "account_number",
            "account_num": "account_number",
            "acct_num": "account_number",
            "value_dt": "value_date",
            "payment_date": "value_date",
            "transfer_date": "value_date",
            "client": "client_name",
            "customer": "client_name",
            "customer_name": "client_name",
            "deal": "deal_name",
            "transaction_number": "transaction_id",
            "tx_id": "transaction_id",
            "trans_id": "transaction_id",
            "currency_type": "currency",
            "beneficiary": "beneficiary_name"
        }
        
        return field_mapping.get(field, field)