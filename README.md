# 📈 Binance Paper Trader (simulación) + Dashboard

Bot de **paper trading** (SIMULACIÓN) sobre **BTC/USDT** y **ETH/USDT** que corre solo
en **GitHub Actions** (no depende de tu PC) y publica un **dashboard responsive** por
**GitHub Pages** para verlo desde el teléfono con una URL fija.

> ⚠️ **Esto es 100% simulación.** No usa API keys, no se conecta a tu cuenta de Binance
> y **no ejecuta órdenes reales**. Solo lee precios públicos y simula operaciones con
> capital ficticio.

## ¿Cómo funciona?

1. **`paper_trader.py`** corre una vez por invocación: lee precios públicos de Binance
   (`data-api.binance.vision`, sin API key), aplica una estrategia y actualiza el estado.
2. **GitHub Actions** (`.github/workflows/trade.yml`) lo ejecuta con un **cron cada 15 min**
   y commitea los resultados a `docs/data/state.json` y `docs/data/history.csv`.
3. **`docs/index.html`** es el dashboard: lee ese JSON y muestra precio, PnL, operaciones
   y la curva de capital. Se sirve por **GitHub Pages** (carpeta `/docs`).

## Estrategia (de ejemplo, fácil de cambiar)

Cruce de medias móviles simples (SMA) sobre velas de 15m:
- SMA rápida (7) por encima de la lenta (25) → **LONG** (compra simulada).
- SMA rápida por debajo → **FLAT** (vende y se queda en efectivo).

Long-only, un sub-portafolio virtual de **5.000 USDT por símbolo** (10.000 en total),
con una comisión simulada de 0,1% por operación. Cambia los parámetros arriba de
`paper_trader.py` (`FAST`, `SLOW`, `INTERVAL`, `START_CASH_PER_SYMBOL`, `FEE`).

## Estructura

```
paper_trader.py            # lógica de simulación (corre 1 vez por cron)
docs/index.html            # dashboard (GitHub Pages)
docs/data/state.json       # estado actual (lo escribe la Action)
docs/data/history.csv      # histórico en CSV
.github/workflows/trade.yml# cron cada 15 min
```

## Ejecutar localmente

```bash
python paper_trader.py          # genera/actualiza docs/data/state.json
# abre docs/index.html en el navegador (o sirve la carpeta docs con un server local)
```

## Notas sobre GitHub Actions

- Los cron son *best-effort*: pueden retrasarse unos minutos si hay mucha carga.
- GitHub **deshabilita los cron tras ~60 días sin actividad** en el repo; basta con
  hacer un commit o re-activarlo desde la pestaña *Actions* para reanudarlo.
- El mínimo intervalo real de cron es 5 min; aquí usamos 15.

---

## 🚨 Si algún día quieres pasar a modo REAL (dinero de verdad)

Actualmente **NO** hay claves ni órdenes reales. Antes de conectar dinero real, hay que
hacerlo con cuidado. Recordatorio de seguridad para ese momento:

- Crea una **API key de Binance con permisos LIMITADOS**: solo *Spot Trading*,
  **sin permiso de retiros** (withdrawals) nunca.
- Restringe la key por **lista de IPs permitidas**.
- **Nunca** subas las keys al repo: úsalas como **GitHub Secrets** / variables de entorno.
- Empieza con montos mínimos y valida el comportamiento antes de escalar.
- Ten claro el riesgo: el trading automatizado **puede perder dinero**; una estrategia
  que funciona en simulación no garantiza resultados reales (comisiones, slippage,
  latencia, fallos de red y del exchange).

Cuando me pidas pasar a real, te lo recordaré y repasaremos estos puntos **antes** de continuar.
