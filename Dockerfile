FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN sed -i '/-e ./d' requirements.txt && pip install --no-cache-dir -r requirements.txt

# Hugging Face embedding model cache build step (RAM crash se bachane ke liye)
RUN python -c "from langchain_huggingface import HuggingFaceEmbeddings; HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')"

COPY . .

EXPOSE 8501

# FINAL CMD MATRIX: Pehle background mein bina RAM overload ke test_agent chala kar 1 Million data seed hoga,
# uske baad hi Streamlit app active hogi.
CMD ["sh", "-c", "python test_agent.py && streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.fileWatcherType=none"]