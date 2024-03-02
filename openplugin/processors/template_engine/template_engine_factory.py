from openplugin.processors import ProcessorImplementationType

from .template_engine import TemplateEngine


def get_template_engine(
    implementation_type: ProcessorImplementationType, metadata: dict
) -> TemplateEngine:
    if implementation_type == ProcessorImplementationType.TEMPLATE_ENGINE_WITH_JINJA:
        from .template_engine_with_jinja import TemplateEngineWithJinja

        return TemplateEngineWithJinja(**metadata)
    else:
        raise ValueError("Invalid implementation type: {}".format(implementation_type))
