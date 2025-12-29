import sys
from git import Repo
from llama_cpp import Llama
from pathlib import Path

def get_commits(repo_path, base_commit, head_commit):
    repo = Repo(repo_path)
    commits = repo.iter_commits(f"{base_commit}..{head_commit}")
    return [f"{c.hexsha[:7]}: {c.message.strip()}" for c in commits]

def generate_report(commits, output_file):
    llm = Llama(
        model_path="/app/models/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
        n_ctx=4096,
        n_threads=8
    )

    prompt = f"""
    Jesteś asystentem piszącym raport zmian dla klienta.
    Nie używaj żargonu technicznego.
    Nie zgaduj – opieraj się wyłącznie na podanych zmianach.
    
    Zwróć raport w sekcjach:
    1. Nowe funkcje
    2. Poprawki
    3. Zmiany techniczne (jeśli istotne)
    
    Lista commitów:
    {chr(10).join(commits)}
    """
    result = llm(prompt, max_tokens=1000)

    Path(output_file).write_text(result['choices'][0]['text'].strip())
    print(f"Raport zapisany w {output_file}")

if __name__ == "__main__":
    repo_path = sys.argv[1]     # ścieżka repo
    base_commit = sys.argv[2]   # np. HEAD^
    head_commit = sys.argv[3]   # np. HEAD
    output_file = sys.argv[4]   # np. /app/reports/CHANGELOG_CLIENT.md

    commits = get_commits(repo_path, base_commit, head_commit)
    generate_report(commits, output_file)
