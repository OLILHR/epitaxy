import os
import re

from alloy.collector import consolidate, escape_markdown_characters, remove_trailing_whitespace
from alloy.filter import read_alloyignore


def test_read_alloyignore(project_root, mock_operations):  # pylint: disable=unused-argument

    exclude = read_alloyignore(project_root, [])

    assert exclude("test.png") is True
    assert exclude("test.svg") is True

    assert exclude("test.md") is False
    assert exclude("test.txt") is False
    assert exclude("test.py") is False
    assert exclude("test.yml") is False


def test_consolidate_removes_trailing_whitespace():
    input_content = "trailing whitespace         "
    expected_output = "trailing whitespace"

    output = remove_trailing_whitespace(input_content)

    assert output == expected_output
    assert not re.search(r"\n{3,}", output)
    assert not re.search(r" +$", output, re.MULTILINE)


def test_consolidate_excludes_ignored_files(
    project_root, mock_project, mock_operations
):  # pylint: disable=unused-argument
    codebase, _, _ = consolidate(project_root)
    alloyignore = mock_project[os.path.join(project_root, ".alloyignore")]

    assert ".png" in alloyignore
    assert ".svg" in alloyignore
    assert not re.search(rf"#### {re.escape(escape_markdown_characters('image.png'))}", codebase)
    assert not re.search(rf"#### {re.escape(escape_markdown_characters('vector.svg'))}", codebase)

    assert ".markdown.md" not in alloyignore
    assert ".python.py" not in alloyignore
    assert "text.txt" not in alloyignore
    assert re.search(rf"#### {re.escape(escape_markdown_characters('markdown.md'))}", codebase)
    assert re.search(rf"#### {re.escape(escape_markdown_characters('python.py'))}", codebase)
    assert re.search(rf"#### {re.escape(escape_markdown_characters('text.txt'))}", codebase)


def test_consolidate_considers_subdirectories(
    project_root, mock_project, mock_operations
):  # pylint: disable=unused-argument
    codebase, _, _ = consolidate(project_root)

    print(f"Mock project structure: {mock_project}")
    print(f"Consolidated codebase:\n{codebase}")

    assert re.search(rf"#### {re.escape(escape_markdown_characters('markdown.md'))}", codebase)
    assert re.search(rf"#### {re.escape(escape_markdown_characters('text.txt'))}", codebase)
    assert re.search(rf"#### {re.escape(escape_markdown_characters('python.py'))}", codebase)

    subdir_yml_path = os.path.join("subdirectory", "markup.yml")
    assert re.search(
        rf"#### {re.escape(escape_markdown_characters(subdir_yml_path))}", codebase
    ), f"File {subdir_yml_path} not found in consolidated output"

    subdir_svg_path = os.path.join("subdirectory", "vector.svg")
    assert not re.search(
        rf"#### {re.escape(escape_markdown_characters(subdir_svg_path))}", codebase
    ), f"File {subdir_svg_path} should be excluded as per .alloyignore"


def test_consolidate_file_token_count(project_root, mock_project, mock_operations):  # pylint: disable=unused-argument
    codebase, file_count, token_count = consolidate(project_root)

    expected_file_count = len(
        [
            f
            for f in mock_project.keys()
            if not f.endswith(".alloyignore") and not f.endswith(".png") and not f.endswith(".svg")
        ]
    )

    assert file_count == expected_file_count
    assert token_count > 0

    for file_path, content in mock_project.items():
        if not file_path.endswith((".alloyignore", ".png", ".svg")):
            escaped_path = escape_markdown_characters(os.path.relpath(file_path, project_root))
            assert re.search(rf"#### {re.escape(escaped_path)}", codebase)
            assert content in codebase
