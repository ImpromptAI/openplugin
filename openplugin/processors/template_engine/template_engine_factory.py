from ..processor import ProcessorImplementationType
from .template_engine import TemplateEngine


def get_template_engine(
    implementation_type: ProcessorImplementationType, metadata: dict
) -> TemplateEngine:
    if implementation_type == ProcessorImplementationType.TEMPLATE_ENGINE_WITH_JINJA:
        from .implementations.template_engine_with_jinja import (
            TemplateEngineWithJinja,
        )

        return TemplateEngineWithJinja(**metadata)
    elif implementation_type == ProcessorImplementationType.TEMPLATE_ENGINE_WITH_JSX:
        from .implementations.template_engine_with_jsx import TemplateEngineWithJSX

        return TemplateEngineWithJSX(**metadata)
    else:
        raise ValueError("Invalid implementation type: {}".format(implementation_type))
