import boto3
from botocore.config import Config
from src.core.config import settings
from botocore.exceptions import ClientError

class BedrockClient:
    def __init__(self):
        self.client = boto3.client(
            'bedrock-runtime',
            region_name=settings.BEDROCK_REGION,
            config=Config(
                max_pool_connections=500,
                connect_timeout=300,
                read_timeout=300,
                retries={'max_attempts': 5, 'mode': 'standard'},
            )
        )
    
    async def generate(self, context: str, query: str):
        model_id = settings.MODEL_ID
        conversation = [
            {
                "role": "system",
                "content": [
                    {
                        "text": f"Answer only using the provided context. \n**Context**: {context}\n\n Be concise and **Do Not** answer anything outside of context. If unsure, say 'I don't know'."
                    }
                ],
            },
            {
                "role": "user",
                "content": [{"text": query}],
            }
        ]

        try:
            response = await self.client.converse(
                modelId=model_id,
                messages=conversation,
                inferenceConfig={"maxTokens": 300, "temperature": 0.3},
            )

            response_text = response["output"]["message"]["content"][0]["text"]

            return response_text

        except (ClientError, Exception) as e:
            print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
            exit(1)
