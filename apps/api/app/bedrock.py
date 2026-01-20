import json
import os
from typing import List
from uuid import uuid4

import boto3

from .schemas import Suggestion


class BedrockAgentError(RuntimeError):
    pass


def _load_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise BedrockAgentError(f"Missing environment variable: {name}")
    return value


def _read_completion(response) -> str:
    if "completion" in response:
        completion = response["completion"]
        if isinstance(completion, str):
            return completion
        if isinstance(completion, dict):
            data = completion.get("bytes")
            if data:
                return data.decode("utf-8")
        if hasattr(completion, "read"):
            return completion.read().decode("utf-8")
        chunks = []
        event_keys = []
        for event in completion:
            event_keys.append(",".join(event.keys()) if isinstance(event, dict) else type(event).__name__)
            chunk = event.get("chunk") if isinstance(event, dict) else None
            if not chunk:
                continue
            data = chunk.get("bytes")
            if not data:
                continue
            chunks.append(data.decode("utf-8"))
        if chunks:
            return "".join(chunks)
        raise BedrockAgentError(f"Empty Bedrock completion stream. Events: {event_keys}")

    output_text = response.get("outputText")
    if output_text:
        return output_text

    raise BedrockAgentError(f"Bedrock response missing completion content: {list(response.keys())}")


def _extract_json(payload: str) -> dict:
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        start = payload.find("{")
        end = payload.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(payload[start : end + 1])


def analyze_slide_text(slide_id: str, text: str) -> List[Suggestion]:
    region = _load_env("AWS_REGION")
    agent_id = _load_env("BEDROCK_AGENT_ID")
    alias_id = _load_env("BEDROCK_AGENT_ALIAS_ID")

    client = boto3.client("bedrock-agent-runtime", region_name=region)
    input_payload = json.dumps({"slide_id": slide_id, "slide_text": text})
    response = client.invoke_agent(
        agentId=agent_id,
        agentAliasId=alias_id,
        sessionId=str(uuid4()),
        inputText=input_payload,
    )
    completion = _read_completion(response)
    data = _extract_json(completion)
    suggestions_raw = data.get("suggestions", [])
    suggestions = []
    for item in suggestions_raw:
        suggestions.append(Suggestion(**item))
    return suggestions
