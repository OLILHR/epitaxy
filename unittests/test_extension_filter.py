import os
import re

from alloy.collector import consolidate, escape_markdown_characters
from alloy.filter import filter_extensions, parse_extensions


def test_consolidate_only_specified_filters(
    project_root, mock_project, mock_operations, mock_alloyignore
):  # pylint: disable=unused-argument
    filtered_codebase, _, _ = consolidate(project_root, extensions=["md", "txt"])

    assert not any(extension in mock_alloyignore for extension in [".md", ".txt", ".py", ".yml"])
    assert re.search(rf"#### {re.escape(escape_markdown_characters('markdown.md'))}", filtered_codebase)
    assert re.search(rf"#### {re.escape(escape_markdown_characters('text.txt'))}", filtered_codebase)

    assert not re.search(rf"#### {re.escape(escape_markdown_characters('python.py'))}", filtered_codebase)
    assert not re.search(
        rf"#### {re.escape(escape_markdown_characters(os.path.join('subdirectory', 'markup.yml')))}",
        filtered_codebase,
    )

    assert ".png" in mock_alloyignore
    assert not re.search(rf"#### {re.escape(escape_markdown_characters('image.png'))}", filtered_codebase)
    assert ".svg" in mock_alloyignore
    assert not re.search(
        rf"#### {re.escape(escape_markdown_characters(os.path.join('subdirectory', 'vector.svg')))}",
        filtered_codebase,
    )


def test_extension_filter_bypasses_alloyignore(
    project_root, mock_project, mock_operations, mock_alloyignore
):  # pylint: disable=unused-argument
    filtered_codebase, _, _ = consolidate(project_root, extensions=["svg"])

    assert ".svg" in mock_alloyignore
    assert re.search(
        rf"#### {re.escape(escape_markdown_characters(os.path.join('subdirectory', 'vector.svg')))}",
        filtered_codebase,
    )

    assert not re.search(rf"#### {re.escape(escape_markdown_characters('markdown.md'))}", filtered_codebase)
    assert not re.search(rf"#### {re.escape(escape_markdown_characters('text.txt'))}", filtered_codebase)
    assert not re.search(rf"#### {re.escape(escape_markdown_characters('python.py'))}", filtered_codebase)
    assert not re.search(
        rf"#### {re.escape(escape_markdown_characters(os.path.join('subdirectory', 'markup.yml')))}",
        filtered_codebase,
    )
    assert not re.search(rf"#### {re.escape(escape_markdown_characters('image.png'))}", filtered_codebase)


def test_filter_extensions_edge_cases():
    assert filter_extensions("test.py", []) is True
    assert filter_extensions("test.py", None) is True
    assert filter_extensions("test.py", ["py"]) is True

    assert filter_extensions("test", ["py"]) is False
    assert filter_extensions(".gitignore", ["py"]) is False


def test_parse_extensions_edge_cases():
    assert parse_extensions(None, None, "") is None
    assert parse_extensions(None, None, ["py, js, css"]) == ["py", "js", "css"]
    assert parse_extensions(None, None, ["py", "js", "css"]) == ["py", "js", "css"]
