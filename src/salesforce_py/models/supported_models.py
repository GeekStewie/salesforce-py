"""API names for the standard Salesforce-managed models.

These strings are the ``{modelName}`` segment accepted by the Models API
generations, chat-generations, and embeddings endpoints. Custom
configurations created in Einstein Studio (BYOLLM) also work — look up
their API name in Einstein Studio and pass it as a string.

Availability, rate limits, and deprecation status change over time; see
the Salesforce documentation for the authoritative list. This module
just gives typed constants so callers don't have to hand-type the
``sfdc_ai__Default…`` prefix.
"""

from __future__ import annotations

from typing import Final

# ----------------------------------------------------------------------
# Amazon Bedrock — Salesforce Trust Boundary
# ----------------------------------------------------------------------

BEDROCK_AMAZON_NOVA_LITE: Final[str] = "sfdc_ai__DefaultBedrockAmazonNovaLite"
BEDROCK_AMAZON_NOVA_PRO: Final[str] = "sfdc_ai__DefaultBedrockAmazonNovaPro"
BEDROCK_ANTHROPIC_CLAUDE_45_HAIKU: Final[str] = "sfdc_ai__DefaultBedrockAnthropicClaude45Haiku"
BEDROCK_ANTHROPIC_CLAUDE_45_OPUS: Final[str] = "sfdc_ai__DefaultBedrockAnthropicClaude45Opus"
BEDROCK_ANTHROPIC_CLAUDE_46_OPUS: Final[str] = "sfdc_ai__DefaultBedrockAnthropicClaude46Opus"
BEDROCK_ANTHROPIC_CLAUDE_47_OPUS: Final[str] = "sfdc_ai__DefaultBedrockAnthropicClaude47Opus"
BEDROCK_ANTHROPIC_CLAUDE_4_SONNET: Final[str] = "sfdc_ai__DefaultBedrockAnthropicClaude4Sonnet"
BEDROCK_ANTHROPIC_CLAUDE_45_SONNET: Final[str] = "sfdc_ai__DefaultBedrockAnthropicClaude45Sonnet"
BEDROCK_ANTHROPIC_CLAUDE_46_SONNET: Final[str] = "sfdc_ai__DefaultBedrockAnthropicClaude46Sonnet"
BEDROCK_NVIDIA_NEMOTRON_NANO_330B: Final[str] = "sfdc_ai__DefaultBedrockNvidiaNemotronNano330b"

# ----------------------------------------------------------------------
# OpenAI / Azure OpenAI
# ----------------------------------------------------------------------

AZURE_OPENAI_ADA_002: Final[str] = "sfdc_ai__DefaultAzureOpenAITextEmbeddingAda_002"
OPENAI_ADA_002: Final[str] = "sfdc_ai__DefaultOpenAITextEmbeddingAda_002"
GPT_4_OMNI: Final[str] = "sfdc_ai__DefaultGPT4Omni"
GPT_4_OMNI_MINI: Final[str] = "sfdc_ai__DefaultGPT4OmniMini"
OPENAI_GPT_4_OMNI_MINI: Final[str] = "sfdc_ai__DefaultOpenAIGPT4OmniMini"
GPT_4_1: Final[str] = "sfdc_ai__DefaultGPT41"
GPT_4_1_MINI: Final[str] = "sfdc_ai__DefaultGPT41Mini"
GPT_5: Final[str] = "sfdc_ai__DefaultGPT5"
GPT_5_MINI: Final[str] = "sfdc_ai__DefaultGPT5Mini"
GPT_5_1: Final[str] = "sfdc_ai__DefaultGPT51"
GPT_5_2: Final[str] = "sfdc_ai__DefaultGPT52"
GPT_5_4: Final[str] = "sfdc_ai__DefaultGPT54"
O3: Final[str] = "sfdc_ai__DefaultO3"
O4_MINI: Final[str] = "sfdc_ai__DefaultO4Mini"

# ----------------------------------------------------------------------
# Vertex AI (Google)
# ----------------------------------------------------------------------

VERTEX_GEMINI_25_FLASH: Final[str] = "sfdc_ai__DefaultVertexAIGemini25Flash001"
VERTEX_GEMINI_25_FLASH_LITE: Final[str] = "sfdc_ai__DefaultVertexAIGemini25FlashLite001"
VERTEX_GEMINI_25_PRO: Final[str] = "sfdc_ai__DefaultVertexAIGeminiPro25"
VERTEX_GEMINI_30_FLASH: Final[str] = "sfdc_ai__DefaultVertexAIGemini30Flash"
VERTEX_GEMINI_30_PRO: Final[str] = "sfdc_ai__DefaultVertexAIGeminiPro30"
VERTEX_GEMINI_31_FLASH_LITE: Final[str] = "sfdc_ai__DefaultVertexAIGemini31FlashLite"
VERTEX_GEMINI_31_PRO: Final[str] = "sfdc_ai__DefaultVertexAIGeminiPro31"

# ----------------------------------------------------------------------
# Convenience collection
# ----------------------------------------------------------------------

SUPPORTED_MODELS: Final[tuple[str, ...]] = (
    BEDROCK_AMAZON_NOVA_LITE,
    BEDROCK_AMAZON_NOVA_PRO,
    BEDROCK_ANTHROPIC_CLAUDE_45_HAIKU,
    BEDROCK_ANTHROPIC_CLAUDE_45_OPUS,
    BEDROCK_ANTHROPIC_CLAUDE_46_OPUS,
    BEDROCK_ANTHROPIC_CLAUDE_47_OPUS,
    BEDROCK_ANTHROPIC_CLAUDE_4_SONNET,
    BEDROCK_ANTHROPIC_CLAUDE_45_SONNET,
    BEDROCK_ANTHROPIC_CLAUDE_46_SONNET,
    BEDROCK_NVIDIA_NEMOTRON_NANO_330B,
    AZURE_OPENAI_ADA_002,
    OPENAI_ADA_002,
    GPT_4_OMNI,
    GPT_4_OMNI_MINI,
    OPENAI_GPT_4_OMNI_MINI,
    GPT_4_1,
    GPT_4_1_MINI,
    GPT_5,
    GPT_5_MINI,
    GPT_5_1,
    GPT_5_2,
    GPT_5_4,
    O3,
    O4_MINI,
    VERTEX_GEMINI_25_FLASH,
    VERTEX_GEMINI_25_FLASH_LITE,
    VERTEX_GEMINI_25_PRO,
    VERTEX_GEMINI_30_FLASH,
    VERTEX_GEMINI_30_PRO,
    VERTEX_GEMINI_31_FLASH_LITE,
    VERTEX_GEMINI_31_PRO,
)
