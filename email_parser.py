"""Módulo de extração de comprovantes a partir de arquivos de e-mail (.eml).

Permite que o usuário arraste um e-mail salvo (do Gmail, Outlook, Thunderbird)
diretamente no LattesFácil com total privacidade, extraindo certificados em anexo
ou o texto da declaração sem conexão IMAP ou compartilhamento de senhas.
"""

from __future__ import annotations

import email
from email import policy
from typing import Any


def parse_eml_bytes(raw_bytes: bytes) -> dict[str, Any]:
    """Lê os bytes de um arquivo .eml e extrai metadados, texto e anexos."""
    try:
        msg = email.message_from_bytes(raw_bytes, policy=policy.default)
    except Exception:
        return {"error": "Arquivo de e-mail inválido ou corrompido.", "attachments": [], "body": "", "subject": ""}

    subject = str(msg.get("Subject", "") or "")
    sender = str(msg.get("From", "") or "")
    date_str = str(msg.get("Date", "") or "")
    
    body_text_parts = []
    attachments = []

    for part in msg.walk():
        ctype = part.get_content_type()
        cdispo = str(part.get("Content-Disposition", "") or "")
        filename = part.get_filename() or ""

        # Verifica se é anexo
        if "attachment" in cdispo or filename:
            try:
                payload = part.get_payload(decode=True)
                if payload:
                    attachments.append({
                        "filename": filename or "anexo.pdf",
                        "data": payload,
                        "content_type": ctype,
                        "size": len(payload)
                    })
            except Exception:
                pass
        elif ctype == "text/plain":
            try:
                content = part.get_content()
                if content:
                    body_text_parts.append(str(content))
            except Exception:
                pass

    full_body = "\n".join(body_text_parts).strip()

    # Prioriza anexos em PDF (certificados típicos) e imagens (PNG, JPG)
    pdf_attachments = [a for a in attachments if a["filename"].lower().endswith(".pdf")]
    image_attachments = [a for a in attachments if re.search(r"\.(png|jpe?g|webp|bmp|tiff?)$", a["filename"], re.I)]

    return {
        "ok": True,
        "subject": subject,
        "sender": sender,
        "date": date_str,
        "body": full_body,
        "attachments_count": len(attachments),
        "pdf_attachments": pdf_attachments,
        "first_pdf": pdf_attachments[0] if pdf_attachments else None,
        "image_attachments": image_attachments,
        "first_image": image_attachments[0] if image_attachments else None,
    }
