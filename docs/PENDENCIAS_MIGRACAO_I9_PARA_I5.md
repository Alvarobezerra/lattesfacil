# Pendências da migração i9 (16 GB) → i5 (24 GB)

Relatório de 25/11/2026. O que buscar na máquina i9 e o que conferir aqui.

## 1. Buscar na máquina i9 (prioridade alta)

Estes três arquivos estavam apagados no working tree do i5. Restaurei a versão do último commit (`20057f1`), mas a cópia do i9 tinha alterações **não commitadas** que se perderam na transferência.

| Arquivo | O que falta / indício |
|---|---|
| `extractor.py` | Faltava `extract_text_from_image_bytes` (usada por `server.py` e `tests/test_gemini.py`). **Reescrevi uma versão mínima** (OCR via PyMuPDF/Tesseract, senão texto vazio). Substituir pela original do i9. |
| `classificador.py` | Pode ter alterações não commitadas. Não detectei nome faltando, mas não é prova de que está igual. |
| `itens/leitores.py` | Idem. O `server.py` novo importa `montar_resposta` daqui, e o nome existe. |

**Como buscar:** copie os três arquivos do i9 por cima dos daqui. Depois rode:

```powershell
git diff HEAD --stat -- extractor.py classificador.py itens/leitores.py
python -m unittest tests.test_gemini
```

O `git diff` mostra o que as cópias do i9 têm de diferente do último commit.

## 2. Conferir no i9 (o que mais pode ter ficado para trás)

- **Arquivos sem rastreio no Git** (não existem no GitHub, só em disco). Confirme que chegaram aqui: `gemini.py`, `iniciar_gemini.py`, `ferramentas/diagnosticar_gemini.py`, `ferramentas/seed_curriculos.py`, `tests/test_gemini.py`, `tests/teste_evidencias_recentes.py`, `docs/metodologia-reconhecimento-extracao.md`.
- **Arquivos ignorados pelo `.gitignore`** (nunca vão pelo Git, só por cópia): `.acesso` (código de acesso local), `lattes_records.db` (banco real), `data/`, `tests/curriculos/`, `tests/curriculos e modelos/`, `tests/base_documentos_teste/`, `Lattes para referencia/`, `ferramentas/saida/`, `tests/amostras_sinteticas/nome.local.txt` e `tests/amostras_sinteticas/pdf/`.
  - Compare a data e o tamanho do banco com os de `backups/`. O backup mais recente aqui é de 23/11/2026 07:48.
- **Alterações não commitadas em outros arquivos:** há 24 arquivos modificados aqui (`server.py`, `static/*`, `lote.py`, etc.). Compare com o i9 (`git status`, `git diff --stat`) para ver se o i9 tem mais coisas do que veio.
- **Variáveis de ambiente:** a chave do Gemini (`GEMINI_API_KEY`, `GEMINI_ENABLED`, `GEMINI_MODEL`) vive só no terminal do i9. Aqui precisa configurar de novo (`python iniciar_gemini.py`).

## 3. Reparar neste i5

- **`.git` danificado:** `git fsck` aponta 16 objetos ausentes (blob do `README.md` do commit raiz, entre outros). O histórico antigo está incompleto. Plano: clonar `Alvarobezerra/lattesfacil` de novo, comparar com esta pasta e só então apagar a antiga. Antes, confirme que o último commit está no GitHub.
- **Tesseract** (opcional): sem ele, imagens só são lidas se o Gemini estiver ligado. Para OCR local, instale o Tesseract com o idioma `por`.
- **Python:** local é 3.14.7 e o `render.yaml` usa 3.11.8. Fixe 3.11 num `.venv`. O `torch` 2.14 instalado globalmente não é usado pelo projeto.

## 4. Critério de "pronto"

- [ ] Três arquivos do i9 copiados e `git diff` revisado
- [ ] `python -c "import server"` sem erro
- [ ] `python -m unittest` dos testes principais passando
- [ ] Banco e `.acesso` conferidos
- [ ] Clone novo do GitHub comparado e `.git` saneado
