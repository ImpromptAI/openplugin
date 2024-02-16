import pytest
import tempfile
import os


@pytest.fixture
def temp_file():
    # Create a temporary file
    temp = tempfile.NamedTemporaryFile(delete=False)
    yield temp.name
    # Ensure the file is cleaned up
    os.remove(temp.name)


def test_file_to_text_with_langchain1(temp_file):
    # Write some known content to the file
    known_content = "This is some test content"
    with open(temp_file, "w") as f:
        f.write(known_content)

    # Read the content from the file
    with open(temp_file, "r") as f:
        read_content = f.read()

    # Assert that the content read from the file is the same as the known content
    assert read_content == known_content
