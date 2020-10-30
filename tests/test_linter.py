from yamllint import linter
from yamllint.config import YamlLintConfig

yaml_script = """\
issue: "test case"  # 0, 0
                    # 1
    steps:              # 2, 0
                    # 3
  1. test step:     # 4, 2
    use: none       # 5, 4
"""


def test_default_config():
    conf = YamlLintConfig(content="extends: default")
    gen = linter.run(input=yaml_script, conf=conf)
    errors = list(gen)
    assert not errors


def test_linter_relaxed_config():
    conf = YamlLintConfig(content="extends: relaxed")
    for problem in linter.run(input=yaml_script, conf=conf):
        # print(f"line {problem.line:<4} : {problem.level:<7} : {problem.desc}")
        print(f"{problem.line:>4}: {problem.desc}")


def test_custom_config():
    conf = YamlLintConfig(file="yamllint_custom_config.yaml")
    for error in linter.run(input=yaml_script, conf=conf):
        print(error)
