from enum import Enum


class InpAction(Enum):
    AGENT_SETUP = "agent_setup"
    AGENT_PROMPT = "agent_prompt"
    AGENT_STOP = "agent_stop"
    AGENT_AUTH = "agent_auth"
    AGENT_CURRENT_SESSION_CLEAR = "agent_current_session_clear"
    AGENT_CURRENT_SESSION_PROMPTS = "agent_current_session_prompts"


class InpResponse(Enum):
    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

    MISSING_ACTION = ("missing_action", "Action object is missing")
    INCORRECT_ACTION = (
        "incorrect_action",
        "Incorrect action object. Please provide a valid action object",
    )
    AGENT_NOT_SETUP = ("agent_not_setup", "Agent setup required")
    AGENT_STOPPED = ("agent_stopped", "Agent stopped")
    AGENT_SESSION_CLEARED = ("agent_session_cleared", "Agent session cleared")
    AGENT_SESSION_PROMPTS = ("agent_session_prompts", "Agent session prompts")
    AGENT_JOB_FAILED = ("agent_job_failed", "Agent job failed")
    AGENT_ALREADY_SETUP = ("agent_already_setup", "Agent already setup")
    AGENT_JOB_STARTED = ("agent_job_started", "Agent job started")
    AGENT_JOB_STEP = ("agent_job_step", "")
    AGENT_MESSAGE_STREAMING = ("agent_message_streaming", "")
    AGENT_JOB_COMPLETED = ("agent_job_completed", "Agent job completed")
    INVALID_API_KEY = ("invalid_api_key", "Invalid API key")
    AGENT_BLOCKED = ("agent_blocked", "Agent blocked")
