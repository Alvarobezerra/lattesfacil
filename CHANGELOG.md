# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/). Versionamento semântico (MAJOR.MINOR.PATCH).

## [Não lançado]

### Adicionado
- Integração contínua (GitHub Actions): roda a suíte de testes a cada push e pull request.
- `tests/rodar_todos.py`: executor único da suíte (scripts `teste_*.py` + pytest).
- `.env.example`, `requirements-dev.txt` e `pytest.ini`.

### Alterado
- `requirements.txt` agora limita a versão maior de cada dependência.

### Conhecido
- `teste_leitura_comum.py`: histórico escolar devolve "Matemática" em vez de "Licenciatura em Matemática".
- `teste_api_classificacao.py` depende de um PDF fora do repositório.
