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
    repo_path: str

@app.post("/generate-report")
async def generate_report_endpoint(req: ReportRequest):
    try:
        # 1. Pobieranie commitów
        repo = Repo(req.repo_path)

        commits = list(repo.iter_commits(f"HEAD~5..HEAD"))

        print(commits)

        if not commits:
            return {"message": "Brak nowych commitów do analizy."}

        commits_list = "\n".join([f"- {c.message.strip()}" for c in commits])

        # OFICJALNY FORMAT LLAMA 3.2
        prompt = (
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
            "Jesteś profesjonalnym asystentem. Tworzysz czytelne raporty zmian dla klientów biznesowych. "
            "Nie używaj żargonu technicznego. Skup się na korzyściach dla użytkownika.<|eot_id|>"
            "<|start_header_id|>user<|end_header_id|>\n\n"
            f"Na podstawie poniższej listy commitów przygotuj raport w sekcjach: "
            f"1. Nowe funkcje, 2. Poprawki, 3. Zmiany techniczne.\n\n"
            f"Lista commitów:\n{commits_list}<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n\n"
        )

        # Wywołanie modelu
        result = llm(
            prompt,
            max_tokens=1000,
            stop=["<|eot_id|>"], # Ważne: model przestanie pisać po wygenerowaniu końca odpowiedzi
            temperature=0.7
        )

        report = result['choices'][0]['text'].strip()
        return {"report": report}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)