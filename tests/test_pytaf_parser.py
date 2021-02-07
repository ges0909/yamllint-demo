import glob
from pathlib import Path

import lark
import pytest
from lark import UnexpectedToken
from yamllint import linter
from yamllint.config import YamlLintConfig

from parse.pytaf_parser import PytafParser, PytafParserError


@pytest.fixture
def parser():
    return PytafParser()


def read_file(path_: Path) -> str:
    with open(str(path_), "r") as stream:
        return stream.read()


# -- parser


def test_pytaf_grammar(parser):
    tree = parser.parse(
        r"""
    issue: test case id
    before:
        wait:
            input:
                duration: 5
    after:
    steps:
        test step id:
            skip: reason
            flaky: 3
            use: func call
            input:
                param:
                    env: value
            output:
                param1: value
    """
    )
    print("\n" + tree.pretty())


def test_pytaf_grammar_with_error(parser):
    try:
        tree = parser.parse(
            r"""
        issue: test case id
        steps:
            test step id:
            
            use: none
    """
        )
        print("\n" + tree.pretty())
    except UnexpectedToken as error:
        print(f"line {error.line} column {error.column}: syntax error: unexpected token '{error.token}'")


def test_pytaf_grammar_all_scripts(parser):
    for path in glob.glob("./scripts/*.yaml"):
        try:
            parser.parse(text=read_file(path))
        # except ruamel.yaml.parser.ParserError as error:
        #     pass
        except lark.UnexpectedToken as error:
            pytest.fail(
                msg=f"{Path(path).name} line {error.line} column {error.column}, unexpected token", pytrace=False
            )


# -- linter


def test_linter_pytaf_script():
    # conf = YamlLintConfig(content="extends: relaxed")
    conf = YamlLintConfig(file="yamllint_custom_config.yaml")
    for path in glob.glob("./scripts/*.yaml"):
        for problem in linter.run(input=path, conf=conf):
            print(
                f"{Path(path).name:<85} {problem.level:<7} line {problem.line} column {problem.column}: {problem.desc}"
            )


# -- linter + parser


def test_pytaf_all_scripts():
    conf = YamlLintConfig(file="yamllint_custom_config.yaml")
    parser = PytafParser()
    for path in glob.glob("./scripts/*.yaml"):
        text = read_file(path)
        try:
            for problem in linter.run(input=text, conf=conf):
                print(
                    f"{Path(path).name:<85} {problem.level:<7} line {problem.line} column {problem.column}: {problem.desc}"
                )
            parser.parse(text=text)
        # except ruamel.yaml.parser.ParserError as error:
        #     pass
        except lark.UnexpectedToken as error:
            pytest.fail(
                msg=f"{Path(path).name} line {error.line} column {error.column}, unexpected token", pytrace=False
            )


# -- parse all scripts


def test_pytaf_parse_all_scripts():
    errors = []
    parser = PytafParser()
    # lint_conf = YamlLintConfig(content="extends: relaxed")
    for path in Path("scripts").glob("*.yaml"):
        try:
            _ = parser.parse(path=path)
        except PytafParserError as error:
            errors.append(f"{error.path}, line {error.line} column {error.column}, {error.text}")
    print()
    for error in errors:
        print(error)
