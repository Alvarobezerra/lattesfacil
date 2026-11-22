"""Gera ferramentas/saida/payload_<item>.js (carga de salvamento de teste, fase 7) a partir do spec, sem leitor de documento.
Uso: python ferramentas/gerar_payload_generico.py banca
Os valores de teste ficam em VALORES (por item); todo título leva o prefixo ZZ-TESTE-LATTESFACIL."""
import json
import os
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from itens import especificacao  # noqa: E402

USUARIO = "Álvaro Antônio Bezerra dos Santos"
P = "ZZ-TESTE-LATTESFACIL"
VALORES = {
    "banca": {"F_COD_PROD": "Graduação", "f_titulo": f"{P} Banca de teste (validação automática)", "f_ano": "2024", "f_pais": "Brasil", "F_IDIOMA": "Português",
              "f_nme_orient": "ZZ Candidato de Teste", "f_inst": "Universidade Federal do Maranhão", "f_curso": "Farmácia", "f_ref": "Papel na banca: membro (teste automático)."},
    "patente": {"f_natureza": "Produto", "f_tipo": "Patente de Invenção", "f_titulo": f"{P} Patente de teste (validação automática)", "f_cod_reg": "BR1020200000001",
                "f_inst": "INPI - Instituto Nacional da Propriedade Industrial", "f_pais": "Brasil", "f_sta_inovacao": "Sim", "f_txt_potencial": "Teste automático de validação",
                "f_ref": "Teste automático de validação do formulário."},
    "banca_comissao_julgadora": {"F_COD_PROD": "Concurso público", "f_titulo": f"{P} Comissão julgadora de teste (validação automática)", "f_ano": "2024", "f_pais": "Brasil",
                                 "F_IDIOMA": "Português", "f_inst": "Universidade Federal do Maranhão", "f_ref": "Teste automático de validação do formulário."},
}
GRADES = {
    "patente": {"autores": [{"nome": USUARIO, "citacao": "SANTOS, A. A. B."}, {"nome": "ZZ Coautor de Teste", "citacao": "TESTE, Z. C."}], "titulares_pessoa": [USUARIO],
                "situacoes": [{"nome": "Depósito", "data": "15/03/2020"}], "palavras_chave": ["teste", "validação"], "areas": ["Microbiologia"]},
    "banca_comissao_julgadora": {"autores": [{"nome": USUARIO, "citacao": "SANTOS, A. A. B."}, {"nome": "ZZ Coautor de Teste", "citacao": "TESTE, Z. C."}], "palavras_chave": ["teste", "validação"], "areas": ["Microbiologia"]},
    "banca": {"autores": [{"nome": USUARIO, "citacao": "SANTOS, A. A. B."}, {"nome": "ZZ Coautor de Teste", "citacao": "TESTE, Z. C."}], "palavras_chave": ["teste", "validação"], "areas": ["Microbiologia"]},
}


def valores_automaticos(var, item=""):
    """Valores de teste preenchendo 100% dos campos preenchíveis do spec (obrigatórios, opcionais, condicionais, traduções e lupas)."""
    v = {}
    url_low = str(var.get("url", "")).lower()
    eh_aceito = "aceito" in (item + " " + var.get("variante", "")).lower()
    for c in var["campos"]:
        n, nl = c["name"], c["name"].lower()
        if c.get("bloqueado_no_lattes") or (c.get("oculto") and not c.get("mostrar_quando")) or c.get("automatico"):
            continue
        ops = c.get("opcoes") or {}
        maxl = c.get("maxlength") or 99
        if nl == "f_titulo":
            v[n] = f"{P} Teste de {item or var['variante']} (validação automática)"[: (c.get("maxlength") or 140)]
        elif nl in ("f_ano_ini", "f_ano_inic"):
            v[n] = "2022"
        elif nl == "f_ano" or nl.startswith("f_ano_"):
            v[n] = "2026" if eh_aceito and nl == "f_ano" else "2024"
        elif nl in ("f_pais", "f_pais_r", "f_pais_i", "f_pais_nacio", "f_pais_nasc", "fpaispassaporte"):
            v[n] = "Brasil" if "Brasil" in ops else next((k for k, cod in ops.items() if cod not in ("", "Selecione")), "")
        elif nl in ("f_idioma", "f_cod_idioma", "f_idioma_obra"):
            v[n] = "Português" if "Português" in ops else next((k for k, cod in ops.items() if cod not in ("", "Selecione")), "")
        elif "dta" in nl or nl.startswith("f_data"):
            v[n] = "15/03/2020"
        elif nl == "f_cod_reg":
            v[n] = "BR1020200000001"[:maxl]
        elif nl == "f_inst" and c.get("entra_pela_abertura"):
            v[n] = "INPI - Instituto Nacional da Propriedade Industrial"
        elif nl == "f_inst" and "ultivar" in var["variante"] + item:
            v[n] = "MAPA - Serviço Nacional de Proteção de Cultivares"
        elif nl in ("f_inst", "f_inst_dout", "f_inst_dout_sw", "f_inst_dout_ct"):
            v[n] = "Universidade de São Paulo" if "pkg_formacao" in url_low else "Universidade Federal do Maranhão"
        elif nl == "f_orgao":
            v[n] = "Centro de Ciências de Imperatriz (CCIm)"
        elif nl == "f_curso":
            if re.search(r"f_nivel=(2|X)", var.get("url", "")) or "pkg_formacao_compl" in url_low:
                v[n] = "Computacao"
            elif "pkg_formacao" in url_low:
                v[n] = "Administração"
            else:
                v[n] = "Farmácia"
        elif nl == "f_nme_agencia":
            v[n] = "CNPq"
        elif nl == "f_vinc":
            v[n] = "Servidor público"
        elif nl in ("f_titulo_cap", "f_tit_obra"):
            v[n] = f"{P} Título de teste (validação automática)"[: (c.get("maxlength") or 255)]
        elif nl == "f_nme_evento":
            v[n] = f"{P} Evento de teste (validação automática)"[: (c.get("maxlength") or 255)]
        elif nl == "f_relev":
            v[n] = "não"  # o Lattes limita os itens "mais relevantes" e o currículo já tem o máximo
        elif nl == "f_sta_inovacao":
            v[n] = "Não"
        elif nl == "f_isbn":
            v[n] = "9788535902778"[: (c.get("maxlength") or 13)]
        elif nl == "f_issn":
            v[n] = "00348910"[:maxl]
        elif nl == "f_cod_doi":
            v[n] = "10.1371/journal.pmed.0020124"[: (c.get("maxlength") or 250)]
        elif nl in ("f_home_page", "f_homepage") or nl.startswith("f_homepage_"):
            v[n] = "https://lattes.cnpq.br"[:maxl]
        elif nl.startswith("f_email_"):
            v[n] = "teste@ufma.br"[:maxl]
        elif nl in ("f_titulo_en", "f_titulo_cap_en"):
            v[n] = f"{P} Automatic validation test title"[: (c.get("maxlength") or 140)]
        elif nl == "f_ref_en":
            v[n] = "Automatic validation test of the form."[: (c.get("maxlength") or 3800)]
        elif nl == "f_txt_potencial":
            v[n] = "Potencial de inovação de teste (validação automática)."[: (c.get("maxlength") or 400)]
        elif nl in ("f_cidade", "f_cidade_ed", "f_cidade_evento", "f_cidade_nasc") or nl.startswith("f_munic_"):
            v[n] = "São Luís"[:maxl]
        elif nl.startswith("f_estado_") or nl.startswith("f_uf_"):
            v[n] = (next((k for k, cod in ops.items() if cod not in ("", "Selecione")), "") if ops else "MA")[:maxl]
        elif nl.startswith("f_cep_"):
            v[n] = "65000000"[:maxl]
        elif nl.startswith("f_ddd_"):
            v[n] = "98"[:maxl]
        elif nl.startswith("f_fone_") or nl.startswith("f_fax_"):
            v[n] = "32728000"[:maxl]
        elif nl.startswith("f_ramal_") or nl.startswith("f_caixa_"):
            v[n] = "100"[:maxl]
        elif nl in ("f_edicao", "f_pag_ini", "f_volume", "f_volume_l", "f_volume_c", "f_serie", "f_fasciculo"):
            v[n] = "1"
        elif nl in ("f_pag_fim", "f_paginas", "f_duracao", "f_carga"):
            v[n] = "10"[:maxl]
        elif nl in ("f_meses_sw", "f_meses_sw_aux", "f_indiceh", "f_qtd_citacoes", "f_qtd_trabalhos"):
            v[n] = "6"[:maxl]
        elif nl == "f_mes_ini":
            v[n] = "03"
        elif nl == "f_mes_fim":
            v[n] = "11"
        elif nl == "f_res_id":
            v[n] = "A-1000-2024"[:maxl]
        elif nl == "f_query":
            v[n] = "https://scholar.google.com/citations?user=teste"[:maxl]
        elif c["tipo"] in ("radio", "select") and ops:
            v[n] = next((k for k, cod in ops.items() if cod not in ("", "Selecione")), "")
        elif c["tipo"] == "checkbox":
            v[n] = next((k for k, cod in ops.items() if cod not in ("", "Selecione")), next(iter(ops), "S")) if ops else "S"
        elif c["tipo"] == "textarea":
            v[n] = "Teste automático de validação do formulário."[: (c.get("maxlength") or 3800)]
        else:
            v[n] = "Teste de validação"[:maxl]
    return v


def grades_automaticas(var, item=""):
    ch = {g["chave"] for g in var.get("grades", [])}
    g = {}
    if "autores" in ch:
        tit = {"nome": USUARIO, "citacao": "SANTOS, A. A. B."}
        if item == "projeto" or "instituicoes_envolvidas" in ch:
            tit["coordenador"] = True
        g["autores"] = [tit, {"nome": "ZZ Coautor de Teste", "citacao": "TESTE, Z. C."}]
    if "titulares_pessoa" in ch:
        g["titulares_pessoa"] = [USUARIO]
    if "titulares_inst" in ch:
        g["titulares_inst"] = ["Universidade Federal do Maranhão"]
    if "situacoes" in ch:
        g["situacoes"] = [{"nome": "Depósito", "data": "15/03/2020"}]
    if "palavras_chave" in ch:
        g["palavras_chave"] = ["teste", "validação"]
    if "areas" in ch:
        g["areas"] = ["Microbiologia"]
    if "setores" in ch:
        g["setores"] = ["Educação superior"]
    if "instituicoes_envolvidas" in ch:
        g["instituicoes_envolvidas"] = ["Universidade Federal do Maranhão"]
    if "financiamentos" in ch:
        g["financiamentos"] = ["CNPq; 123456; REAL; 10000; Auxílio Financeiro"]
    if "nomes_citacao" in ch:
        g["nomes_citacao"] = ["SANTOS, A. A. B."]
    if "contatos" in ch:
        g["contatos"] = ["E-mail; teste@ufma.br"]
    if "redes_sociais" in ch:
        g["redes_sociais"] = ["LinkedIn; https://linkedin.com/in/teste"]
    return g


def carga(item, idx=0):
    spec = especificacao(item)
    var = spec["variantes"][idx]
    v = {} if os.environ.get("SEM_ALTERAR") else {**valores_automaticos(var, spec["item"]), **VALORES.get(item, {})}  # SEM_ALTERAR=1: abre o registro atual e salva sem mudar nada
    campos = []
    for c in var["campos"]:
        if (c.get("oculto") and not c.get("mostrar_quando")) or c.get("bloqueado_no_lattes"):
            continue
        valor = str(v.get(c["name"], ""))
        cod = (c.get("opcoes") or {}).get(valor, "")
        campos.append({
            "name": c["name"], "rotulo": c["rotulo"], "tipo": c["tipo"], "valor": valor, "codigo": cod,
            "codigos": [cod] if c["tipo"] == "checkbox" and cod else [],
            "auto": bool(c.get("automatico")), "auto_de": c.get("auto_de", ""),
        })
    grades = {} if os.environ.get("SEM_ALTERAR") else {**grades_automaticas(var, item), **GRADES.get(item, {})}
    return {"tipo_producao": "generico", "__usuario": USUARIO, "__origem": "", "__autoSalvar": True, "__semAlerta": True,
            "__generico": {"id": item if not idx else f"{item}_v{idx}", "item": spec["item"], "como_abrir": spec["como_abrir"], "url": var["url"], "lista": spec.get("lista", ""), "campos": campos, "faltam": [], "grades": grades}}


if __name__ == "__main__":
    item, _, idx = sys.argv[1].partition("#")  # "livro_capitulo#1" = segunda variante
    idx = int(idx or 0)
    saida = RAIZ / "ferramentas" / "saida"
    saida.mkdir(exist_ok=True)
    (saida / f"payload_{item}{'_v' + str(idx) if idx else ''}.js").write_text("window.__payloadTeste = " + json.dumps(carga(item, idx), ensure_ascii=False) + ";\n", encoding="utf-8")
    print("gerado", [(c["name"], c["valor"][:25]) for c in carga(item, idx)["__generico"]["campos"] if c["valor"]])
