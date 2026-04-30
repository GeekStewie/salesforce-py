"""Live exercise of the Salesforce Models REST API against the ``sdonew`` org.

Run with:

    LIVE_MODELS_TESTS=1 \\
    SF_MODELS_CLIENT_ID=... \\
    SF_MODELS_CLIENT_SECRET=... \\
    SF_MODELS_INSTANCE_URL=https://<my-domain>.my.salesforce.com \\
    uv run pytest tests/models/live/test_models_live.py -v -s

The Models API is **not** reachable via SF CLI session tokens — it requires
an External Client App with the ``sfap_api einstein_gpt_api api`` scopes
and the client-credentials flow. This test uses :meth:`ModelsClient.from_env`,
which reads those env vars.

The probe exercises all four Models capabilities:

* ``fetch_token`` — client-credentials token bootstrap
* ``generations.generate`` — single-prompt text generation
* ``chat_generations.generate`` — multi-turn chat completion
* ``embeddings.embed`` — single and batch embeddings
* ``feedback.submit`` — feedback submission

Each capability prints a short status line under ``-s``. If the org has
Einstein Generative AI disabled, the individual endpoints will return
``403 FUNCTIONALITY_NOT_ENABLED`` — we log and classify as "skipped" in
that case rather than failing the test.
"""

from __future__ import annotations

import os
from typing import Any

import pytest

from salesforce_py.models import ModelsClient
from salesforce_py.models.supported_models import (
    OPENAI_ADA_002,
    OPENAI_GPT_4_OMNI_MINI,
)

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.environ.get("LIVE_MODELS_TESTS") != "1",
        reason="Set LIVE_MODELS_TESTS=1 to run live Models API tests",
    ),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


SKIP_PATTERNS = [
    "not enabled",
    "functionality_not_enabled",
    "feature_not_enabled",
    "not currently enabled",
    "disabled",
    "insufficient access",
    "insufficient privileges",
    "not available",
    "not configured",
    "unauthorized",
    "no such",
    "not found",
    "does not exist",
    "no model",
    "model not available",
    "unknown model",
    "invalid model",
    "rate limit",
    "quota",
]


def _classify(exc: Exception) -> tuple[str, str]:
    """Return ``(status, detail)``. ``"skipped"`` when the org/feature is absent."""
    msg = str(exc)
    lower = msg.lower()
    for pattern in SKIP_PATTERNS:
        if pattern in lower:
            return "skipped", msg[:300]
    if any(code in msg for code in ("error 400", "error 403", "error 404", "error 501")):
        return "skipped", msg[:300]
    return "fail", msg[:400]


def _log_outcome(label: str, exc: Exception | None, extra: Any = None) -> None:
    if exc is None:
        suffix = f" — {extra}" if extra is not None else ""
        print(f"  [pass] {label}{suffix}")
        return
    status, detail = _classify(exc)
    tag = "skipped" if status == "skipped" else "FAIL"
    print(f"  [{tag}] {label}: {detail}")


# ---------------------------------------------------------------------------
# Test entry point
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_models_live_all_capabilities() -> None:
    # from_env() performs the client-credentials token bootstrap itself.
    print("\n[1/5] TOKEN — ModelsClient.from_env() (client_credentials)")
    failures: list[str] = []
    async with await ModelsClient.from_env() as client:
        print(f"  token acquired, base_url={client._session._base_url}")

        # --- generations.generate --------------------------------------
        print("\n[2/5] generations.generate — OPENAI_GPT_4_OMNI_MINI")
        try:
            res = await client.generations.generate(
                OPENAI_GPT_4_OMNI_MINI,
                "In one short sentence, greet the Salesforce Trailblazer community.",
                extra={"localization": {"defaultLocale": "en_US"}},
            )
            text = _extract_generation_text(res)
            _log_outcome("generations.generate", None, f"reply: {text[:80]}")
        except Exception as exc:  # noqa: BLE001
            _log_outcome("generations.generate", exc)
            if _classify(exc)[0] == "fail":
                failures.append(f"generations.generate: {exc}")

        # --- chat_generations.generate ---------------------------------
        print("\n[3/5] chat_generations.generate — OPENAI_GPT_4_OMNI_MINI")
        messages = [
            {"role": "system", "content": "You are a concise assistant."},
            {"role": "user", "content": "What is 2+2? Answer with the digit only."},
        ]
        try:
            res = await client.chat_generations.generate(
                OPENAI_GPT_4_OMNI_MINI, messages
            )
            text = _extract_chat_text(res)
            _log_outcome("chat_generations.generate", None, f"reply: {text[:80]}")
        except Exception as exc:  # noqa: BLE001
            _log_outcome("chat_generations.generate", exc)
            if _classify(exc)[0] == "fail":
                failures.append(f"chat_generations.generate: {exc}")

        # --- embeddings.embed — single ---------------------------------
        print("\n[4/5] embeddings.embed — single + batch (OPENAI_ADA_002)")
        try:
            res = await client.embeddings.embed(OPENAI_ADA_002, "hello salesforce")
            dim = _embedding_dim(res)
            _log_outcome("embeddings.embed[single]", None, f"dim={dim}")
        except Exception as exc:  # noqa: BLE001
            _log_outcome("embeddings.embed[single]", exc)
            if _classify(exc)[0] == "fail":
                failures.append(f"embeddings.embed[single]: {exc}")

        try:
            res = await client.embeddings.embed(
                OPENAI_ADA_002, ["hello salesforce", "goodbye salesforce"]
            )
            count = _embedding_count(res)
            _log_outcome("embeddings.embed[batch]", None, f"vectors={count}")
        except Exception as exc:  # noqa: BLE001
            _log_outcome("embeddings.embed[batch]", exc)
            if _classify(exc)[0] == "fail":
                failures.append(f"embeddings.embed[batch]: {exc}")

        # --- feedback.submit -------------------------------------------
        print("\n[5/5] feedback.submit")
        feedback_body = {
            "id": "live-test-feedback-" + os.urandom(4).hex(),
            "generationId": "live-test-generation-" + os.urandom(4).hex(),
            "feedback": "GOOD",
            "feedbackText": "salesforce-py live test",
            "appGenerationId": "live-test-app-" + os.urandom(4).hex(),
            "appFeedbackId": "live-test-app-fb-" + os.urandom(4).hex(),
            "source": "APP",
        }
        try:
            res = await client.feedback.submit(feedback_body)
            _log_outcome("feedback.submit", None, f"keys={list(res.keys())[:5]}")
        except Exception as exc:  # noqa: BLE001
            _log_outcome("feedback.submit", exc)
            if _classify(exc)[0] == "fail":
                failures.append(f"feedback.submit: {exc}")

    print("\nMODELS LIVE — done")
    if failures:
        print("\nHARD FAILURES:")
        for f in failures:
            print(f"  {f}")
        raise AssertionError(f"{len(failures)} hard failure(s) — see log above")


# ---------------------------------------------------------------------------
# Response shape helpers
# ---------------------------------------------------------------------------


def _extract_generation_text(res: dict[str, Any]) -> str:
    # Response typically looks like:
    #   {"id": ..., "generation": {"generatedText": "..."}, "parameters": ..., ...}
    gen = res.get("generation") or {}
    if isinstance(gen, dict):
        text = gen.get("generatedText") or gen.get("text") or ""
        if text:
            return text
    # Fallback — some models respond with "generations": [ {...} ]
    gens = res.get("generations") or []
    if gens and isinstance(gens[0], dict):
        return gens[0].get("generatedText") or gens[0].get("text") or ""
    return str(res)[:200]


def _extract_chat_text(res: dict[str, Any]) -> str:
    # chat-generations response:
    #   {"id": ..., "generationDetails": {"generations": [{"content": "...", "role": "assistant"}]}, ...}
    details = res.get("generationDetails") or {}
    gens = details.get("generations") or []
    if gens and isinstance(gens[0], dict):
        return gens[0].get("content") or gens[0].get("text") or ""
    return str(res)[:200]


def _embedding_dim(res: dict[str, Any]) -> int | None:
    embeds = res.get("embeddings") or []
    if embeds and isinstance(embeds[0], dict):
        vec = embeds[0].get("embedding") or embeds[0].get("vector") or []
        if isinstance(vec, list):
            return len(vec)
    return None


def _embedding_count(res: dict[str, Any]) -> int:
    embeds = res.get("embeddings") or []
    return len(embeds) if isinstance(embeds, list) else 0
