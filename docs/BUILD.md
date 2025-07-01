
# Format & typecheck

```shell
cd ..
ruff check --select I --fix fastapi_utk
ruff format .
mypy fastapi_utk 
```


# Build & publishing

```shell
cd ..
rm -rf ./dist
uv pip compile pyproject.toml -o requirements.txt
uv build
uv publish
```
