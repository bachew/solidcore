import logging
import structlog


def init(json: bool = False):
    # See https://www.structlog.org/en/stable/standard-library.html#suggested-configurations
    common_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.processors.StackInfoRenderer(),
    ]

    common_processors += [
        structlog.processors.UnicodeDecoder(),
    ]

    structlog.configure(
        processors=common_processors + [  # type: ignore
            # Prepare event dict for `ProcessorFormatter`.
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter_processors: list = [
        # Remove _record & _from_structlog.
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
    ]

    if json:
        formatter_processors.extend([
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ])
    else:
        formatter_processors.extend([
            structlog.dev.ConsoleRenderer()
        ])

    handler = logging.StreamHandler()
    handler.setFormatter(structlog.stdlib.ProcessorFormatter(
        # These run ONLY on `logging` entries that do NOT originate within
        # structlog.
        foreign_pre_chain=common_processors,  # type: ignore
        # These run on ALL entries after the pre_chain is done.
        processors=formatter_processors,
    ))
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)


def set_verbosity(verbosity: int):
    l = logging  # noqa
    lvl_root = l.WARNING
    lvl_sh = l.INFO

    if verbosity >= 1:
        lvl_root = l.INFO
        lvl_sh = l.DEBUG

    if verbosity >= 2:
        lvl_root = l.DEBUG

    levels = {
        '': lvl_root,
        'dev.sh': lvl_sh,
    }

    for name, level in levels.items():
        logging.getLogger(name).setLevel(level)


def log_all_levels(name):
    log = structlog.get_logger(name)

    for method_name in ['critical', 'error', 'warning', 'info', 'debug']:
        getattr(log, method_name)(method_name.title())
