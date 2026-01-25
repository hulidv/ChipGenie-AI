from __future__ import annotations

import os
from typing import Optional

import httpx
from pydantic import BaseModel
from dotenv import load_dotenv


class LlmConfig(BaseModel):
    provider: str = "stub"  # openai|deepseek|ollama|stub
    model: Optional[str] = None
    base_url: Optional[str] = None


class LLMClient:
    def __init__(self, config: Optional[LlmConfig] = None):
        load_dotenv()
        self.config = config or LlmConfig(
            provider=os.getenv("CHIPGENIE_LLM_PROVIDER", "stub"),
            model=os.getenv("CHIPGENIE_LLM_MODEL"),
            base_url=os.getenv("CHIPGENIE_LLM_BASE_URL"),
        )

    async def chat(self, system: str, user: str) -> str:
        provider = self.config.provider.lower()
        if provider == "openai":
            return await self._chat_openai(system, user)
        if provider == "deepseek":
            return await self._chat_deepseek(system, user)
        if provider == "ollama":
            return await self._chat_ollama(system, user)
        return self._chat_stub(system, user)

    def _chat_stub(self, system: str, user: str) -> str:
        return (
            "Search for well-known parts matching constraints; prefer availability. "
            "Example query: site:octopart.com 3.3V LDO 500mA SOT-23-5."
        )

    async def _chat_openai(self, system: str, user: str) -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return self._chat_stub(system, user)
        model = self.config.model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        url = (self.config.base_url or "https://api.openai.com/v1") + "/chat/completions"
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": 0.2,
        }
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def _chat_deepseek(self, system: str, user: str) -> str:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            return self._chat_stub(system, user)
        model = self.config.model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        url = (self.config.base_url or "https://api.deepseek.com/v1") + "/chat/completions"
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": 0.2,
        }
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def _chat_ollama(self, system: str, user: str) -> str:
        base = self.config.base_url or "http://localhost:11434"
        model = self.config.model or os.getenv("OLLAMA_MODEL", "llama3.2")
        payload = {"model": model, "prompt": f"{system}\nUser: {user}", "stream": False}
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(base + "/api/generate", json=payload)
            if resp.status_code != 200:
                return self._chat_stub(system, user)
            data = resp.json()
            return data.get("response", "")
