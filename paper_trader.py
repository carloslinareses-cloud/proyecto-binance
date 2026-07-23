#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Binance Paper Trader  --  SIMULACION (paper trading). NO usa API keys, NO ejecuta
ordenes reales. Solo lee precios PUBLICOS de Binance y simula la estrategia.

Corre UNA vez por invocacion (ideal para GitHub Actions / cron): carga el estado
previo, hace una iteracion y guarda.

ESTRATEGIA GANADORA POR ACTIVO (elegida tras backtestear 7 familias y validar
out-of-sample 2024 vs 2025+):
  - BTC: Donchian 20/10 (breakout tipo Turtle). Compra al romper el maximo de 20
         dias; vende al romper el minimo de 10 dias.  (+97%, Sharpe 1.12, positivo
         en ambos periodos)
  - ETH: cruce de medias SMA 7/25.  (+53%, positivo out-of-sample +55% en 2025+)
Long-only; empieza en USDT y compra en la senal. Un sub-portafolio por activo.
"""
import json
import csv
import os
import urllib.request
from datetime import datetime, timezone

# ----------------------- Configuracion -----------------------
BASE = "https://data-api.binance.vision"   # datos publicos, sin API key, sin bloqueo geografico
SYMBOLS = ["BTCUSDT", "ETHUSDT"]
INTERVAL = "1d"                 # temporalidad DIARIA
START_CASH_PER_SYMBOL = 12.5    # capital virtual (USDT) por simbolo -> $25 total
FEE = 0.001                     # comision simulada por operacion (0.1%)

# Estrategia por activo (validada out-of-sample)
STRATEGY = {
    "BTCUSDT": {"type": "donchian", "entry": 20, "exit": 10, "label": "Donchian 20/10 (breakout)"},
    "ETHUSDT": {"type": "sma", "fast": 7, "slow": 25, "label": "SMA 7/25 (cruce)"},
}

MAX_TRADES = 200
MAX_EQUITY_POINTS = 2000

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")
STATE_FILE = os.path.join(DATA_DIR, "state.json")
CSV_FILE = os.path.join(DATA_DIR, "history.csv")


def http_get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "paper-trader/2.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def get_klines(symbol):
    """Ultimas velas diarias como (high, low, close)."""
    url = "{}/api/v3/klines?symbol={}&interval={}&limit=40".format(BASE, symbol, INTERVAL)
    data = http_get_json(url)
    return [(float(c[2]), float(c[3]), float(c[4])) for c in data]


def sma(values, n):
    if len(values) < n:
        return None
    return sum(values[-n:]) / n


def compute_signal(sym, closes):
    """Devuelve (should_buy, should_sell, lvl_a, lvl_b, trend) segun la estrategia del activo."""
    price = closes[-1]
    strat = STRATEGY[sym]
    if strat["type"] == "sma":
        mf = sma(closes, strat["fast"])
        ms = sma(closes, strat["slow"])
        long_ok = (mf is not None and ms is not None and mf > ms)
        return long_ok, (not long_ok), (round(mf, 2) if mf else 0.0), \
            (round(ms, 2) if ms else 0.0), ("UP" if long_ok else "DOWN")
    # donchian
    en, ex = strat["entry"], strat["exit"]
    hi = max(closes[-en - 1:-1]) if len(closes) > en else None   # maximo de los `en` cierres previos
    lo = min(closes[-ex - 1:-1]) if len(closes) > ex else None   # minimo de los `ex` cierres previos
    should_buy = (hi is not None and price >= hi)
    should_sell = (lo is not None and price <= lo)
    trend = "UP" if (hi and lo and price >= (hi + lo) / 2) else "DOWN"
    return should_buy, should_sell, (round(hi, 2) if hi else 0.0), \
        (round(lo, 2) if lo else 0.0), trend


def new_symbol_state():
    return {
        "start_cash": START_CASH_PER_SYMBOL,
        "cash": START_CASH_PER_SYMBOL,
        "position": 0.0,
        "avg_entry": 0.0,
        "price": 0.0,
        "sma_fast": 0.0,   # SMA rapida  (o maximo del canal Donchian)
        "sma_slow": 0.0,   # SMA lenta   (o minimo del canal Donchian)
        "trend": "-",
        "signal": "FLAT",
        "strat": "",
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
        "config": {"interval": INTERVAL, "fee": FEE,
                   "start_cash_per_symbol": START_CASH_PER_SYMBOL,
                   "strategies": {s: STRATEGY[s]["label"] for s in SYMBOLS}},
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

        kl = get_klines(sym)
        closes = [x[2] for x in kl]
        price = closes[-1]
        should_buy, should_sell, lvl_a, lvl_b, trend = compute_signal(sym, closes)

        # --- Empieza en USDT y COMPRA en la senal de la estrategia ---
        if s["position"] == 0.0 and s["cash"] > 0 and should_buy:
            qty = (s["cash"] * (1 - FEE)) / price
            st["trades"].insert(0, {
                "time": now_iso, "symbol": sym, "side": "BUY",
                "price": round(price, 2), "qty": round(qty, 8),
                "value": round(s["cash"], 2)})
            s["position"] = qty
            s["avg_entry"] = price
            s["cash"] = 0.0
        # --- VENDE en la senal de salida (protege el capital) ---
        elif s["position"] > 0.0 and should_sell:
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
        s["sma_fast"] = lvl_a
        s["sma_slow"] = lvl_b
        s["trend"] = trend
        s["signal"] = "LONG" if s["position"] > 0.0 else "FLAT"
        s["strat"] = STRATEGY[sym]["label"]
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
        print("  {}: {} price={:.2f} ref={}/{} trend={} signal={} equity={:.2f}".format(
            sym, s["strat"], s["price"], s["sma_fast"], s["sma_slow"], s["trend"],
            s["signal"], s["equity"]))


if __name__ == "__main__":
    run()
