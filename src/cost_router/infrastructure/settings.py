"""Settings from the environment, validated once at start-up."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from cost_router.infrastructure.env import read_int, read_str


@dataclass(frozen=True)
class Settings:
    """Everything configurable about a run."""

    models: dict[str, str]
    workers: int
    log_level: str
    data_dir: Path
    prompts_dir: Path
    config_dir: Path
    router_config_path: Path
    fixtures_dir: Path
    reports_dir: Path

    @classmethod
    def from_env(cls, env: Mapping[str, str], root: Path) -> Settings:
        """Read and validate; raises ConfigError on a bad value."""
        config_dir = Path(read_str(env, "CONFIG_DIR", str(root / "config")))
        return cls(
            models={
                "small": read_str(env, "TIER_SMALL", "qwen2.5:0.5b"),
                "medium": read_str(env, "TIER_MEDIUM", "llama3.2:1b"),
                "large": read_str(env, "TIER_LARGE", "qwen2.5:1.5b"),
            },
            workers=read_int(env, "WORKERS", 1, minimum=1),
            log_level=read_str(env, "LOG_LEVEL", "INFO"),
            data_dir=Path(read_str(env, "DATA_DIR", str(root / "data"))),
            prompts_dir=root / "prompts",
            config_dir=config_dir,
            router_config_path=Path(read_str(env, "ROUTER_CONFIG", str(config_dir / "router.json"))),
            fixtures_dir=Path(read_str(env, "FIXTURES_DIR", str(root / "tests" / "fixtures"))),
            reports_dir=Path(read_str(env, "REPORTS_DIR", str(root / "reports"))),
        )
