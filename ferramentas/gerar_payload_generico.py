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


def carga(item):
    spec = especificacao(item)
    var = spec["variantes"][0]
    v = VALORES[item]
    campos = []
    for c in var["campos"]:
        if (c.get("oculto") and not c.get("mostrar_quando")) or c.get("bloqueado_no_lattes"):
            continue
        valor = str(v.get(c["name"], ""))
        campos.append({"name": c["name"], "rotulo": c["rotulo"], "tipo": c["tipo"], "valor": valor, "codigo": (c.get("opcoes") or {}).get(valor, ""), "auto": False, "auto_de": ""})
    return {"tipo_producao": "generico", "__usuario": USUARIO, "__origem": "", "__autoSalvar": True, "__semAlerta": True,
            "__generico": {"id": item, "item": spec["item"], "como_abrir": spec["como_abrir"], "url": var["url"], "lista": spec.get("lista", ""), "campos": campos, "faltam": [], "grades": GRADES[item]}}


if __name__ == "__main__":
    item = sys.argv[1]
    saida = RAIZ / "ferramentas" / "saida"
    saida.mkdir(exist_ok=True)
    (saida / f"payload_{item}.js").write_text("window.__payloadTeste = " + json.dumps(carga(item), ensure_ascii=False) + ";\n", encoding="utf-8")
    print("gerado", [(c["name"], c["valor"][:25]) for c in carga(item)["__generico"]["campos"] if c["valor"]])
