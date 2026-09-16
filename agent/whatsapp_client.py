import logging
import os
import re
import threading

try:
    from neonize import NewClient
    from neonize.proto.Neonize_pb2 import Message
    from neonize.utils.jid import build_jid
except ImportError:  # pragma: no cover - optional dependency for Neonize integration
    NewClient = None
    Message = None
    build_jid = None

logger = logging.getLogger(__name__)

_NEONIZE_CLIENT = None
_NEONIZE_THREAD = None
_NEONIZE_LOCK = threading.Lock()


def _is_neonize_connected(client) -> bool:
    if client is None:
        return False

    try:
        conn_state = getattr(client, "is_connected", None)
        if conn_state is not None:
            if callable(conn_state):
                return bool(conn_state())
            return bool(conn_state)
    except Exception:
        pass

    try:
        return bool(getattr(client, "connected", False))
    except Exception:
        return False


def _render_qr_to_terminal(qr_bytes: bytes):
    payload = qr_bytes.decode("utf-8", errors="replace").strip()

    if not payload:
        return None

    try:
        import qrcode

        qr = qrcode.QRCode(
            version=1,
            box_size=1,
            border=1
        )

        qr.add_data(payload)
        qr.make(fit=True)

        matrix = qr.get_matrix()

        print("\nNeonize QR code:\n")

        # Junta duas linhas do QR em uma linha do terminal
        for i in range(0, len(matrix), 2):
            upper = matrix[i]
            lower = (
                matrix[i + 1]
                if i + 1 < len(matrix)
                else [False] * len(upper)
            )

            line = ""

            for top, bottom in zip(upper, lower):
                if top and bottom:
                    line += "█"
                elif top:
                    line += "▀"
                elif bottom:
                    line += "▄"
                else:
                    line += " "

            print(line)

        print()

        return "qr-rendered"

    except Exception:
        print("\nNeonize QR code:")
        print("[QR rendering unavailable in this terminal]")
        print()

        return "qr-rendered"


def _normalize_whatsapp_target(value: str) -> str:
    raw = (value or "").strip()
    raw = raw.replace("whatsapp:", "").replace("+", "").replace(" ", "")
    raw = re.sub(r"[^0-9]", "", raw)
    return raw


def _provider_name() -> str:
    return os.getenv("WHATSAPP_PROVIDER", "neonize").strip().lower()


def _extract_message_text(message) -> str:
    if message is None:
        return ""

    payload = getattr(message, "Message", None)
    if payload is not None:
        conversation = getattr(payload, "conversation", None)
        if conversation:
            return str(conversation)

        extended = getattr(payload, "extendedTextMessage", None)
        if extended is not None and getattr(extended, "text", None):
            return str(extended.text)

    conversation = getattr(message, "conversation", None)
    if conversation:
        return str(conversation)

    extended = getattr(message, "extendedTextMessage", None)
    if extended is not None and getattr(extended, "text", None):
        return str(extended.text)

    return ""


def _extract_sender_number(message) -> str:
    if message is None:
        return ""

    info = getattr(message, "Info", None)
    source = getattr(info, "MessageSource", None) if info is not None else None
    if source is None:
        payload = getattr(message, "Message", None)
        if payload is not None:
            info = getattr(payload, "Info", None)
            source = getattr(info, "MessageSource", None) if info is not None else None
        if source is None:
            return ""

    sender = getattr(source, "Sender", None) or getattr(source, "Chat", None)
    if sender is None:
        return ""

    user = getattr(sender, "User", None)
    if user:
        return str(user)

    if getattr(sender, "Server", None):
        return _normalize_whatsapp_target(str(sender))

    return _normalize_whatsapp_target(str(sender))


def _extract_reply_target_jid(message):
    if message is None:
        return None

    info = getattr(message, "Info", None)
    source = getattr(info, "MessageSource", None) if info is not None else None
    if source is None:
        payload = getattr(message, "Message", None)
        if payload is not None:
            info = getattr(payload, "Info", None)
            source = getattr(info, "MessageSource", None) if info is not None else None
        if source is None:
            return None

    # Prefer the chat JID (current conversation), then sender variants.
    for attr_name in ("Chat", "Sender", "SenderAlt", "RecipientAlt"):
        jid = getattr(source, attr_name, None)
        if jid is None:
            continue

        user = getattr(jid, "User", None)
        server = getattr(jid, "Server", None)
        if user and server:
            return jid

    return None


def get_neonize_client():
    global _NEONIZE_CLIENT

    if NewClient is None or Message is None or build_jid is None:
        return None

    with _NEONIZE_LOCK:
        if _NEONIZE_CLIENT is None:
            client_name = os.getenv("NEONIZE_CLIENT_NAME", "smart-schedule-agent").strip() or "smart-schedule-agent"
            client = NewClient(client_name)

            @client.event(Message)
            def _on_message(_client, message):
                from agent.agent import handle_message

                text = _extract_message_text(message)
                sender = _extract_sender_number(message)
                target_jid = _extract_reply_target_jid(message)
                if not text:
                    return

                normalized_sender = _normalize_whatsapp_target(sender)
                if target_jid is None and not normalized_sender:
                    return

                if target_jid is not None:
                    user = getattr(target_jid, "User", "")
                    server = getattr(target_jid, "Server", "")
                    logger.info("Mensagem recebida via Neonize de %s@%s", user, server)
                else:
                    logger.info("Mensagem recebida via Neonize de %s", normalized_sender)

                reply = handle_message(text)
                send_whatsapp_message(target_jid if target_jid is not None else normalized_sender, reply)

            def _on_qr(_client, qr_bytes):
                text = qr_bytes.decode("utf-8", errors="replace").strip()
                logger.warning("Neonize QR gerado. Exibindo código no terminal.")
                _render_qr_to_terminal(qr_bytes)
                if text.startswith("https://") or text.startswith("http://"):
                    logger.debug("URL de login do Neonize recebida para autenticação.")

            client.event.qr(_on_qr)
            _NEONIZE_CLIENT = client

        return _NEONIZE_CLIENT


def start_neonize_listener() -> None:
    global _NEONIZE_THREAD

    if _provider_name() != "neonize":
        return

    client = get_neonize_client()
    if client is None:
        logger.warning("Neonize nao instalado; listener do WhatsApp nao foi iniciado.")
        return

    if _is_neonize_connected(client):
        if _NEONIZE_THREAD is None or not _NEONIZE_THREAD.is_alive():
            _NEONIZE_THREAD = threading.Thread(target=lambda: None, daemon=True, name="neonize-whatsapp-listener")
        return

    if _NEONIZE_THREAD and _NEONIZE_THREAD.is_alive():
        return

    def _runner():
        try:
            if not _is_neonize_connected(client):
                client.connect()
            logger.info("Cliente Neonize conectado e aguardando mensagens do WhatsApp.")
        except Exception as exc:  # pragma: no cover
            logger.error(f"Falha ao iniciar o cliente Neonize: {exc}")

    _NEONIZE_THREAD = threading.Thread(target=_runner, daemon=True, name="neonize-whatsapp-listener")
    _NEONIZE_THREAD.start()


def stop_neonize_listener() -> None:
    global _NEONIZE_CLIENT, _NEONIZE_THREAD

    client = _NEONIZE_CLIENT
    if client is not None:
        for method_name in ("stop", "disconnect"):
            method = getattr(client, method_name, None)
            if callable(method):
                try:
                    method()
                except Exception as exc:  # pragma: no cover
                    logger.warning(f"Falha ao encerrar cliente Neonize via {method_name}: {exc}")
                break
    _NEONIZE_CLIENT = None
    _NEONIZE_THREAD = None


def _send_via_neonize(to, body: str) -> None:
    client = get_neonize_client()
    if client is None:
        logger.warning("Neonize nao instalado; mensagem nao enviada.")
        return

    target = None
    target_for_log = ""

    if hasattr(to, "SerializeToString") or (hasattr(to, "User") and hasattr(to, "Server")):
        target = to
        target_for_log = f"{getattr(to, 'User', '')}@{getattr(to, 'Server', '')}"
    else:
        normalized = _normalize_whatsapp_target(str(to))
        if not normalized:
            logger.error("Destino do WhatsApp invalido para Neonize: %s", to)
            return

        if build_jid is not None:
            target = build_jid(normalized, "s.whatsapp.net")
            target_for_log = f"{normalized}@s.whatsapp.net"
        else:
            target = normalized
            target_for_log = normalized

    try:
        if not _is_neonize_connected(client):
            client.connect()

        client.send_message(target, str(body), link_preview=False)
        logger.info("Mensagem enviada via Neonize WhatsApp para %s.", target_for_log)
    except Exception as exc:
        logger.error(f"Falha ao enviar mensagem via Neonize: {exc}")


def send_whatsapp_message(to: str, body: str) -> None:
    provider = _provider_name()
    if provider != "neonize":
        raise ValueError("WHATSAPP_PROVIDER deve ser 'neonize'.")

    try:
        _send_via_neonize(to, body)
    except Exception as exc:  # pragma: no cover
        logger.error(f"Erro ao enviar mensagem via Neonize: {exc}")
        raise
