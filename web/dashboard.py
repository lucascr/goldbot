import json


def render_dashboard(symbols, symbol_metadata):
    symbols_json = json.dumps(symbols)
    symbol_metadata_json = json.dumps(symbol_metadata)
    html = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Goldbot Pulse</title>
    <style>
        :root {
            --paper: #f7f1e4;
            --paper-deep: #ede2cf;
            --ink: #1c1b18;
            --muted: #6c665b;
            --line: rgba(68, 54, 36, 0.14);
            --gold: #c68a2d;
            --gold-deep: #8b5e1c;
            --teal: #0d7a72;
            --teal-soft: rgba(13, 122, 114, 0.14);
            --red: #a64b3c;
            --red-soft: rgba(166, 75, 60, 0.12);
            --card: rgba(255, 251, 245, 0.78);
            --card-strong: rgba(255, 252, 248, 0.96);
            --shadow: 0 18px 55px rgba(84, 58, 21, 0.14);
            --display: Georgia, "Times New Roman", serif;
            --body: "Trebuchet MS", "Segoe UI", sans-serif;
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            color: var(--ink);
            font-family: var(--body);
            background:
                radial-gradient(circle at top left, rgba(198, 138, 45, 0.24), transparent 34%),
                radial-gradient(circle at top right, rgba(13, 122, 114, 0.16), transparent 30%),
                linear-gradient(135deg, #f9f4eb 0%, #f1e7d7 46%, #e8dfd1 100%);
        }

        body::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background-image:
                linear-gradient(rgba(255,255,255,0.16) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.12) 1px, transparent 1px);
            background-size: 28px 28px;
            mask-image: linear-gradient(to bottom, rgba(0,0,0,0.4), rgba(0,0,0,0.08));
        }

        .shell {
            max-width: 1320px;
            margin: 0 auto;
            padding: 24px 18px 40px;
        }

        .hero {
            position: relative;
            overflow: hidden;
            padding: 28px;
            border-radius: 30px;
            border: 1px solid var(--line);
            background: linear-gradient(145deg, rgba(255, 252, 247, 0.88), rgba(245, 236, 219, 0.9));
            box-shadow: var(--shadow);
        }

        .hero::after {
            content: "";
            position: absolute;
            width: 260px;
            height: 260px;
            right: -50px;
            top: -110px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(198, 138, 45, 0.30), rgba(198, 138, 45, 0));
        }

        .eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 7px 12px;
            border-radius: 999px;
            background: rgba(198, 138, 45, 0.12);
            color: var(--gold-deep);
            font-size: 12px;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }

        h1 {
            margin: 14px 0 10px;
            max-width: 9ch;
            font-family: var(--display);
            font-size: clamp(2.8rem, 7vw, 5.7rem);
            line-height: 0.94;
            letter-spacing: -0.04em;
        }

        .hero-copy {
            max-width: 58ch;
            margin: 0;
            color: var(--muted);
            line-height: 1.65;
            font-size: 1.02rem;
        }

        .hero-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 14px;
            margin-top: 24px;
        }

        .hero-stat {
            padding: 14px 16px;
            border-radius: 18px;
            border: 1px solid var(--line);
            background: rgba(255, 251, 246, 0.78);
            backdrop-filter: blur(8px);
        }

        .hero-stat strong {
            display: block;
            font-size: 1.45rem;
        }

        .hero-stat span {
            color: var(--muted);
            font-size: 0.9rem;
        }

        .status-line {
            margin-top: 14px;
            color: var(--muted);
            font-size: 0.92rem;
        }

        .layout {
            display: grid;
            grid-template-columns: 1.05fr 1.3fr;
            gap: 20px;
            margin-top: 22px;
        }

        .panel {
            padding: 20px;
            border-radius: 24px;
            border: 1px solid var(--line);
            background: var(--card);
            box-shadow: var(--shadow);
            backdrop-filter: blur(10px);
        }

        .panel h2 {
            margin: 0;
            font-size: 2rem;
            font-family: var(--display);
        }

        .panel-copy {
            margin: 8px 0 18px;
            color: var(--muted);
            line-height: 1.55;
        }

        .board {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(165px, 1fr));
            gap: 14px;
        }

        .card {
            padding: 16px;
            border-radius: 18px;
            border: 1px solid var(--line);
            background: var(--card-strong);
            cursor: pointer;
            transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
        }

        .card:hover,
        .card.active {
            transform: translateY(-3px);
            border-color: rgba(198, 138, 45, 0.44);
            box-shadow: 0 12px 28px rgba(84, 58, 21, 0.12);
        }

        .card .symbol {
            font-weight: 800;
            font-size: 1.02rem;
            letter-spacing: 0.04em;
        }

        .card .label {
            margin-top: 4px;
            color: var(--muted);
            font-size: 0.78rem;
            line-height: 1.35;
            min-height: 2.1em;
        }

        .card .price {
            margin-top: 10px;
            font-family: var(--display);
            font-size: 1.85rem;
        }

        .card .sub {
            margin-top: 8px;
            color: var(--muted);
            font-size: 0.88rem;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            margin-top: 12px;
            padding: 6px 10px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .badge.live {
            background: var(--teal-soft);
            color: var(--teal);
        }

        .badge.calm {
            background: rgba(108, 102, 91, 0.12);
            color: var(--muted);
        }

        .detail-head {
            display: flex;
            justify-content: space-between;
            gap: 16px;
            align-items: flex-start;
        }

        .detail-price {
            margin: 10px 0 0;
            font-family: var(--display);
            font-size: clamp(2.4rem, 5vw, 4.4rem);
            line-height: 0.94;
        }

        .detail-copy {
            margin: 8px 0 0;
            color: var(--muted);
        }

        .signal-chip {
            padding: 8px 12px;
            border-radius: 999px;
            background: var(--teal-soft);
            color: var(--teal);
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .signal-chip.wait {
            background: rgba(108, 102, 91, 0.12);
            color: var(--muted);
        }

        .detail-grid {
            display: grid;
            grid-template-columns: 1.15fr 0.85fr;
            gap: 16px;
            margin-top: 18px;
        }

        .stack {
            display: grid;
            gap: 14px;
        }

        .metric-row {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 12px;
        }

        .metric {
            padding: 14px;
            border-radius: 16px;
            border: 1px solid var(--line);
            background: rgba(255,255,255,0.48);
        }

        .metric span {
            display: block;
            color: var(--muted);
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .metric strong {
            display: block;
            margin-top: 6px;
            font-size: 1.18rem;
        }

        .chart-wrap,
        .signal-wrap,
        .flow-wrap {
            padding: 14px;
            border-radius: 18px;
            border: 1px solid var(--line);
            background: rgba(255, 252, 248, 0.72);
        }

        .chart-wrap h3,
        .signal-wrap h3,
        .flow-wrap h3 {
            margin: 0 0 10px;
            font-size: 0.95rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--muted);
        }

        canvas {
            display: block;
            width: 100%;
            height: 280px;
        }

        .timeframes {
            display: grid;
            gap: 10px;
        }

        .tf-row {
            display: grid;
            grid-template-columns: 80px 1fr auto;
            gap: 10px;
            align-items: center;
        }

        .tf-tag {
            font-weight: 800;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }

        .tf-bar {
            position: relative;
            height: 12px;
            border-radius: 999px;
            overflow: hidden;
            background: rgba(108, 102, 91, 0.14);
        }

        .tf-fill {
            position: absolute;
            inset: 0 auto 0 0;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--red), var(--gold), var(--teal));
            transform-origin: left center;
        }

        .tf-value {
            min-width: 62px;
            text-align: right;
            font-weight: 700;
        }

        .reason-list,
        .pulse-list {
            display: grid;
            gap: 10px;
        }

        .telegram-form {
            display: grid;
            gap: 10px;
        }

        .telegram-form textarea {
            width: 100%;
            min-height: 110px;
            resize: vertical;
            padding: 12px 14px;
            border-radius: 14px;
            border: 1px solid var(--line);
            background: rgba(255,255,255,0.74);
            color: var(--ink);
            font: inherit;
        }

        .telegram-actions {
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }

        .telegram-button {
            appearance: none;
            border: 0;
            border-radius: 999px;
            padding: 11px 16px;
            background: linear-gradient(135deg, var(--gold), var(--gold-deep));
            color: #fff9f1;
            font: inherit;
            font-weight: 700;
            letter-spacing: 0.04em;
            cursor: pointer;
        }

        .telegram-button:disabled {
            opacity: 0.6;
            cursor: progress;
        }

        .telegram-status {
            color: var(--muted);
            font-size: 0.9rem;
        }

        .reason,
        .pulse {
            padding: 12px 14px;
            border-radius: 14px;
            border: 1px solid var(--line);
            background: rgba(255,255,255,0.5);
        }

        .reason strong,
        .pulse strong {
            display: block;
            font-size: 0.92rem;
        }

        .reason span,
        .pulse span {
            display: block;
            margin-top: 5px;
            color: var(--muted);
            font-size: 0.88rem;
            line-height: 1.5;
        }

        .pulse.live {
            border-color: rgba(13, 122, 114, 0.22);
            background: rgba(13, 122, 114, 0.08);
        }

        .pulse.alert {
            border-color: rgba(166, 75, 60, 0.22);
            background: rgba(166, 75, 60, 0.08);
        }

        .footer-note {
            margin-top: 12px;
            color: var(--muted);
            font-size: 0.88rem;
        }

        .loading {
            opacity: 0.6;
        }

        @media (max-width: 1080px) {
            .layout,
            .detail-grid {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 720px) {
            .metric-row {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }
    </style>
</head>
<body>
    <main class="shell">
        <section class="hero">
            <div class="eyebrow">Live Market Pulse</div>
            <h1>Goldbot Dashboard</h1>
            <p class="hero-copy">
                Track the whole watchlist, inspect rolling price action, and compare buy pressure across
                multiple timeframes. The board updates through a live WebSocket stream, so the screen
                stays fresh without manual reloads.
            </p>
            <div class="hero-stats">
                <div class="hero-stat">
                    <strong id="stat-symbols">0</strong>
                    <span>Symbols watched</span>
                </div>
                <div class="hero-stat">
                    <strong id="stat-buy">0</strong>
                    <span>Active buy windows</span>
                </div>
                <div class="hero-stat">
                    <strong id="stat-focus">-</strong>
                    <span>Focus ticker</span>
                </div>
                <div class="hero-stat">
                    <strong id="stat-socket">Connecting</strong>
                    <span>Live stream</span>
                </div>
            </div>
            <div class="status-line" id="status-line">Preparing first market snapshot.</div>
        </section>

        <section class="layout">
            <section class="panel">
                <h2>Signal Board</h2>
                <p class="panel-copy">A compact board of the tracked universe with signal state, RSI, and the active watchlist pulse.</p>
                <div id="board" class="board loading"></div>
            </section>

            <section class="panel">
                <div class="detail-head">
                    <div>
                        <div class="eyebrow" id="detail-symbol">Loading</div>
                        <h2 id="detail-title">Building signal stack</h2>
                        <p class="detail-copy" id="detail-copy">Waiting for the first live market frame.</p>
                    </div>
                    <div class="signal-chip wait" id="detail-chip">Wait</div>
                </div>

                <div class="detail-price" id="detail-price">--</div>

                <div class="detail-grid">
                    <div class="stack">
                        <div class="metric-row">
                            <div class="metric">
                                <span>MA20</span>
                                <strong id="metric-ma20">--</strong>
                            </div>
                            <div class="metric">
                                <span>MA50</span>
                                <strong id="metric-ma50">--</strong>
                            </div>
                            <div class="metric">
                                <span>RSI</span>
                                <strong id="metric-rsi">--</strong>
                            </div>
                            <div class="metric">
                                <span>Rows</span>
                                <strong id="metric-rows">--</strong>
                            </div>
                        </div>

                        <div class="chart-wrap">
                            <h3>Price + Moving Averages</h3>
                            <canvas id="price-chart" width="820" height="280"></canvas>
                        </div>

                        <div class="flow-wrap">
                            <h3>Signal Drivers</h3>
                            <div id="reason-list" class="reason-list"></div>
                        </div>
                    </div>

                    <div class="stack">
                        <div class="signal-wrap">
                            <h3>Multi-Timeframe Matrix</h3>
                            <div id="timeframes" class="timeframes"></div>
                        </div>

                        <div class="signal-wrap">
                            <h3>Live Feed</h3>
                            <div id="pulse-list" class="pulse-list"></div>
                        </div>

                        <div class="signal-wrap">
                            <h3>Telegram Test</h3>
                            <div class="telegram-form">
                                <textarea id="telegram-message">Goldbot dashboard test ping.</textarea>
                                <div class="telegram-actions">
                                    <button id="telegram-send" class="telegram-button" type="button">Send test message</button>
                                    <div id="telegram-status" class="telegram-status">Ready to send a Telegram test.</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="footer-note">Uses the existing Goldbot storage, indicators, and signal rules with a live streaming layer on top.</div>
            </section>
        </section>
    </main>

    <script>
        const trackedSymbols = __SYMBOLS_JSON__;
        const symbolMeta = __SYMBOL_META_JSON__;
        const state = {
            activeSymbol: trackedSymbols[0] || null,
            overview: [],
            detail: null,
            socket: null,
            pulse: []
        };

        const els = {
            board: document.getElementById('board'),
            statusLine: document.getElementById('status-line'),
            statSymbols: document.getElementById('stat-symbols'),
            statBuy: document.getElementById('stat-buy'),
            statFocus: document.getElementById('stat-focus'),
            statSocket: document.getElementById('stat-socket'),
            detailSymbol: document.getElementById('detail-symbol'),
            detailTitle: document.getElementById('detail-title'),
            detailCopy: document.getElementById('detail-copy'),
            detailChip: document.getElementById('detail-chip'),
            detailPrice: document.getElementById('detail-price'),
            metricMa20: document.getElementById('metric-ma20'),
            metricMa50: document.getElementById('metric-ma50'),
            metricRsi: document.getElementById('metric-rsi'),
            metricRows: document.getElementById('metric-rows'),
            timeframes: document.getElementById('timeframes'),
            reasonList: document.getElementById('reason-list'),
            pulseList: document.getElementById('pulse-list'),
            priceChart: document.getElementById('price-chart'),
            telegramMessage: document.getElementById('telegram-message'),
            telegramSend: document.getElementById('telegram-send'),
            telegramStatus: document.getElementById('telegram-status')
        };

        function formatPrice(value) {
            if (value === null || value === undefined) return '--';
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
                maximumFractionDigits: value >= 100 ? 2 : 4
            }).format(value);
        }

        function formatNumber(value) {
            if (value === null || value === undefined || Number.isNaN(Number(value))) return '--';
            return Number(value).toFixed(2);
        }

        function formatPct(value) {
            if (value === null || value === undefined || Number.isNaN(Number(value))) return '--';
            return `${(Number(value) * 100).toFixed(2)}%`;
        }

        async function readJsonResponse(response, fallbackMessage) {
            const rawText = await response.text();
            let payload = null;

            if (rawText) {
                try {
                    payload = JSON.parse(rawText);
                } catch (error) {
                    if (!response.ok) {
                        throw new Error(rawText.trim() || fallbackMessage);
                    }
                    throw new Error(fallbackMessage);
                }
            }

            if (!response.ok) {
                const detail = payload && typeof payload === 'object'
                    ? (payload.detail || payload.message || rawText)
                    : rawText;
                throw new Error(detail || fallbackMessage);
            }

            return payload;
        }

        function pushPulse(kind, title, body) {
            state.pulse = [{ kind, title, body }, ...state.pulse].slice(0, 5);
            renderPulse();
        }

        function renderPulse() {
            els.pulseList.innerHTML = state.pulse.map(item => `
                <article class="pulse ${item.kind}">
                    <strong>${item.title}</strong>
                    <span>${item.body}</span>
                </article>
            `).join('');
        }

        function renderBoard() {
            els.statSymbols.textContent = String(state.overview.length);
            els.statBuy.textContent = String(state.overview.filter(item => item.signal_summary === 'BUY').length);
            els.statFocus.textContent = state.activeSymbol || '-';

            els.board.innerHTML = state.overview.map(item => {
                const active = item.symbol === state.activeSymbol ? 'active' : '';
                const badge = item.signal_summary === 'BUY'
                    ? `<div class="badge live">${item.active_timeframes.length} active windows</div>`
                    : `<div class="badge calm">No trigger</div>`;
                return `
                    <article class="card ${active}" data-symbol="${item.symbol}">
                        <div class="symbol">${item.symbol}</div>
                        <div class="label">${item.label || symbolMeta[item.symbol]?.label || item.name || item.symbol}</div>
                        <div class="price">${formatPrice(item.price)}</div>
                        <div class="sub">RSI ${formatNumber(item.rsi)} · 1h ${formatPct(item.change_1h)}</div>
                        ${badge}
                    </article>
                `;
            }).join('');

            els.board.classList.remove('loading');
            for (const card of els.board.querySelectorAll('.card')) {
                card.addEventListener('click', () => {
                    state.activeSymbol = card.dataset.symbol;
                    renderBoard();
                    if (state.socket && state.socket.readyState === WebSocket.OPEN) {
                        state.socket.send(JSON.stringify({ type: 'focus', symbol: state.activeSymbol }));
                    } else {
                        void fetchDetail(state.activeSymbol);
                    }
                });
            }
        }

        function drawChart(detail) {
            const canvas = els.priceChart;
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            const history = detail?.history || [];
            if (history.length < 2) {
                ctx.fillStyle = '#6c665b';
                ctx.font = '16px Trebuchet MS';
                ctx.fillText('Not enough history to draw chart yet.', 18, 30);
                return;
            }

            const series = history.slice(-48);
            const prices = series.map(point => Number(point.price));
            const ma20 = series.map(point => point.ma20 == null ? null : Number(point.ma20));
            const ma50 = series.map(point => point.ma50 == null ? null : Number(point.ma50));
            const allValues = [...prices, ...ma20.filter(v => v != null), ...ma50.filter(v => v != null)];
            const min = Math.min(...allValues);
            const max = Math.max(...allValues);
            const range = max - min || 1;
            const pad = { top: 18, right: 18, bottom: 24, left: 12 };
            const chartW = canvas.width - pad.left - pad.right;
            const chartH = canvas.height - pad.top - pad.bottom;

            function pointX(index) {
                return pad.left + (index / Math.max(series.length - 1, 1)) * chartW;
            }

            function pointY(value) {
                return pad.top + chartH - ((value - min) / range) * chartH;
            }

            ctx.strokeStyle = 'rgba(108, 102, 91, 0.18)';
            ctx.lineWidth = 1;
            for (let i = 0; i < 4; i += 1) {
                const y = pad.top + (chartH / 3) * i;
                ctx.beginPath();
                ctx.moveTo(pad.left, y);
                ctx.lineTo(canvas.width - pad.right, y);
                ctx.stroke();
            }

            ctx.beginPath();
            prices.forEach((value, index) => {
                const x = pointX(index);
                const y = pointY(value);
                if (index === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            ctx.lineTo(pointX(prices.length - 1), canvas.height - pad.bottom);
            ctx.lineTo(pointX(0), canvas.height - pad.bottom);
            ctx.closePath();
            ctx.fillStyle = 'rgba(198, 138, 45, 0.14)';
            ctx.fill();

            function drawLine(values, color, width) {
                ctx.beginPath();
                let started = false;
                values.forEach((value, index) => {
                    if (value == null) return;
                    const x = pointX(index);
                    const y = pointY(value);
                    if (!started) {
                        ctx.moveTo(x, y);
                        started = true;
                    } else {
                        ctx.lineTo(x, y);
                    }
                });
                ctx.strokeStyle = color;
                ctx.lineWidth = width;
                ctx.lineCap = 'round';
                ctx.lineJoin = 'round';
                ctx.stroke();
            }

            drawLine(prices, '#8b5e1c', 3.2);
            drawLine(ma20, '#0d7a72', 2.2);
            drawLine(ma50, '#a64b3c', 2);
        }

        function renderTimeframes(detail) {
            const rows = detail?.signals?.timeframes || [];
            els.timeframes.innerHTML = rows.map(item => {
                const magnitude = Math.min(Math.abs(Number(item.change || 0)) / 0.05, 1);
                return `
                    <div class="tf-row">
                        <div class="tf-tag">${item.timeframe}</div>
                        <div class="tf-bar">
                            <div class="tf-fill" style="width:${Math.max(magnitude * 100, 4)}%"></div>
                        </div>
                        <div class="tf-value">${formatPct(item.change)}</div>
                    </div>
                `;
            }).join('');
        }

        function renderReasons(detail) {
            const signalReasons = detail?.signals?.timeframes || [];
            const active = signalReasons.filter(item => item.reasons && item.reasons.length);
            const cards = active.length ? active : [{ timeframe: 'No edge', reasons: ['WAIT'], confidence: 0 }];
            els.reasonList.innerHTML = cards.map(item => `
                <article class="reason">
                    <strong>${item.timeframe} · ${item.signal || 'WAIT'} · confidence ${item.confidence}</strong>
                    <span>${item.reasons.join(', ')}</span>
                </article>
            `).join('');
        }

        function renderDetail(detail) {
            state.detail = detail;
            const indicators = detail.indicators || {};
            const summary = detail.signals?.summary || 'WAIT';
            const activeTimeframes = detail.signals?.active_timeframes || [];

            els.detailSymbol.textContent = detail.label || detail.symbol;
            els.detailTitle.textContent = detail.name || detail.symbol;
            els.detailCopy.textContent = summary === 'BUY'
                ? `${detail.symbol} is active across ${activeTimeframes.length} timeframe${activeTimeframes.length === 1 ? '' : 's'}.`
                : `${detail.symbol} has not reached the current buy threshold across the timeframe stack.`;
            els.detailChip.textContent = summary;
            els.detailChip.className = `signal-chip ${summary === 'BUY' ? '' : 'wait'}`.trim();
            els.detailPrice.textContent = formatPrice(detail.price);
            els.metricMa20.textContent = formatPrice(indicators.ma20);
            els.metricMa50.textContent = formatPrice(indicators.ma50);
            els.metricRsi.textContent = formatNumber(indicators.rsi);
            els.metricRows.textContent = String((detail.history || []).length);
            if (!els.telegramMessage.value.trim() || els.telegramMessage.value.includes('dashboard test ping')) {
                els.telegramMessage.value = `Goldbot dashboard test for ${detail.symbol} at ${new Date().toLocaleTimeString()}.`;
            }

            drawChart(detail);
            renderTimeframes(detail);
            renderReasons(detail);
        }

        async function sendTelegramTest() {
            const message = els.telegramMessage.value.trim();
            els.telegramSend.disabled = true;
            els.telegramStatus.textContent = 'Sending Telegram test...';

            try {
                const response = await fetch('/telegram/test', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });
                const payload = await readJsonResponse(response, 'Telegram test failed.');
                if (!payload.ok) {
                    throw new Error(payload.detail || 'Telegram test failed.');
                }

                els.telegramStatus.textContent = `Sent: ${payload.message}`;
                pushPulse('live', 'Telegram test sent', payload.message);
            } catch (error) {
                const messageText = error instanceof Error ? error.message : 'Telegram test failed.';
                els.telegramStatus.textContent = messageText;
                pushPulse('alert', 'Telegram test error', messageText);
            } finally {
                els.telegramSend.disabled = false;
            }
        }

        async function fetchDetail(symbol) {
            const response = await fetch(`/snapshot/${encodeURIComponent(symbol)}`);
            const detail = await readJsonResponse(response, 'Snapshot request failed.');
            renderDetail(detail);
        }

        function applyFrame(frame) {
            if (Array.isArray(frame.overview)) {
                state.overview = frame.overview;
                renderBoard();
            }
            if (frame.detail) {
                renderDetail(frame.detail);
            }
            if (frame.generated_at) {
                els.statusLine.textContent = `Last update ${new Date(frame.generated_at).toLocaleTimeString()}`;
            }
        }

        function connectSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
            const socket = new WebSocket(`${protocol}://${window.location.host}/ws/market`);
            state.socket = socket;

            socket.addEventListener('open', () => {
                els.statSocket.textContent = 'Live';
                pushPulse('live', 'Socket connected', 'Streaming fresh market snapshots.');
                socket.send(JSON.stringify({ type: 'focus', symbol: state.activeSymbol }));
            });

            socket.addEventListener('message', event => {
                const frame = JSON.parse(event.data);
                applyFrame(frame);
                const summary = frame.detail?.signals?.summary || 'WAIT';
                const title = `${frame.detail?.symbol || state.activeSymbol} ${summary}`;
                const body = summary === 'BUY'
                    ? `Active windows: ${(frame.detail?.signals?.active_timeframes || []).join(', ')}`
                    : 'Monitoring for stronger alignment across timeframes.';
                pushPulse(summary === 'BUY' ? 'alert' : 'live', title, body);
            });

            socket.addEventListener('close', () => {
                els.statSocket.textContent = 'Retrying';
                pushPulse('alert', 'Socket closed', 'Attempting to reconnect in 3 seconds.');
                window.setTimeout(connectSocket, 3000);
            });

            socket.addEventListener('error', () => {
                els.statSocket.textContent = 'Error';
            });
        }

        async function boot() {
            renderPulse();
            try {
                const overviewRes = await fetch('/overview');
                state.overview = await readJsonResponse(overviewRes, 'Overview request failed.');
                renderBoard();
                if (state.activeSymbol) {
                    await fetchDetail(state.activeSymbol);
                }
                connectSocket();
            } catch (error) {
                els.statusLine.textContent = error instanceof Error ? error.message : 'Dashboard failed to initialize.';
                els.statSocket.textContent = 'Offline';
            }
        }

        els.telegramSend.addEventListener('click', () => {
            void sendTelegramTest();
        });

        boot();
    </script>
</body>
</html>
"""
    return html.replace("__SYMBOLS_JSON__", symbols_json).replace("__SYMBOL_META_JSON__", symbol_metadata_json)
