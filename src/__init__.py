from .core.logger import get_logger

logger = get_logger("src")

try:
    from .iris.iris import ask_stream
except Exception as e:
    logger.warning(f"Lazy import skipped: iris ({e})")

try:
    from .iris.rag import BookRetriever
except Exception as e:
    logger.warning(f"Lazy import skipped: iris_rag ({e})")

try:
    from .iris.engine import (
        download_gguf,
        load_model,
        unload_model,
        ModelRole,
        TaskType,
        get_device,
        load_generation_config,
    )
except Exception as e:
    logger.warning(f"Lazy import skipped: iris_engine ({e})")

try:
    from .iris.vision import analyze_image
except Exception as e:
    logger.warning(f"Lazy import skipped: iris_vision ({e})")

try:
    from .iris.coding import generate_internal_code
except Exception as e:
    logger.warning(f"Lazy import skipped: iris_coding ({e})")

try:
    from .core.syntax_checker import check_syntax, extract_code_blocks
except Exception as e:
    logger.warning(f"Lazy import skipped: syntax_checker ({e})")

try:
    from .hca.context_compactor import (
        estimate_tokens,
        compact_light,
        compact_context,
        auto_compact_for_role,
        CompactionLevel,
    )
except Exception as e:
    logger.warning(f"Lazy import skipped: context_compactor ({e})")

try:
    from .grpo.trainer import (
        train_with_grpo,
        GRPOConfig,
        GRPOTrainer,
        GRPOMetrics,
        GRPOSample,
        GRPODataset,
        RewardScorer,
        RewardDomain,
        GGUFPolicyBridge,
    )
except Exception as e:
    logger.warning(f"Lazy import skipped: grpo.trainer ({e})")

