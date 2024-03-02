import time

from loguru import logger


def time_taken(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        if func.__name__ == "_run_plugin_signature_selector":
            logger.log(
                "FLOW",
                f"[PLUGIN-SIGNATURE-SELECTOR-FINISHED], time_taken={round((end_time - start_time),4)} seconds",  # noqa: E501
            )
        elif func.__name__ == "_run_plugin_execution":
            logger.log(
                "FLOW",
                f"[PLUGIN-EXECUTION-FINISHED], time_taken={round((end_time - start_time),4)} seconds",  # noqa: E501
            )
        elif func.__name__ == "run_prompt_on_plugin":
            logger.log(
                "FLOW",
                f"[PLUGIN-PIPELINE-FINISHED], total_time_taken={round((end_time - start_time),4)} seconds",  # noqa: E501
            )
        elif func.__name__ == "run_processor":
            logger.log(
                "FLOW",
                f"{args[0].log_title}, total_time_taken={round((end_time - start_time),4)} seconds",  # noqa: E501
            )
        return result

    return wrapper
