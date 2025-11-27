# Configuration settings for the Bedrock Insurance Claims POC

# S3 settings
CLAIM_BUCKET = "claim-documents-poc-lm"  # Replace with your bucket name
CLAIMS_PREFIX = "claims/"
OUTPUTS_PREFIX = "outputs/"
POLICIES_PREFIX = "policies/"

# Bedrock model IDs
DOC_EXTRACT_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"  # Model for document extraction
SUMMARY_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"      # Model for summary generation
