"""
Script: TalentHub → SmartHub
Renomeia todas as ocorrências nos arquivos HTML do projeto.

Como usar:
1. Coloque este arquivo na pasta raiz do projeto (ao lado da pasta telenthub/)
2. Abra o terminal nessa pasta
3. Execute: python rename_to_smarthub.py
"""

import os
import re

# ── Mapeamento de substituições ─────────────────────────────────────────────
REPLACEMENTS = [
    # Nome principal (ordem importa — mais específico primeiro)
    ("TalentHub - RH Inteligente",      "SmartHub - RH Inteligente"),
    ("TalentHub | ",                     "SmartHub | "),
    ("| TalentHub",                      "| SmartHub"),
    ("TalentHub",                        "SmartHub"),
    ("Talenthub",                        "Smarthub"),
    ("talenthub",                        "smarthub"),
    ("TALENTHUB",                        "SMARTHUB"),

    # Textos de marketing/slogan comuns
    ("Conectando talentos e empresas",   "O RH inteligente do futuro"),
    ("Encontre seu próximo talento",     "Encontre seu próximo talento com SmartHub"),

    # Meta tags e SEO
    ('content="TalentHub',              'content="SmartHub'),
    ('property="og:site_name" content="TalentHub"', 'property="og:site_name" content="SmartHub"'),
]

# ── Pastas e extensões a processar ──────────────────────────────────────────
TARGET_EXTENSIONS = (".html", ".css", ".js", ".json", ".md")
SKIP_DIRS = {".git", "node_modules", "__pycache__"}

# ── Cores no terminal ────────────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def process_file(filepath):
    """Aplica todas as substituições em um arquivo."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            original = f.read()
    except (UnicodeDecodeError, PermissionError):
        return False, 0

    content = original
    count = 0

    for old, new in REPLACEMENTS:
        if old in content:
            occurrences = content.count(old)
            content = content.replace(old, new)
            count += occurrences

    if count > 0:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True, count

    return False, 0


def scan_directory(root_dir):
    """Percorre o diretório e processa todos os arquivos relevantes."""
    modified = []
    skipped  = []
    total_replacements = 0

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Ignorar pastas desnecessárias
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        for filename in filenames:
            if not any(filename.endswith(ext) for ext in TARGET_EXTENSIONS):
                continue

            filepath = os.path.join(dirpath, filename)
            changed, count = process_file(filepath)

            rel_path = os.path.relpath(filepath, root_dir)
            if changed:
                modified.append((rel_path, count))
                total_replacements += count
            else:
                skipped.append(rel_path)

    return modified, skipped, total_replacements


def main():
    # Detectar pasta automaticamente
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Procurar a pasta do projeto
    candidates = ["telenthub", "talentehub", "talenthub", "."]
    target_dir = None

    for candidate in candidates:
        path = os.path.join(script_dir, candidate)
        if os.path.isdir(path):
            target_dir = path
            break

    if not target_dir:
        target_dir = script_dir

    print(f"\n{BOLD}🔄 SmartHub Renamer{RESET}")
    print(f"📁 Pasta alvo: {target_dir}\n")

    modified, skipped, total = scan_directory(target_dir)

    # Relatório
    if modified:
        print(f"{GREEN}{BOLD}✅ Arquivos modificados ({len(modified)}):{RESET}")
        for path, count in sorted(modified):
            print(f"   {GREEN}✔{RESET}  {path}  {YELLOW}({count} substituições){RESET}")
    else:
        print(f"{YELLOW}⚠️  Nenhum arquivo precisou de alteração.{RESET}")

    if skipped:
        print(f"\n{RESET}⏭️  Arquivos sem ocorrências: {len(skipped)}")

    print(f"\n{BOLD}{'─'*50}{RESET}")
    print(f"{BOLD}📊 Total de substituições: {GREEN}{total}{RESET}")
    print(f"{BOLD}📝 Arquivos alterados:     {GREEN}{len(modified)}{RESET}")
    print(f"\n{GREEN}{BOLD}🚀 Pronto! Faça o push no GitHub e o Vercel atualiza automaticamente.{RESET}\n")


if __name__ == "__main__":
    main()
