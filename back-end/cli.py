#!/usr/bin/env python3
import argparse, logging, requests, websocket
from clients.st_client import st_client
from clients.tv_client import tv_client


def cli():
    ap = argparse.ArgumentParser()

    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("on")
    sub.add_parser("off")
    sub.add_parser("toggle_mute", help="Toggle mute on/off")

    v = sub.add_parser("vol")
    v.add_argument("dir", choices=["up", "down"])
    v.add_argument("steps", type=int, nargs="?", default=1)

    tok = sub.add_parser("token", help="SmartThings token operations")
    tok.add_argument("action", choices=["check", "renew"])

    args = ap.parse_args()

    # pylint: disable=no-value-for-parameter
    try:
        if args.cmd == "on":
            tv_client.turn_tv_on()
        elif args.cmd == "off":
            tv_client.turn_tv_off()
        elif args.cmd == "vol":
            tv_client.volume(direction=args.dir, steps=args.steps)
        elif args.cmd == "token":
            if args.action == "check":
                logging.info("Checking token...")
                st_client.ensure_token()
            elif args.action == "renew":
                st_client.TOKEN = ""
                st_client.ensure_token()
        elif args.cmd == "toggle_mute":
            tv_client.toggle_mute()
    except (RuntimeError, requests.exceptions.RequestException, websocket.WebSocketException, OSError) as e:
        logging.error(e)


if __name__ == "__main__":
    cli()
