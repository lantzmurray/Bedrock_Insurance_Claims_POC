# src/app.py

import json
import boto3

from .config import (
    CLAIM_BUCKET,
    CLAIMS_PREFIX,
    OUTPUTS_PREFIX,
    DOC_EXTRACT_MODEL_ID,
    SUMMARY_MODEL_ID,
)
from .prompts import PromptTemplateManager
from .models import BedrockModelInvoker
from .rag import load_policy_snippets, simple_keyword_retriever
from .validator import validate_extracted_info

s3 = boto3.client("s3")

prompt_manager = PromptTemplateManager()
extract_invoker = BedrockModelInvoker(DOC_EXTRACT_MODEL_ID)
summary_invoker = BedrockModelInvoker(SUMMARY_MODEL_ID)


def upload_document(local_path: str, key: str) -> None:
    """
    Upload a local file to S3 at the given key.
    Example key: "claims/claim1.txt"
    """
    s3.upload_file(local_path, CLAIM_BUCKET, key)
    print(f"[UPLOAD] {local_path} -> s3://{CLAIM_BUCKET}/{key}")


def get_document_text(key: str) -> str:
    """
    Fetch and decode the claim document at the given key.
    """
    print(f"[GET] s3://{CLAIM_BUCKET}/{key}")
    response = s3.get_object(Bucket=CLAIM_BUCKET, Key=key)
    return response["Body"].read().decode("utf-8")


def process_claim_document(key: str) -> dict:
    """
    Main processing function:

    1) Load claim text from S3
    2) Extract structured info with Bedrock
    3) Retrieve relevant policy snippets (simple RAG)
    4) Generate a concise summary with Bedrock
    5) Save result JSON to outputs/ and return it
    """
    print(f"[PROCESS] Claim document: s3://{CLAIM_BUCKET}/{key}")
    document_text = get_document_text(key)

    # 1) Extraction prompt
    extract_prompt = prompt_manager.get_prompt(
        "extract_info",
        document_text=document_text,
    )

    print("[LLM] Calling extraction model...")
    raw_extracted = extract_invoker.invoke(
        prompt=extract_prompt,
        model_id=DOC_EXTRACT_MODEL_ID,
        temperature=0.0,
        max_tokens=800,
    )

    extracted_info = validate_extracted_info(raw_extracted)
    print("[INFO] Extracted info:", json.dumps(extracted_info, indent=2))

    # 2) Simple RAG over policies
    print("[RAG] Loading policy snippets...")
    policy_snippets_all = load_policy_snippets()
    query_text = f"{extracted_info.get('policy_number', '')} {extracted_info.get('incident_description', '')}"
    relevant_policies = simple_keyword_retriever(policy_snippets_all, query_text, top_k=3)
    policy_text = "\n\n---\n\n".join(relevant_policies) if relevant_policies else "No matching policy snippets found."

    # 3) Summary prompt
    summary_prompt = prompt_manager.get_prompt(
        "generate_summary",
        extracted_info=json.dumps(extracted_info, indent=2),
        policy_text=policy_text,
    )

    print("[LLM] Calling summary model...")
    summary = summary_invoker.invoke(
        prompt=summary_prompt,
        model_id=SUMMARY_MODEL_ID,
        temperature=0.3,
        max_tokens=600,
    )

    result = {
        "claim_key": key,
        "extracted_info": extracted_info,
        "summary": summary,
        "policy_snippets": relevant_policies,
        "extract_model_id": DOC_EXTRACT_MODEL_ID,
        "summary_model_id": SUMMARY_MODEL_ID,
    }

    # 4) Write result to outputs/
    base_name = key.replace(CLAIMS_PREFIX, "").rsplit(".", 1)[0]
    out_key = f"{OUTPUTS_PREFIX}{base_name}_result.json"

    print(f"[WRITE] s3://{CLAIM_BUCKET}/{out_key}")
    s3.put_object(
        Bucket=CLAIM_BUCKET,
        Key=out_key,
        Body=json.dumps(result, indent=2).encode("utf-8"),
        ContentType="application/json",
    )

    print("[DONE] Processing complete.")
    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        # Run web interface
        print("[START] Starting web interface on http://localhost:8000")
        os.system("cd web && python app.py")
    else:
        # Run command line interface
        try:
            claim_key = f"{CLAIMS_PREFIX}sample_claim1.txt"
            print(f"[START] Running claim processor for {claim_key}")
            result = process_claim_document(claim_key)
            print("[RESULT]")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print("[ERROR]", repr(e))
