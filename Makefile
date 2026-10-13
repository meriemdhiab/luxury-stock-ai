.PHONY: install data pipeline train evaluate predict test app clean

install:
	python -m pip install -r requirements.txt

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

test:
	pytest -q
app:
	streamlit run app/streamlit_app.py
clean:
	rm -rf data/processed logs .pytest_cache __pycache__ 03_pipeline/src/__pycache__ 04_ai/src/__pycache__
reports:
	python scripts/generate_reports.py

quality-demo:
	python 03_pipeline/src/run_quality_fixture.py
