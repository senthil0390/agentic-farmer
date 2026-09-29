import logging


# ============================================================
# LOGGER CONFIGURATION
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    ),
    handlers=[
        logging.FileHandler(
            "agent.log",
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
)


logger = logging.getLogger("farmer_agent")