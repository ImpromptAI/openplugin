import re

import pytest
from py.xml import html


@pytest.mark.optionalhook
def pytest_html_results_table_header(cells):
    del cells[1]
    del cells[2]
    cells.insert(1, html.th("Function"))
    cells.insert(2, html.th("Test case"))


def pytest_html_report_title(report):
    """modifying the title  of html report"""
    report.title = "Plugin Test Report"


@pytest.mark.optionalhook
def pytest_html_results_table_row(report, cells):
    del cells[1]
    del cells[2]
    tag = getattr(report, "tag", "")
    cells.insert(1, html.td(report.testcase))
    cells.insert(2, html.td(tag))


@pytest.mark.optionalhook
def pytest_html_results_summary(prefix, summary, postfix):
    """modifying the summary in pytest environment"""
    prefix.extend([html.h3("**Add prefix message**")])


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    function_name = str(item.function.__name__)[5:]
    report.testcase = function_name
    tag = re.split(r"\[|\]", report.nodeid)[-2]
    if function_name.startswith("openapi_parsing"):
        tag = f"openapi_doc_url= {tag.split('-')[0]}"
    elif function_name.startswith("function_calling_gpt4"):
        values = tag.split("-")
        tag = f"openplugin_manifest_url= {values[0]}, request_prompt= {values[1]}"
    report.tag = tag
