from fastapi import FastAPI

app = FastAPI(
    title='LLM Evaluation Platform',
    version='0.1.0'
)


@app.get('/health')
def health_check():
    return {
        'status': 'ok',
        'service': 'llm-evaluation-platform'
    }
