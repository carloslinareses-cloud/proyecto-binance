#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Binance Paper Trader  --  SIMULACION (paper trading). NO usa API keys, NO ejecuta
ordenes reales. Solo lee precios PUBLICOS de Binance y simula una estrategia.

Disenado para correr UNA vez por invocacion (ideal para GitHub Actions / cron):
carga el estado previo desde docs/data/state.json, hace una iteracion y guarda.

Estrategia de ejemplo (facil de cambiar): cruce de medias moviles simples (SMA).
  - SMA rapida (FAST) por encima de SMA lenta (SLOW) -> senal LONG (comprar)
  - SMA rapida por debajo -> senal FLAT (vender / quedarse en efectivo)
Long-only, un "sub-portafolio" virtual por cada simbolo.
"""
import json
import csv
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ----------------------- Configuracion -----------------------
# Endpoint PUBLICO de datos de Binance (sin API key y sin bloqueo geografico en
# los runners de GitHub, a diferencia de api.binance.com que devuelve 451 en EEUU)
BASE = "https://data-api.binance.vision"
SYMBOLS = ["BTCUSDT", "ETHUSDT"]
INTERVAL = "15m"          # temporalidad de las velas
FAST = 7                  # periodo SMA rapida
SLOW = 25                 # periodo SMA lenta
START_CASH_PER_SYMBOL = 5000.0   # capital virtual (USDT) por simbolo
FEE = 0.001               # comision simulada por operacion (0.1%)
MAX_TRADES = 200          # cuantas operaciones guardar en el historial
MAX_EQUITY_POINTS = 2000  # cuantos puntos de la curva de capital guardar

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")
STATE_FILE = os.path.join(DATA_DIR, "state.json")
CSV_FILE = os.path.join(DATA_DIR, "history.csv")


def http_get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "paper-trader/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def get_closes(symbol):
    """Devuelve la lista de precios de cierre de las ultimas velas."""
    url = "{}/api/v3/klines?symbol={}&interval={}&limit={}".format(
        BASE, symbol, INTERVAL, SLOW + 5)
    data = http_get_json(url)
    return [float(c[4]) for c in data]   # indice 4 = precio de cierre


def sma(values, n):
    if len(values) < n:
        return None
    return sum(values[-n:]) / n


def new_symbol_state():
    return {
        "start_cash": START_CASH_PER_SYMBOL,
        "cash": START_CASH_PER_SYMBOL,
        "position": 0.0,      # cantidad de moneda en cartera
        "avg_entry": 0.0,     # precio promedio de entrada
        "price": 0.0,
        "sma_fast": 0.0,
        "sma_slow": 0.0,
        "signal": "FLAT",
        "equity": START_CASH_PER_SYMBOL,
    }


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (ValueError, OSError):
            pass
    return {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "mode": "SIMULATION (paper trading) - sin ordenes reales",
        "config": {"interval": INTERVAL, "fast": FAST, "slow": SLOW,
                   "fee": FEE, "start_cash_per_symbol": START_CASH_PER_SYMBOL},
        "symbols": {s: new_symbol_state() for s in SYMBOLS},
        "trades": [],
        "equity_history": [],
    }


def run():
    os.makedirs(DATA_DIR, exist_ok=True)
    st = load_state()
    now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")

    total_equity = 0.0
    total_start = 0.0

    for sym in SYMBOLS:
        s = st["symbols"].setdefault(sym, new_symbol_state())
        for k, v in new_symbol_state().items():
            s.setdefault(k, v)

        closes = get_closes(sym)
        price = closes[-1]
        f = sma(closes, FAST)
        sl = sma(closes, SLOW)
        signal = "FLAT"
        if f is not None and sl is not None:
            signal = "LONG" if f > sl else "FLAT"

        # --- Ejecutar la operacion simulada segun el cambio de senal ---
        if signal == "LONG" and s["position"] == 0.0 and s["cash"] > 0:
            qty = (s["cash"] * (1 - FEE)) / price
            st["trades"].insert(0, {
                "time": now_iso, "symbol": sym, "side": "BUY",
                "price": round(price, 2), "qty": round(qty, 8),
                "value": round(s["cash"], 2)})
            s["position"] = qty
            s["avg_entry"] = price
            s["cash"] = 0.0
        elif signal == "FLAT" and s["position"] > 0.0:
            qty = s["position"]
            proceeds = qty * price * (1 - FEE)
            pnl = proceeds - (qty * s["avg_entry"])
            st["trades"].insert(0, {
                "time": now_iso, "symbol": sym, "side": "SELL",
                "price": round(price, 2), "qty": round(qty, 8),
                "value": round(proceeds, 2), "pnl": round(pnl, 2)})
            s["cash"] = proceeds
            s["position"] = 0.0
            s["avg_entry"] = 0.0

        s["price"] = price
        s["sma_fast"] = round(f, 2) if f else 0.0
        s["sma_slow"] = round(sl, 2) if sl else 0.0
        s["signal"] = signal
        s["equity"] = round(s["cash"] + s["position"] * price, 2)

        total_equity += s["equity"]
        total_start += s["start_cash"]

    st["trades"] = st["trades"][:MAX_TRADES]
    st["updated_at"] = now_iso
    st["total"] = {
        "equity": round(total_equity, 2),
        "start": round(total_start, 2),
        "pnl": round(total_equity - total_start, 2),
        "pnl_pct": round((total_equity / total_start - 1) * 100, 2) if total_start else 0.0,
    }

    point = {"time": now_iso, "total_equity": round(total_equity, 2)}
    for sym in SYMBOLS:
        point[sym] = round(st["symbols"][sym]["price"], 2)
    st["equity_history"].append(point)
    st["equity_history"] = st["equity_history"][-MAX_EQUITY_POINTS:]

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(st, f, indent=2, ensure_ascii=False)

    write_header = not os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(["time", "total_equity", "total_pnl"]
                       + ["{}_price".format(s) for s in SYMBOLS]
                       + ["{}_signal".format(s) for s in SYMBOLS])
        w.writerow([now_iso, round(total_equity, 2), round(total_equity - total_start, 2)]
                   + [round(st["symbols"][s]["price"], 2) for s in SYMBOLS]
                   + [st["symbols"][s]["signal"] for s in SYMBOLS])

    print("[{}] equity={:.2f} pnl={:+.2f} ({:+.2f}%)".format(
        now_iso, total_equity, total_equity - total_start, st["total"]["pnl_pct"]))
    for sym in SYMBOLS:
        s = st["symbols"][sym]
        print("  {}: price={:.2f} fast={} slow={} signal={} equity={:.2f}".format(
            sym, s["price"], s["sma_fast"], s["sma_slow"], s["signal"], s["equity"]))


if __name__ == "__main__":
    run()
