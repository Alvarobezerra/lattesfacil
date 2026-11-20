"""Gera ferramentas/saida/payload_<item>.js (carga de salvamento de teste, fase 7) a partir do spec, sem leitor de documento.
Uso: python ferramentas/gerar_payload_generico.py banca
Os valores de teste ficam em VALORES (por item); todo título leva o prefixo ZZ-TESTE-LATTESFACIL."""
import json
import pathlib
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
    """Valores de teste para itens sem VALORES próprio: primeira opção válida de cada seleção/opção, país Brasil, idioma Português, título com o prefixo de teste."""
    v = {}
    for c in var["campos"]:
        n, nl = c["name"], c["name"].lower()
        if c.get("bloqueado_no_lattes") or (c.get("oculto") and not c.get("mostrar_quando")):
            continue
        ops = c.get("opcoes") or {}
        if nl in ("f_titulo",):
            v[n] = f"{P} Teste de {item or var['variante']} (validação automática)"[:140]
        elif nl == "f_ano" or nl.startswith("f_ano_"):
            v[n] = "2024"
        elif nl == "f_pais":
            v[n] = "Brasil"
        elif nl == "f_idioma":
            v[n] = "Português"
        elif "dta" in nl or nl.startswith("f_data"):
            v[n] = "15/03/2020"
        elif nl == "f_cod_reg":
            v[n] = "BR1020200000001"
        elif nl == "f_inst" and c.get("entra_pela_abertura"):
            v[n] = "INPI - Instituto Nacional da Propriedade Industrial"
        elif nl == "f_inst" and "ultivar" in var["variante"] + item:
            v[n] = "MAPA - Serviço Nacional de Proteção de Cultivares"
        elif nl == "f_nme_evento":
            v[n] = f"{P} Evento de teste (validação automática)"
        elif nl == "f_relev":
            v[n] = "não"  # o Lattes limita os itens "mais relevantes" e o currículo já tem o máximo
        elif nl == "f_sta_inovacao":
            v[n] = "Não"
        elif nl in ("f_home_page", "f_homepage", "f_txt_potencial", "f_titulo_en", "f_ref_en", "f_inst", "f_curso", "f_nme_agencia") or c.get("lupa"):
            continue
        elif c["tipo"] in ("radio", "select") and ops:
            v[n] = next((k for k, cod in ops.items() if cod not in ("", "Selecione")), "")
        elif c["tipo"] == "textarea":
            v[n] = "Teste automático de validação do formulário."
        elif c["tipo"] == "text" and c.get("obrigatorio"):
            v[n] = "Teste de validação"
    return v


def grades_automaticas(var):
    ch = {g["chave"] for g in var.get("grades", [])}
    g = {}
    if "autores" in ch:
        g["autores"] = [{"nome": USUARIO, "citacao": "SANTOS, A. A. B."}, {"nome": "ZZ Coautor de Teste", "citacao": "TESTE, Z. C."}]
    if "titulares_pessoa" in ch:
        g["titulares_pessoa"] = [USUARIO]
    if "palavras_chave" in ch:
        g["palavras_chave"] = ["teste", "validação"]
    if "areas" in ch:
        g["areas"] = ["Microbiologia"]
    return g


def carga(item):
    spec = especificacao(item)
    var = spec["variantes"][0]
    v = VALORES.get(item) or valores_automaticos(var, spec["item"])
    campos = []
    for c in var["campos"]:
        if (c.get("oculto") and not c.get("mostrar_quando")) or c.get("bloqueado_no_lattes"):
            continue
        valor = str(v.get(c["name"], ""))
        campos.append({"name": c["name"], "rotulo": c["rotulo"], "tipo": c["tipo"], "valor": valor, "codigo": (c.get("opcoes") or {}).get(valor, ""), "auto": bool(c.get("automatico")), "auto_de": c.get("auto_de", "")})
    return {"tipo_producao": "generico", "__usuario": USUARIO, "__origem": "", "__autoSalvar": True, "__semAlerta": True,
            "__generico": {"id": item, "item": spec["item"], "como_abrir": spec["como_abrir"], "url": var["url"], "lista": spec.get("lista", ""), "campos": campos, "faltam": [], "grades": GRADES.get(item) or grades_automaticas(var)}}


if __name__ == "__main__":
    item = sys.argv[1]
    saida = RAIZ / "ferramentas" / "saida"
    saida.mkdir(exist_ok=True)
    (saida / f"payload_{item}.js").write_text("window.__payloadTeste = " + json.dumps(carga(item), ensure_ascii=False) + ";\n", encoding="utf-8")
    print("gerado", [(c["name"], c["valor"][:25]) for c in carga(item)["__generico"]["campos"] if c["valor"]])
