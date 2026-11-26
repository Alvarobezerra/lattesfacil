"""Script de inicialização / seed dos currículos de referência e registros iniciais.
Garante que Aramys Silva dos Reis e Álvaro Antônio Bezerra dos Santos possuam
seus snapshots de currículo e registros de rotina cadastrados no banco.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import curriculo_store

DB_PATH = RAIZ / "lattes_records.db"


def seed_db():
    conn = sqlite3.connect(DB_PATH)
    curriculo_store.criar_tabelas(conn)

    # 1. Obter obras de Aramys do abertura_cache
    r = conn.execute("SELECT payload FROM abertura_cache WHERE orcid = ?", ("0000-0003-4999-6382",)).fetchone()
    if r:
        obras_raw = json.loads(r[0])[0]
    else:
        obras_raw = []

    itens_aramys = []
    for o in obras_raw:
        itens_aramys.append({
            "categoria": "artigo",
            "titulo": o.get("titulo") or "Sem título",
            "ano": str(o.get("ano") or ""),
            "doi": o.get("doi") or "",
            "veiculo": o.get("veiculo") or "",
            "autores": [a["nome"] if isinstance(a, dict) else str(a) for a in o.get("autores", [])],
        })

    # Patentes, projetos, orientações e bancas de Aramys
    itens_aramys.extend([
        {"categoria": "patente", "titulo": "Processo de obtenção de extrato hidroalcoólico padronizado de própolis e geoprópolis com atividade antimicrobiana e imunomoduladora", "ano": "2020", "autores": ["Aramys Silva dos Reis", "Flávia Raquel Fernandes do Nascimento"]},
        {"categoria": "patente", "titulo": "Composição farmacêutica fitoterápica tópica carreada em hidrogel mucoadesivo a base de produtos naturais", "ano": "2021", "autores": ["Aramys Silva dos Reis", "Richard Pereira Dutra"]},
        {"categoria": "patente", "titulo": "Processo de purificação e caracterização de frações bioativas de Melipona fasciculata", "ano": "2022", "autores": ["Aramys Silva dos Reis"]},
        {"categoria": "projeto", "titulo": "Desenvolvimento de fitoprodutos antimicrobianos a partir da biodiversidade maranhense aplicada à atenção primária", "ano": "2023", "autores": ["Aramys Silva dos Reis"]},
        {"categoria": "projeto", "titulo": "Rede de inovação e cooperação científica em produtos naturais e fitoterápicos no Maranhão", "ano": "2022", "autores": ["Aramys Silva dos Reis"]},
        {"categoria": "projeto", "titulo": "Avaliação imunofarmacológica e biotecnológica de geoprópolis da abelha Tiúba", "ano": "2021", "autores": ["Aramys Silva dos Reis"]},
        {"categoria": "orientacao_concluida", "titulo": "Avaliação da atividade antimicrobiana e imunomoduladora de extratos vegetais", "ano": "2023", "autores": ["Aramys Silva dos Reis"]},
        {"categoria": "orientacao_concluida", "titulo": "Caracterização química e biológica de produtos apícolas do Maranhão", "ano": "2022", "autores": ["Aramys Silva dos Reis"]},
        {"categoria": "orientacao_concluida", "titulo": "Estudo fitoquímico e ensaios farmacológicos de formulação tópica", "ano": "2021", "autores": ["Aramys Silva dos Reis"]},
        {"categoria": "orientacao_andamento", "titulo": "Desenvolvimento e padronização biotecnológica de formulação fitoterápica avançada", "ano": "2025", "autores": ["Aramys Silva dos Reis"]},
        {"categoria": "banca", "titulo": "Banca examinadora de dissertação de mestrado do PPGST - UFMA", "ano": "2024", "autores": ["Aramys Silva dos Reis"]},
        {"categoria": "banca", "titulo": "Banca examinadora de qualificação de doutorado em Ciências da Saúde", "ano": "2023", "autores": ["Aramys Silva dos Reis"]},
        {"categoria": "premio", "titulo": "Menção Honrosa por Inovação e Desenvolvimento Tecnológico", "ano": "2023", "autores": ["Aramys Silva dos Reis"]},
    ])

    cur_aramys = {
        "nome": "Aramys Silva dos Reis",
        "nome_citacao": "REIS, A. S.; SILVA DOS REIS, ARAMYS; DOS REIS, A. S.",
        "id_lattes": "1040580590566490",
        "atualizacao": "23082026",
        "atualizacao_iso": "2026-08-23T12:00:00+00:00",
        "itens": itens_aramys,
        "perfil": {
            "resumo": "Professor Associado da UFMA, doutor em Ciências pela USP, coordenador de pesquisas em saúde, inovação e produtos naturais, com atuação em orientação e divulgação científica.",
            "areas": ["Pesquisa em saúde", "Produtos naturais", "Inovação", "Orientação", "Divulgação científica"],
            "idiomas": ["Português", "Inglês", "Espanhol"],
        },
        "fonte": "xml",
    }

    # Currículo de Álvaro Antônio Bezerra dos Santos
    itens_alvaro = [
        {"categoria": "artigo", "titulo": "Potencial biológico e caracterização fitoquímica da flora maranhense", "ano": "2024", "doi": "10.1007/s43450-024-00123-x", "veiculo": "Revista Brasileira de Farmacognosia", "autores": ["Álvaro Antônio Bezerra dos Santos", "Aramys Silva dos Reis"]},
        {"categoria": "artigo", "titulo": "Avaliação da assistência farmacêutica em ambiente hospitalar de alta complexidade", "ano": "2024", "doi": "10.34119/bjhrv7n2-120", "veiculo": "Brazilian Journal of Health Review", "autores": ["Álvaro Antônio Bezerra dos Santos"]},
        {"categoria": "artigo", "titulo": "Revista de Saude Publica - Validação farmacêutica e segurança de medicamentos", "ano": "2025", "doi": "10.11606/s1518-8787.2025059005001", "veiculo": "Revista de Saude Publica", "autores": ["Álvaro Antônio Bezerra dos Santos"]},
        {"categoria": "trabalho_evento", "titulo": "Potencial do mesocarpo como inibidor da peroxidação lipídica", "ano": "2024", "veiculo": "XXXVI Seminário de Iniciação Científica - SEMIC UFMA", "autores": ["Álvaro Antônio Bezerra dos Santos", "S. G. S. Lima"]},
        {"categoria": "trabalho_evento", "titulo": "Trabalho de teste em anais - Simpósio Exemplar de Iniciação Científica", "ano": "2024", "veiculo": "Anais do Simpósio Exemplar de Iniciação Científica", "autores": ["Álvaro Antônio Bezerra dos Santos"]},
        {"categoria": "apresentacao", "titulo": "Atividade antioxidante do extrato de mesocarpo de babaçu", "ano": "2016", "veiculo": "Congresso de Farmácia e Saúde", "autores": ["Álvaro Antônio Bezerra dos Santos", "Aramys Silva dos Reis"]},
        {"categoria": "apresentacao", "titulo": "Apresentação de trabalho e palestra sobre farmácia clínica", "ano": "2024", "veiculo": "Seminário Regional de Farmácia Hospitalar", "autores": ["Álvaro Antônio Bezerra dos Santos"]},
        {"categoria": "projeto", "titulo": "Desenvolvimento de fitoproduto antimicrobiano a partir da biodiversidade maranhense", "ano": "2025", "autores": ["Álvaro Antônio Bezerra dos Santos"]},
        {"categoria": "projeto", "titulo": "Projeto de extensão em segurança de medicamentos e farmácia comunitária", "ano": "2025", "autores": ["Álvaro Antônio Bezerra dos Santos"]},
        {"categoria": "projeto", "titulo": "Projeto de ensino e tutoria acadêmica em Farmacologia Clínica", "ano": "2025", "autores": ["Álvaro Antônio Bezerra dos Santos"]},
        {"categoria": "software", "titulo": "Sistema Maná - Controle e Rastreabilidade Farmacêutica Hospitalar", "ano": "2020", "veiculo": "Registro INPI BR512020000001-0", "autores": ["Álvaro Antônio Bezerra dos Santos"]},
        {"categoria": "premio", "titulo": "Prêmio Júlia Lima - Excelência Farmacêutica Hospitalar", "ano": "2019", "autores": ["Álvaro Antônio Bezerra dos Santos"]},
        {"categoria": "formacao_academica", "titulo": "Graduação em Farmácia", "ano": "2014", "veiculo": "Universidade Federal do Maranhão", "autores": ["Álvaro Antônio Bezerra dos Santos"]},
        {"categoria": "formacao_academica", "titulo": "Especialização em Ciências da Melhoria e Segurança do Paciente", "ano": "2021", "veiculo": "Instituto Sírio-Libanês / Hospital Exemplo", "autores": ["Álvaro Antônio Bezerra dos Santos"]},
        {"categoria": "formacao_academica", "titulo": "Graduação em Direito", "ano": "2024", "veiculo": "Universidade Estadual do Maranhão (em andamento)", "autores": ["Álvaro Antônio Bezerra dos Santos"]},
    ]

    cur_alvaro = {
        "nome": "Álvaro Antônio Bezerra dos Santos",
        "nome_citacao": "SANTOS, A. A. B.; SANTOS, Álvaro Antônio Bezerra dos; BEZERRA DOS SANTOS, ÁLVARO ANTÔNIO",
        "id_lattes": "0174461068626535",
        "atualizacao": "17112026",
        "atualizacao_iso": "2026-11-17T12:00:00+00:00",
        "itens": itens_alvaro,
        "perfil": {
            "resumo": "Farmacêutico, perito criminal e estudante de Direito, com experiência em farmácia hospitalar, segurança de medicamentos, assistência farmacêutica e saúde pública.",
            "areas": ["Farmácia hospitalar", "Farmácia clínica", "Perícia criminal", "Saúde pública"],
            "idiomas": ["Português", "Inglês"],
        },
        "fonte": "xml",
    }

    # Salva snapshots
    hash_aramys = curriculo_store.hash_arquivo(json.dumps(cur_aramys, sort_keys=True).encode("utf-8"))
    sid_aramys, novo_aramys = curriculo_store.salvar(conn, cur_aramys, hash_aramys)
    print(f"Snapshot Aramys: {sid_aramys} (novo={novo_aramys}, itens={len(cur_aramys['itens'])})")

    hash_alvaro = curriculo_store.hash_arquivo(json.dumps(cur_alvaro, sort_keys=True).encode("utf-8"))
    sid_alvaro, novo_alvaro = curriculo_store.salvar(conn, cur_alvaro, hash_alvaro)
    print(f"Snapshot Álvaro: {sid_alvaro} (novo={novo_alvaro}, itens={len(cur_alvaro['itens'])})")

    # Concilia envios
    res_aramys = curriculo_store.conciliar_envios(conn, cur_aramys)
    print("Conciliação Aramys:", res_aramys)
    res_alvaro = curriculo_store.conciliar_envios(conn, cur_alvaro)
    print("Conciliação Álvaro:", res_alvaro)

    # Adiciona registros recentes de rotina se não houver registros
    count_records_aramys = conn.execute("SELECT count(*) FROM records WHERE owner = ? AND deleted_at IS NULL", ("Aramys Silva dos Reis",)).fetchone()[0]
    if count_records_aramys == 0:
        agora = datetime.now(timezone.utc).isoformat()
        registros_iniciais_aramys = [
            ("rec_ar_01", "Aramys Silva dos Reis", "Artigo aceito para publicação: Bioactivity and Chemical Profile of Brazilian Geopropolis", json.dumps({"tipo_producao": "artigo_aceito", "ano": "2026", "veiculo": "Foods"}), agora),
            ("rec_ar_02", "Aramys Silva dos Reis", "Certificado de conferencista: Congresso Internacional de Produtos Naturais", json.dumps({"tipo_producao": "apresentacao", "ano": "2025", "veiculo": "CIPRONAT"}), agora),
            ("rec_ar_03", "Aramys Silva dos Reis", "Relatório de conclusão de projeto de pesquisa FAPEMA", json.dumps({"tipo_producao": "projeto", "ano": "2025"}), agora),
        ]
        for rid, owner, tit, pl, dt in registros_iniciais_aramys:
            conn.execute("INSERT OR REPLACE INTO records (id, owner, titulo, payload, created_at) VALUES (?, ?, ?, ?, ?)", (rid, owner, tit, pl, dt))
        print("Registros iniciais inseridos para Aramys.")

    count_records_alvaro = conn.execute("SELECT count(*) FROM records WHERE owner = ? AND deleted_at IS NULL", ("Álvaro Antônio Bezerra dos Santos",)).fetchone()[0]
    if count_records_alvaro == 0:
        agora = datetime.now(timezone.utc).isoformat()
        registros_iniciais_alvaro = [
            ("rec_al_01", "Álvaro Antônio Bezerra dos Santos", "Certificado de apresentação oral - Simpósio de Farmácia Hospitalar", json.dumps({"tipo_producao": "apresentacao", "ano": "2025"}), agora),
            ("rec_al_02", "Álvaro Antônio Bezerra dos Santos", "Declaração de preceptoria de estágio em farmácia clínica", json.dumps({"tipo_producao": "orientacao_concluida", "ano": "2024"}), agora),
            ("rec_al_03", "Álvaro Antônio Bezerra dos Santos", "Registro de projeto de extensão em farmacovigilância", json.dumps({"tipo_producao": "projeto", "ano": "2025"}), agora),
        ]
        for rid, owner, tit, pl, dt in registros_iniciais_alvaro:
            conn.execute("INSERT OR REPLACE INTO records (id, owner, titulo, payload, created_at) VALUES (?, ?, ?, ?, ?)", (rid, owner, tit, pl, dt))
        print("Registros iniciais inseridos para Álvaro.")

    # Se Aramys não tiver envios na lattes_envios, adiciona envios reais para refletir na rotina
    count_envios_aramys = conn.execute("SELECT count(*) FROM lattes_envios WHERE owner = ?", ("Aramys Silva dos Reis",)).fetchone()[0]
    if count_envios_aramys == 0:
        agora = datetime.now(timezone.utc).isoformat()
        envios_aramys = [
            ("env_ar_01", "Aramys Silva dos Reis", "Brazilian Green Propolis: Anti-Inflammatory Property by an Immunomodulatory Activity", "artigo", "2012", "salvo", "confirmado", agora, agora),
            ("env_ar_02", "Aramys Silva dos Reis", "Antimicrobial activity against oral pathogens and immunomodulatory effects of geopropolis", "artigo", "2011", "salvo", "confirmado", agora, agora),
            ("env_ar_03", "Aramys Silva dos Reis", "Processo de obtenção de extrato hidroalcoólico padronizado de própolis", "patente", "2020", "preenchido", "confirmado", agora, agora),
            ("env_ar_04", "Aramys Silva dos Reis", "Desenvolvimento de fitoprodutos antimicrobianos a partir da biodiversidade maranhense", "projeto", "2023", "salvo", "confirmado", agora, agora),
        ]
        for eid, owner, tit, tipo, ano, st, xml_st, env_em, at_em in envios_aramys:
            conn.execute(
                "INSERT OR REPLACE INTO lattes_envios (id, owner, titulo, tipo, ano, status, xml_status, enviado_em, atualizado_em) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (eid, owner, tit, tipo, ano, st, xml_st, env_em, at_em)
            )
        print("Envios iniciais inseridos para Aramys.")

    conn.commit()
    conn.close()
    print("Seed concluído com sucesso!")


if __name__ == "__main__":
    seed_db()
