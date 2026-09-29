import re


def normalize_whatsapp_phone(value: str | None) -> str | None:
    if value is None or not value.strip():
        return None

    digits = re.sub(r"\D", "", value)
    if not 8 <= len(digits) <= 15:
        raise ValueError("Informe um telefone válido com DDI, entre 8 e 15 dígitos.")
    return digits