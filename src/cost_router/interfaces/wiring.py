"""The composition root: build the adapters and services from settings."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from cost_router.application.ports import ChatModel, Mapper, PromptStore
from cost_router.application.tiers import ModelTiers
from cost_router.domain.pricing import PriceTable
from cost_router.domain.routing import Bar
from cost_router.domain.tasks import Task
from cost_router.infrastructure.data import load_bar, load_prices, load_tasks
from cost_router.infrastructure.llm.factory import build_chat_model
from cost_router.infrastructure.parallel import thread_mapper
from cost_router.infrastructure.prompts import FilePromptStore
from cost_router.infrastructure.settings import Settings


@dataclass(frozen=True)
class Services:
    """Everything a command needs."""

    settings: Settings
    tasks: list[Task]
    bar: Bar
    prices: PriceTable
    prompts: PromptStore
    model: ChatModel
    mapper: Mapper

    @property
    def tiers(self) -> ModelTiers:
        """The three tiers on the configured models."""
        return ModelTiers(self.model, self.prompts, self.settings.models, self.prices)

    def split(self, name: str) -> list[Task]:
        """The `build` or `test` tasks."""
        return [t for t in self.tasks if t.split == name]


def build_services(env: Mapping[str, str], root: Path) -> Services:
    """Read settings and data, and build the model adapter named by LLM_PROVIDER."""
    settings = Settings.from_env(env, root)
    return Services(
        settings=settings,
        tasks=load_tasks(settings.data_dir),
        bar=load_bar(settings.config_dir),
        prices=load_prices(settings.config_dir),
        prompts=FilePromptStore(settings.prompts_dir),
        model=build_chat_model(env, settings.fixtures_dir),
        mapper=thread_mapper(settings.workers),
    )
