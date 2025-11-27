import boto3
from .config import CLAIM_BUCKET, POLICIES_PREFIX

s3 = boto3.client("s3")

def load_policy_snippets():
    objs = s3.list_objects_v2(Bucket=CLAIM_BUCKET, Prefix=POLICIES_PREFIX)
    snippets = []
    contents = objs.get("Contents", [])
    for obj in contents:
        key = obj["Key"]
        try:
            body = s3.get_object(Bucket=CLAIM_BUCKET, Key=key)["Body"].read()
            text = body.decode("utf-8", errors="ignore").strip()
            if text:
                snippets.append(text)
        except Exception:
            continue
    if snippets:
        return snippets
    return [
        "Policy #12345: Coverage for water damage includes burst pipes and accidental leaks.",
        "Policy #67890: Deductible for water damage claims is $500.",
        "Policy #11111: Claims must be filed within 30 days of incident discovery.",
        "Policy #22222: Water damage from maintenance neglect is not covered.",
        "Policy #33333: Emergency repairs are covered up to $2,000 before approval.",
    ]

def simple_keyword_retriever(policy_snippets, query_text, top_k=3):
    """
    Simple keyword-based retrieval function.
    Returns the most relevant policy snippets based on keyword matching.
    """
    # Simple keyword matching - in a real implementation, this would use
    # more sophisticated retrieval methods
    query_lower = query_text.lower()
    scored_snippets = []
    
    for snippet in policy_snippets:
        score = 0
        # Simple scoring based on keyword matches
        if "water" in query_lower and "water" in snippet.lower():
            score += 2
        if "damage" in query_lower and "damage" in snippet.lower():
            score += 2
        if "leak" in query_lower and "leak" in snippet.lower():
            score += 2
        if "pipe" in query_lower and "pipe" in snippet.lower():
            score += 2
        
        if score > 0:
            scored_snippets.append((score, snippet))
    
    # Sort by score (descending) and return top_k
    scored_snippets.sort(key=lambda x: x[0], reverse=True)
    return [snippet for score, snippet in scored_snippets[:top_k]]
