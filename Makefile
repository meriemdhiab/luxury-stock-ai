.PHONY: install all data pipeline train evaluate predict reports drift retrain quality-demo test app clean

install:
	python -m pip install -r requirements.txt

all: data pipeline train evaluate predict reports drift

data:
	python scripts/generate_data.py

pipeline:
	python 03_pipeline/src/run_pipeline.py

train:
	python 04_ai/src/train.py

evaluate:
	python 04_ai/src/evaluate.py

predict:
	python 04_ai/src/predict.py

reports:
	python scripts/generate_reports.py

drift:
	python scripts/check_drift.py

retrain:
	python scripts/retrain_if_needed.py

quality-demo:
	python 03_pipeline/src/run_quality_fixture.py

test:
	python -m pytest -q

app:
	streamlit run app/streamlit_app.py

clean:
	rm -rf data/processed logs .pytest_cache 04_ai/models database/luxury_stock_pipeline.sqlite
	find . -name __pycache__ -type d -prune -not -path './.venv/*' -exec rm -rf {} +
