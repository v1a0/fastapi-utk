# Run

```shell
python3.12 -m venv env
. ./env/bin/activate

python -m pip install -r requirements.txt

uvicorn app:create_app --factory --reload
```

# Open Swagger

> http://127.0.0.1:8000/docs