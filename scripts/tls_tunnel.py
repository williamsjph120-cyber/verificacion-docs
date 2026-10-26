#!/usr/bin/env python3
"""
Tunel TLS local para Postgres (Render) — plan B cuando el libpq empaquetado
de psycopg2-binary falla el handshake TLS (caso visto en este equipo).

Como funciona: escucha PLANO en localhost y hacia el servidor remoto hace el
handshake TLS con el OpenSSL del sistema (que sí funciona). El cliente se
conecta al tunel con sslmode=disable; el trafico sale cifrado al remoto.

Uso:
    python3 scripts/tls_tunnel.py --remote-host dpg-xxxx.a.ohio-postgres.render.com

    # en otra terminal:
    psql 'postgresql://user:pass@127.0.0.1:5433/dbname?sslmode=disable'
"""
import argparse
import socket
import ssl
import threading

# Paquete SSLRequest de PostgreSQL: longitud 8 + codigo 80877103
SSL_REQUEST = b"\x00\x00\x00\x08\x04\xd2\x16\x2f"


def pump(src: socket.socket, dst: socket.socket) -> None:
    """Copia bytes de un socket a otro hasta EOF."""
    try:
        while True:
            data = src.recv(65536)
            if not data:
                break
            dst.sendall(data)
    except OSError:
        pass
    finally:
        for s in (src, dst):
            try:
                s.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass


def handle(client: socket.socket, remote_host: str, remote_port: int,
           ctx: ssl.SSLContext) -> None:
    try:
        remote = socket.create_connection((remote_host, remote_port), timeout=30)
        remote.sendall(SSL_REQUEST)
        if remote.recv(1) != b"S":  # el servidor rechazo SSL
            remote.close()
            client.close()
            return
        tls = ctx.wrap_socket(remote, server_hostname=remote_host)
        client.settimeout(None)
        tls.settimeout(None)
    except Exception as exc:  # noqa: BLE001
        print(f"   handshake falló: {exc}")
        try:
            client.close()
        except OSError:
            pass
        return

    print(f"   conexión relé activa ({remote_host})")
    t = threading.Thread(target=pump, args=(client, tls), daemon=True)
    t.start()
    pump(tls, client)


def main() -> None:
    ap = argparse.ArgumentParser(description="Tunel TLS local para Postgres")
    ap.add_argument("--remote-host", required=True)
    ap.add_argument("--remote-port", type=int, default=5432)
    ap.add_argument("--local-port", type=int, default=5433)
    args = ap.parse_args()

    ctx = ssl.create_default_context()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", args.local_port))
    server.listen(16)
    print(f"🔓 Tunel: 127.0.0.1:{args.local_port} -> tls://{args.remote_host}:"
          f"{args.remote_port}")
    print("   Conéctate con sslmode=disable (Ctrl+C para salir)")

    try:
        while True:
            client, _addr = server.accept()
            threading.Thread(
                target=handle,
                args=(client, args.remote_host, args.remote_port, ctx),
                daemon=True,
            ).start()
    except KeyboardInterrupt:
        print("\nTunel cerrado.")


if __name__ == "__main__":
    main()
