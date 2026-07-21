FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN sed -i '/-e ./d' requirements.txt && pip install --no-cache-dir -r requirements.txt

RUN python -c "from langchain_huggingface import HuggingFaceEmbeddings; HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')"

COPY . .

RUN PYTHONPATH=. python src/components/upload_data.py

EXPOSE 8501

CMD ["sh", "-c", "PYTHONPATH=. python test_agent.py && PYTHONPATH=. python -c 'from src.components.schema_retriever import SchemaRetrieverComponent; SchemaRetrieverComponent()' && streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.fileWatcherType=none"]