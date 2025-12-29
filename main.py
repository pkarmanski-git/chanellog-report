from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from git import Repo
from llama_cpp import Llama
import os

app = FastAPI(title="Git Report Generator AI")

# Załadowanie modelu raz przy starcie aplikacji
MODEL_PATH = os.getenv("MODEL_PATH", "/app/models/Llama-3.2-3B-Instruct-Q4_K_M.gguf")
llm = Llama(model_path=MODEL_PATH, n_ctx=4096, n_threads=4)

class ReportRequest(BaseModel):
    project_name: str
    commits: str

@app.post("/generate-report")
async def generate_report_endpoint(req: ReportRequest):
    try:
        if not req.commits.strip():
            return {"report": "Brak zmian do zaraportowania."}

        prompt = (
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
            "Jesteś profesjonalnym asystentem. Tworzysz raporty zmian dla klientów.\n"
            f"Projekt: {req.project_name}<|eot_id|>"
            "<|start_header_id|>user<|end_header_id|>\n\n"
            f"Przygotuj raport na podstawie tych commitów:\n{req.commits}<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n\n"
        )

        result = llm(prompt, max_tokens=1000, stop=["<|eot_id|>"])
        return {"report": result['choices'][0]['text'].strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)