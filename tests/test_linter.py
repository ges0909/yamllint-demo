from yamllint import linter
from yamllint.config import YamlLintConfig

yaml_script = r"""---
issue: "test case"  # 0, 0

steps:              # 2, 0

  1. test step:     # 4, 2
    use: none       # 5, 4
"""


def test_linter_default_config():
    conf = YamlLintConfig(content="extends: default")
    gen = linter.run(input=yaml_script, conf=conf)
    problems = list(gen)
    assert not problems


def test_linter_relaxed_config():
    conf = YamlLintConfig(content="extends: relaxed")
    for problem in linter.run(input=yaml_script, conf=conf):
        # print(f"line {problem.line:<4} : {problem.level:<7} : {problem.desc}")
        print(f"line {problem.line} column {problem.column}: {problem.desc}")


def test_linter_custom_config():
    conf = YamlLintConfig(file="yamllint_custom_config.yaml")
    for problem in linter.run(input=yaml_script, conf=conf):
        print(f"{problem.level}, line {problem.line} column {problem.column}, {problem.desc} (rule: {problem.rule})")


# yamllint --config-data "{extends: relaxed, rules: {new-lines: {type: dos}}}" yaml_script.yaml
