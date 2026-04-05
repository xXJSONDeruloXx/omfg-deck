# omfg-deck TDD — Near-Full Coverage

## Goal
Write a pytest suite covering all Python backend modules. Target: red→green, near-full coverage across all public methods and edge cases.

## Modules to cover
- `config_schema.py` — `ConfigurationManager`: get_defaults, validate, generate_toml, parse_toml, roundtrip
- `configuration.py` — `ConfigurationService`: get_config, update_config, update_field, reset_config (with backup), file-not-found path, parse error path
- `installation.py` — `InstallationService`: check_installation (all combos), uninstall (files present/absent), _extract_and_install (zip layout), _write_default_config, _write_wrapper_script, cleanup_on_uninstall, _get_release_asset_url fallback, _version_newer
- `base_service.py` — `BaseService`: path construction, _ensure_directories, _remove_if_exists, _atomic_write
- `plugin.py` — `Plugin`: all async methods mocked at service layer, _version_newer edge cases, get_launch_option path construction

## Constraints
- No real network calls (mock `urllib.request.urlopen`)
- No real filesystem (use `pyfakefs` or `tmp_path` fixtures)
- Mock `decky` module (not available outside deck)
- pytest + pytest-mock + pyfakefs already installed
- Tests live in `tests/`
- `conftest.py` sets up mock_logger, mock_decky, patches Path.home()

## Working directory
`/Users/kurt/Developer/omfg-deck`

## Reference pattern
`/Users/kurt/Developer/decky-lossless-scaling-vk/tests/` — same stack, same fixture patterns
