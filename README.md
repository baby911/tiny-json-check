# tiny-json-check

A small, dependency-free Python command-line tool for checking JSON files.
一个零第三方依赖的 JSON 检查工具，适用于本地配置文件和 CI 检查。

## Features / 功能

- Detect JSON syntax errors and duplicate object keys, including nested objects.
- Reject non-standard `NaN`, `Infinity`, and `-Infinity` values.
- Read UTF-8 files (optional BOM) or standard input; leave source files unchanged.
- Check multiple files and return a nonzero exit code if any check fails.
- Work entirely offline, with a 10 MiB input limit per file.

## Quick start / 快速开始

Requires Python 3.9 or newer. No installation or API key is needed.
Download or clone this repository, then run from its directory:

```sh
python3 json_check.py examples/valid.json
python3 json_check.py config.json settings.json
printf '%s' '{"hello":"world"}' | python3 json_check.py -
```

Valid files print `OK <path>` to stdout. Invalid or unreadable files print
`FAIL <path>: <reason>` to stderr. JSON syntax errors include line and column.
Exit codes: `0` = all valid, `1` = at least one failed, `2` = command usage error.

```sh
printf '%s' '{"a":1,"a":2}' | python3 json_check.py -
# FAIL -: duplicate object key: 'a'
```

## Scope and limits / 范围和限制

This checks syntax and duplicate keys; it does not validate a JSON Schema or
application-specific requirements. Top-level scalar values are accepted.
Numbers use decimal parsing to avoid binary floating-point overflow during
validation. Deeply nested input is limited by Python's parser. The byte limit
does not imply a fixed memory limit after parsing. Use only on files you intend
to inspect; error messages can contain object key names.

## Development / 开发

```sh
python3 -m unittest -v
```

This is a newly started project. It has no established adoption or download
metrics. The initial implementation, documentation, and tests were created with
AI assistance and checked locally. Community review and bug reports are welcome.

## Contributing / 贡献

Open an issue with the command, Python version, expected result, and a minimal
JSON example with sensitive data removed. For a fix, add a regression test,
run the test command above, and submit a pull request. Possible future work:
JSON Lines support and machine-readable diagnostic output.

## License

MIT. See [LICENSE](LICENSE).
