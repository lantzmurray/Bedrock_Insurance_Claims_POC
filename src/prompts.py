# Prompt templates for the Bedrock Insurance Claims POC

class PromptTemplateManager:
    """
    Manages prompt templates for different tasks in the claims processing pipeline
    """
    
    def __init__(self):
        self.templates = {
            "extract_info": """
You are an insurance claims processor. Extract the following information from the claim document:
- claimant_name: Full name of the person making the claim
- policy_number: Insurance policy number
- incident_date: Date when the incident occurred
- claim_amount: Amount being claimed
- incident_description: Detailed description of what happened

Document text:
{document_text}

Return the information in JSON format with the exact field names specified above.
            """,
            
            "generate_summary": """
You are an insurance claims processor. Based on the extracted claim information and relevant policy snippets, generate a concise summary of the claim.

Extracted Information:
{extracted_info}

Policy Information:
{policy_text}

Provide a summary that includes:
1. Brief description of the incident
2. Coverage assessment based on policy
3. Next steps for processing

Keep the summary professional and concise.
            """
        }
    
    def get_prompt(self, template_name: str, **kwargs) -> str:
        """
        Get a formatted prompt template with the provided parameters
        """
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        template = self.templates[template_name]
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required parameter for template '{template_name}': {e}")
