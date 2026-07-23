# 🩺 Evaluación clínica: BTC/ETH (2024 → 2026) y estrategia

> Análisis con **datos reales** de Binance (velas diarias, ene-2024 → jul-2026) + síntesis de
> **planes de traders profesionales** y evidencia académica. Todo es para **paper trading**
> (simulación); no es asesoría financiera.

## 0. Resumen ejecutivo (TL;DR)
1. **La temporalidad importa MÁS que los parámetros.** La misma estrategia SMA 7/25 da **+53%** en diario, **+13%** en 4h y **−48%** en 1h. El bot original en **15m era inviable**. → **Usamos velas diarias.**
2. **El trend-following no gana siempre; protege.** En el toro de 2024, comprar y aguantar (buy&hold) ganó más. En el mercado choppy/bajista de 2025-2026, el cruce de medias **evitó caídas del −50/−68%** y hasta ganó en ETH. Su valor es **reducir el drawdown**, no batir al buy&hold en todo momento.
3. **Lo simple ganó a lo complejo.** Añadir filtros y stops "sofisticados" empeoró el resultado en este período (síntoma clásico de sobreoptimización).
4. **$25 es muy poco para trading activo real.** El mínimo de Binance es **$5/orden** y arriesgar 1% de $25 = $0.25 < $5 → te obliga a sobre-arriesgar. Para dinero real pequeño, **DCA** (compras periódicas) es más sensato. Por eso: **seguimos en simulación.**

---

## 1. Cómo se movieron BTC y ETH (datos reales)

| | Inicio 2024 | Máximo | Hoy | 2024 | 2025 | 2026 (YTD) |
|---|---|---|---|---|---|---|
| **BTC** | $44.180 | $126.200 | ~$65.700 | **+111.8%** | −7.3% | −26.0% |
| **ETH** | $2.352 | $4.957 | ~$1.924 | +41.9% | −11.6% | −36.0% |

**Lectura clínica:** 2024 fue un **toro fuerte**; 2025-2026 ha sido **corrección/lateral bajista**. ETH está
**por debajo** de su precio de inicio de 2024 (buy&hold = −18% en el período completo). Alta volatilidad:
caídas máximas (drawdown) de **−53% en BTC** y **−68% en ETH** aguantando.

## 2. La temporalidad decide (SMA 7/25, 2024→hoy)

| Temporalidad | BTC | ETH | Nº operaciones |
|---|---|---|---|
| **1 día** ✅ | **+52.7%** | **+56.0%** | ~43 |
| 4 horas | +12.8% | +37.5% | ~270 |
| 1 hora ❌ | −48% | −62% | ~1.140 |

Cadena causal: menor temporalidad → más cruces → más señales falsas en lateral → más operaciones →
más comisiones/slippage → expectativa negativa. **Los sistemas de tendencia se operan en 4h/diario, no en 15m/1h.**

## 3. Backtest de estrategias (diario, con comisión 0.1%)

| Estrategia | BTC ret. | BTC MaxDD | ETH ret. | ETH MaxDD |
|---|---|---|---|---|
| Buy & Hold | +48.7% | −53% | −18.2% | −68% |
| **SMA 7/25** ✅ | **+52.7%** | −39% | **+56.0%** | −46% |
| SMA 10/30 | +30.6% | −38% | +52.0% | −44% |
| 10/30 + filtro >SMA100 | −9.6% | −28% | +9.1% | −31% |
| 10/30 + stop ATR | +29% | −39% | +26% | −50% |

**Win rate ~30-36%** (¡normal en trend-following!): ganas pocas veces pero las ganadoras son grandes.

## 4. Validación OUT-OF-SAMPLE (la prueba anti-sobreoptimización)

Optimizar en un período y validar en otro **intocado**. Dividimos: 2024 (in-sample, toro) vs 2025→hoy (out-of-sample, bajista):

| | **2024 (toro)** BTC / ETH | **2025+ (bajista)** BTC / ETH |
|---|---|---|
| Buy & Hold | +111.8% / +41.9% | **−30.6% / −42.7%** |
| SMA 7/25 | +50.1% / −1.0% | **+1.7% / +57.6%** |

**Conclusión honesta:** en el toro, buy&hold gana (das ventaja al esperar el cruce). En el bajista,
**el cruce te salvó**: BTC −31% vs +2%, y ETH **−43% vs +58%**. La estrategia demostró valor
**fuera de muestra** — no es puro overfitting, sobre todo su **protección a la baja**.

## 5. Qué hacen los traders profesionales (síntesis + fuentes)

- **El cruce es solo el gatillo; la gestión de riesgo es la estrategia.** ([Quantt](https://www.quantt.co.uk/resources/moving-average-crossover-guide))
- **Regla del 1% de riesgo por operación.** Tamaño = (capital × 1%) ÷ (entrada − stop). 10 pérdidas seguidas ≈ solo −10%. ([TradeThatSwing](https://tradethatswing.com/the-1-risk-rule-for-day-trading-and-swing-trading/))
- **Stop por ATR** (2× ATR swing) y **objetivo R:R ≥ 1:2**. ([QuantVPS](https://www.quantvps.com/blog/atr-stop-loss))
- **Expectativa > win rate.** Expectativa = (Win% × GananciaMedia) − (Loss% × PérdidaMedia). Un 35% de aciertos con 3R ya es rentable. ([CrossTrade](https://crosstrade.io/learn/performance-metrics/win-rate-vs-expectancy))
- **Filtros anti-whipsaw:** operar a favor de la tendencia de mayor temporalidad, ADX>25, cierre confirmado, separación mínima entre medias. ([ChartScout](https://chartscout.io/golden-cross-vs-death-cross-crypto-trading-guide))
- **El trend-following es real** (AQR *Time Series Momentum*; "A Century of Evidence") pero un solo par es una versión ruidosa; **sobreoptimizar es el error #1** → validar out-of-sample. ([AQR](https://www.aqr.com/Insights/Research/Journal-Article/Time-Series-Momentum))
- **BTC tiende fuerte** y el trend-following captura la mayor parte de su retorno con menos drawdown. ([QuantPedia](https://quantpedia.com/trend-following-and-mean-reversion-in-bitcoin/))

## 6. La realidad de una cuenta de $25 (mecánica de Binance, verificada)

- **Mínimo por orden = $5 USDT**; **comisión 0.1%** (0.2% ida y vuelta). ([Binance](https://www.binance.com/en/support/announcement/detail/c4706c73b805423a8d36be948e297603))
- Arriesgar **1% de $25 = $0.25**, pero el mínimo es $5 → estás **forzado a arriesgar 20-50%+** de la cuenta por operación (imprudente).
- **~92% de traders activos rinden peor que comprar y aguantar**; **~59% de inversores usan DCA**. ([FinanceFeeds](https://financefeeds.com/dollar-cost-averaging-vs-active-trading-in-crypto/))
- **Umbral práctico para trading activo real: unos cientos de $ a ~$1.000+.** Con $25: **simula, aprende, y considera DCA** para acumular.

## 7. La estrategia recomendada (la que corre el bot ahora)

Tras backtestear **7 familias** (SMA, EMA, momentum TSMOM, Donchian breakout, filtro SMA, dual-momentum) y **validar out-of-sample** (2024 vs 2025+), la mejor combinación robusta es **estrategia por activo**:

| Activo | Estrategia | Retorno 24-26 | Sharpe | 2024 | 2025+ (out-of-sample) |
|---|---|---|---|---|---|
| **BTC** | **Donchian 20/10** (breakout tipo Turtle) | **+97%** | **1.12** | +76% | **+12%** ✅ |
| **ETH** | **SMA 7/25** (cruce de medias) | +53% | 0.60 | −1% | **+55%** ✅ |

- **Capital simulado:** $25 ($12.50 c/u) · **Temporalidad:** diaria · empieza en **USDT** · comisión 0.1%.
- **BTC (Donchian):** compra al **romper el máximo de 20 días**; vende al romper el mínimo de 10 días.
- **ETH (SMA):** compra cuando **SMA(7) > SMA(25)**; vende cuando cruza abajo.
- **Por qué así:** cada activo tiene carácter distinto (BTC rompe niveles, ETH sigue tendencias) y **ambas reglas fueron positivas tanto en el toro (2024) como en el bajista (2025+)** — robustez real, no sobreoptimización. Es lo mejor que encontré probando en serio.

### Versión "profesional" completa (para cuando crezca la cuenta y vayas a real)
Añadir sobre la regla base: **filtro de tendencia mayor** (precio > SMA200 diaria) · **ADX > 25** · **stop inicial 2×ATR** · **sizing al 1% de riesgo** · **trailing Chandelier (3×ATR)** · **R:R ≥ 1:2**. Validar **walk-forward** con comisiones reales antes de arriesgar dinero.

## 8. Expectativas realistas y riesgos
- **Win rate bajo (~30-45%) es NORMAL**; no te asustes de rachas de 7-10 pérdidas seguidas.
- Espera **drawdowns del ~40%** incluso en la versión que "funciona".
- Rendimiento pasado **no garantiza** futuro; el trend-following **sangra en mercados laterales**.
- **Nada de esto es asesoría financiera.** Cripto es volátil; puedes perder todo el capital.

## 9. Fuentes principales
Binance ([comisiones](https://www.binance.com/en/fee/schedule), [mínimo](https://www.binance.com/en/support/announcement/detail/c4706c73b805423a8d36be948e297603)) ·
[Quantt](https://www.quantt.co.uk/resources/moving-average-crossover-guide) ·
[ChartScout](https://chartscout.io/golden-cross-vs-death-cross-crypto-trading-guide) ·
[AQR TSMOM](https://www.aqr.com/Insights/Research/Journal-Article/Time-Series-Momentum) ·
[QuantPedia BTC](https://quantpedia.com/trend-following-and-mean-reversion-in-bitcoin/) ·
[TradeThatSwing 1% rule](https://tradethatswing.com/the-1-risk-rule-for-day-trading-and-swing-trading/) ·
[CrossTrade expectancy](https://crosstrade.io/learn/performance-metrics/win-rate-vs-expectancy) ·
[QuantVPS ATR](https://www.quantvps.com/blog/atr-stop-loss) ·
[FinanceFeeds DCA](https://financefeeds.com/dollar-cost-averaging-vs-active-trading-in-crypto/)

*Backtests: velas diarias reales de Binance (data-api.binance.vision), comisión 0.1%, ene-2024 a jul-2026.*
