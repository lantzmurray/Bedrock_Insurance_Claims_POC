# Bedrock model integration

import json
import boto3
import botocore

class BedrockModelInvoker:
    """
    Wrapper class for invoking AWS Bedrock models
    """
    
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.client = boto3.client("bedrock-runtime")
    
    def invoke(self, prompt: str, model_id: str = None, temperature: float = 0.0, max_tokens: int = 800) -> str:
        """
        Invoke the Bedrock model with the given prompt
        """
        if model_id is None:
            model_id = self.model_id
            
        # Prepare the request body based on the model
        if "claude-3" in model_id.lower() or "claude-4" in model_id.lower():
            # Use Messages API for Claude 3+ models
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        elif "claude" in model_id.lower():
            # Use legacy completion API for older Claude models
            body = json.dumps({
                "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                "temperature": temperature,
                "max_tokens_to_sample": max_tokens,
            })
        else:
            # Default format for other models
            body = json.dumps({
                "inputText": prompt,
                "textGenerationConfig": {
                    "temperature": temperature,
                    "maxTokenCount": max_tokens,
                }
            })
        
        try:
            response = self.client.invoke_model(
                modelId=model_id,
                body=body
            )
            
            response_body = json.loads(response.get("body").read())
            
            # Extract the text based on the model response format
            if "claude-3" in model_id.lower() or "claude-4" in model_id.lower():
                # Extract from Messages API response
                return response_body.get("content", [{}])[0].get("text", "")
            elif "claude" in model_id.lower():
                # Extract from legacy completion API response
                return response_body.get("completion", "")
            else:
                # Default format for other models
                return response_body.get("results", [{}])[0].get("outputText", "")
                
        except botocore.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            return f"Error invoking model {model_id}: {error_code} - {error_message}"
        except Exception as e:
            return f"Unexpected error invoking model {model_id}: {str(e)}"
