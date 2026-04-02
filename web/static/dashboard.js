(function () {
    const bootstrap = window.GOLDBOT_BOOTSTRAP || { symbols: [], symbolMeta: {} };
    const trackedSymbols = bootstrap.symbols || [];
    const symbolMeta = bootstrap.symbolMeta || {};
    const staleAfterSeconds = 15 * 60;

    const state = {
        activeSymbol: trackedSymbols[0] || null,
        overview: [],
        detail: null,
        socket: null,
        pulse: [],
        botHealth: null,
    };

    const els = {
        board: document.getElementById("board"),
        statusLine: document.getElementById("status-line"),
        statSymbols: document.getElementById("stat-symbols"),
        statBuy: document.getElementById("stat-buy"),
        statFocus: document.getElementById("stat-focus"),
        statSocket: document.getElementById("stat-socket"),
        statBotHealth: document.getElementById("stat-bot-health"),
        statBotHealthMeta: document.getElementById("stat-bot-health-meta"),
        detailSymbol: document.getElementById("detail-symbol"),
        detailTitle: document.getElementById("detail-title"),
        detailCopy: document.getElementById("detail-copy"),
        detailChip: document.getElementById("detail-chip"),
        detailPrice: document.getElementById("detail-price"),
        summarySignal: document.getElementById("summary-signal"),
        summaryWindows: document.getElementById("summary-windows"),
        summaryRefresh: document.getElementById("summary-refresh"),
        metricMa20: document.getElementById("metric-ma20"),
        metricMa50: document.getElementById("metric-ma50"),
        metricRsi: document.getElementById("metric-rsi"),
        metricRows: document.getElementById("metric-rows"),
        timeframes: document.getElementById("timeframes"),
        reasonList: document.getElementById("reason-list"),
        pulseList: document.getElementById("pulse-list"),
        priceChart: document.getElementById("price-chart"),
        telegramMessage: document.getElementById("telegram-message"),
        telegramSend: document.getElementById("telegram-send"),
        telegramStatus: document.getElementById("telegram-status"),
    };

    function formatPrice(value) {
        if (value === null || value === undefined || Number.isNaN(Number(value))) return "--";
        return new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: "USD",
            maximumFractionDigits: Number(value) >= 100 ? 2 : 4,
        }).format(value);
    }

    function formatNumber(value) {
        if (value === null || value === undefined || Number.isNaN(Number(value))) return "--";
        return Number(value).toFixed(2);
    }

    function formatPct(value) {
        if (value === null || value === undefined || Number.isNaN(Number(value))) return "--";
        return `${(Number(value) * 100).toFixed(2)}%`;
    }

    function formatTime(value) {
        if (!value) return "--";
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return "--";
        return date.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
    }

    function ageSeconds(value) {
        if (!value) return null;
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return null;
        return Math.max(0, Math.round((Date.now() - date.getTime()) / 1000));
    }

    async function readJsonResponse(response, fallbackMessage) {
        const rawText = await response.text();
        let payload = null;
        if (rawText) {
            try {
                payload = JSON.parse(rawText);
            } catch (error) {
                if (!response.ok) throw new Error(rawText.trim() || fallbackMessage);
                throw new Error(fallbackMessage);
            }
        }
        if (!response.ok) {
            const detail = payload && typeof payload === "object"
                ? (payload.detail || payload.message || rawText)
                : rawText;
            throw new Error(detail || fallbackMessage);
        }
        return payload;
    }

    function pushPulse(kind, title, body) {
        state.pulse = [{ kind, title, body }, ...state.pulse].slice(0, 6);
        renderPulse();
    }

    function renderPulse() {
        els.pulseList.innerHTML = state.pulse.map((item) => `
            <article class="pulse ${item.kind}">
                <strong>${item.title}</strong>
                <span>${item.body}</span>
            </article>
        `).join("");
    }

    function renderBotHealth() {
        const health = state.botHealth || {};
        const stale = ageSeconds(health.updated_at);
        const status = stale && stale > staleAfterSeconds ? "Stale" : (health.status || "Idle");
        let meta = health.current_symbol || health.last_symbol || "Waiting for first fetch";

        if (health.last_error) {
            meta = health.last_error;
        } else if (health.last_price_save_at) {
            meta = `Last save ${formatTime(health.last_price_save_at)}`;
        }

        els.statBotHealth.textContent = status;
        els.statBotHealthMeta.textContent = meta;
    }

    function renderBoard() {
        els.statSymbols.textContent = String(state.overview.length);
        els.statBuy.textContent = String(state.overview.filter((item) => item.signal_summary === "BUY").length);
        els.statFocus.textContent = state.activeSymbol || "-";

        els.board.innerHTML = state.overview.map((item) => {
            const active = item.symbol === state.activeSymbol ? "active" : "";
            const stale = item.is_stale ? "stale" : "";
            const badge = item.signal_summary === "BUY"
                ? `<div class="badge live">${item.active_timeframes.length} active windows</div>`
                : `<div class="badge calm">No trigger</div>`;
            const tinyPill = item.is_stale
                ? `<div class="tiny-pill stale">Stale</div>`
                : item.signal_summary === "BUY"
                    ? `<div class="tiny-pill buy">Buy setup</div>`
                    : `<div class="tiny-pill">Watching</div>`;
            return `
                <article class="card ${active} ${stale}" data-symbol="${item.symbol}">
                    <div class="card-top">
                        <div>
                            <div class="symbol">${item.symbol}</div>
                            <div class="label">${item.label || symbolMeta[item.symbol]?.label || item.name || item.symbol}</div>
                        </div>
                        ${tinyPill}
                    </div>
                    <div class="price">${formatPrice(item.price)}</div>
                    <div class="sub">RSI ${formatNumber(item.rsi)} | 1h ${formatPct(item.change_1h)}</div>
                    <div class="card-meta">
                        <span>Updated ${formatTime(item.updated_at)}</span>
                        <span>${item.active_timeframes.length} windows</span>
                    </div>
                    ${badge}
                </article>
            `;
        }).join("");

        els.board.classList.remove("loading");
        for (const card of els.board.querySelectorAll(".card")) {
            card.addEventListener("click", () => {
                state.activeSymbol = card.dataset.symbol;
                renderBoard();
                if (state.socket && state.socket.readyState === WebSocket.OPEN) {
                    state.socket.send(JSON.stringify({ type: "focus", symbol: state.activeSymbol }));
                } else {
                    void fetchDetail(state.activeSymbol);
                }
            });
        }
    }

    function drawChart(detail) {
        const canvas = els.priceChart;
        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        const history = detail?.history || [];
        if (history.length < 2) {
            ctx.fillStyle = "#6c665b";
            ctx.font = "16px Trebuchet MS";
            ctx.fillText("Not enough history to draw chart yet.", 18, 30);
            return;
        }

        const series = history.slice(-48);
        const prices = series.map((point) => Number(point.price));
        const ma20 = series.map((point) => point.ma20 == null ? null : Number(point.ma20));
        const ma50 = series.map((point) => point.ma50 == null ? null : Number(point.ma50));
        const allValues = [...prices, ...ma20.filter((v) => v != null), ...ma50.filter((v) => v != null)];
        const min = Math.min(...allValues);
        const max = Math.max(...allValues);
        const range = max - min || 1;
        const pad = { top: 18, right: 18, bottom: 30, left: 58 };
        const chartW = canvas.width - pad.left - pad.right;
        const chartH = canvas.height - pad.top - pad.bottom;

        function pointX(index) {
            return pad.left + (index / Math.max(series.length - 1, 1)) * chartW;
        }

        function pointY(value) {
            return pad.top + chartH - ((value - min) / range) * chartH;
        }

        ctx.strokeStyle = "rgba(108, 102, 91, 0.18)";
        ctx.lineWidth = 1;
        for (let i = 0; i < 4; i += 1) {
            const y = pad.top + (chartH / 3) * i;
            ctx.beginPath();
            ctx.moveTo(pad.left, y);
            ctx.lineTo(canvas.width - pad.right, y);
            ctx.stroke();
        }

        ctx.fillStyle = "#6c665b";
        ctx.font = "12px Trebuchet MS";
        ctx.textAlign = "right";
        ctx.textBaseline = "middle";
        for (let i = 0; i < 4; i += 1) {
            const value = max - (range / 3) * i;
            const y = pad.top + (chartH / 3) * i;
            ctx.fillText(formatPrice(value), pad.left - 8, y);
        }

        ctx.textAlign = "left";
        ctx.textBaseline = "top";
        ctx.fillText("Older", pad.left, canvas.height - pad.bottom + 8);
        ctx.textAlign = "right";
        ctx.fillText("Latest", canvas.width - pad.right, canvas.height - pad.bottom + 8);

        ctx.beginPath();
        prices.forEach((value, index) => {
            const x = pointX(index);
            const y = pointY(value);
            if (index === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        });
        ctx.lineTo(pointX(prices.length - 1), canvas.height - pad.bottom);
        ctx.lineTo(pointX(0), canvas.height - pad.bottom);
        ctx.closePath();
        ctx.fillStyle = "rgba(198, 138, 45, 0.14)";
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
            ctx.lineCap = "round";
            ctx.lineJoin = "round";
            ctx.stroke();
        }

        drawLine(prices, "#8b5e1c", 3.2);
        drawLine(ma20, "#0d7a72", 2.2);
        drawLine(ma50, "#a64b3c", 2);
    }

    function renderTimeframes(detail) {
        const rows = detail?.signals?.timeframes || [];
        els.timeframes.innerHTML = rows.map((item) => {
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
        }).join("");
    }

    function renderReasons(detail) {
        const rows = detail?.signals?.timeframes || [];
        const active = rows.filter((item) => item.reasons && item.reasons.length);
        const cards = active.length ? active : [{ timeframe: "No edge", reasons: ["WAIT"], confidence: 0 }];
        els.reasonList.innerHTML = cards.map((item) => `
            <article class="reason">
                <strong>${item.timeframe} | ${item.signal || "WAIT"} | confidence ${item.confidence}</strong>
                <span>${item.reasons.join(", ")}</span>
            </article>
        `).join("");
    }

    function renderDetail(detail) {
        state.detail = detail;
        const indicators = detail.indicators || {};
        const summary = detail.signals?.summary || "WAIT";
        const activeTimeframes = detail.signals?.active_timeframes || [];
        const stale = detail.is_stale;

        els.detailSymbol.textContent = detail.label || detail.symbol;
        els.detailTitle.textContent = detail.name || detail.symbol;
        els.detailCopy.textContent = stale
            ? `${detail.symbol} looks stale. Check the bot health panel while reviewing the latest saved data.`
            : summary === "BUY"
                ? `${detail.symbol} is active across ${activeTimeframes.length} timeframe${activeTimeframes.length === 1 ? "" : "s"}.`
                : `${detail.symbol} has not reached the current buy threshold across the timeframe stack.`;
        els.detailChip.textContent = stale ? "Stale" : summary;
        els.detailChip.className = `signal-chip ${summary === "BUY" && !stale ? "" : "wait"}`.trim();
        els.detailPrice.textContent = formatPrice(detail.price);
        els.summarySignal.textContent = stale ? "STALE" : summary;
        els.summaryWindows.textContent = activeTimeframes.length ? activeTimeframes.join(", ") : "None";
        els.summaryRefresh.textContent = formatTime(detail.updated_at);
        els.metricMa20.textContent = formatPrice(indicators.ma20);
        els.metricMa50.textContent = formatPrice(indicators.ma50);
        els.metricRsi.textContent = formatNumber(indicators.rsi);
        els.metricRows.textContent = String((detail.history || []).length);

        if (!els.telegramMessage.value.trim() || els.telegramMessage.value.includes("dashboard test ping")) {
            els.telegramMessage.value = `Goldbot dashboard test for ${detail.symbol} at ${new Date().toLocaleTimeString()}.`;
        }

        drawChart(detail);
        renderTimeframes(detail);
        renderReasons(detail);
    }

    async function sendTelegramTest() {
        const message = els.telegramMessage.value.trim();
        els.telegramSend.disabled = true;
        els.telegramStatus.textContent = "Sending Telegram test...";

        try {
            const response = await fetch("/telegram/test", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message }),
            });
            const payload = await readJsonResponse(response, "Telegram test failed.");
            if (!payload.ok) throw new Error(payload.detail || "Telegram test failed.");
            els.telegramStatus.textContent = `Sent: ${payload.message}`;
            pushPulse("live", "Telegram test sent", payload.message);
        } catch (error) {
            const messageText = error instanceof Error ? error.message : "Telegram test failed.";
            els.telegramStatus.textContent = messageText;
            pushPulse("alert", "Telegram test error", messageText);
        } finally {
            els.telegramSend.disabled = false;
        }
    }

    async function fetchDetail(symbol) {
        const response = await fetch(`/snapshot/${encodeURIComponent(symbol)}`);
        const detail = await readJsonResponse(response, "Snapshot request failed.");
        renderDetail(detail);
    }

    function applyFrame(frame) {
        if (Array.isArray(frame.overview)) {
            state.overview = frame.overview;
            renderBoard();
        }
        if (frame.detail) renderDetail(frame.detail);
        if (frame.bot_health) {
            state.botHealth = frame.bot_health;
            renderBotHealth();
        }
        if (frame.generated_at) {
            els.statusLine.textContent = `Last update ${new Date(frame.generated_at).toLocaleTimeString()}`;
        }
    }

    function connectSocket() {
        const protocol = window.location.protocol === "https:" ? "wss" : "ws";
        const socket = new WebSocket(`${protocol}://${window.location.host}/ws/market`);
        state.socket = socket;

        socket.addEventListener("open", () => {
            els.statSocket.textContent = "Live";
            pushPulse("live", "Socket connected", "Streaming fresh market snapshots.");
            socket.send(JSON.stringify({ type: "focus", symbol: state.activeSymbol }));
        });

        socket.addEventListener("message", (event) => {
            const frame = JSON.parse(event.data);
            if (frame.error) {
                els.statusLine.textContent = frame.error;
                pushPulse("alert", "Market frame error", frame.error);
                return;
            }
            applyFrame(frame);
            const summary = frame.detail?.signals?.summary || "WAIT";
            const title = `${frame.detail?.symbol || state.activeSymbol} ${summary}`;
            const body = frame.detail?.is_stale
                ? "Latest saved data looks stale."
                : summary === "BUY"
                    ? `Active windows: ${(frame.detail?.signals?.active_timeframes || []).join(", ")}`
                    : "Monitoring for stronger alignment across timeframes.";
            pushPulse(summary === "BUY" ? "alert" : "live", title, body);
        });

        socket.addEventListener("close", () => {
            els.statSocket.textContent = "Retrying";
            pushPulse("alert", "Socket closed", "Attempting to reconnect in 3 seconds.");
            window.setTimeout(connectSocket, 3000);
        });

        socket.addEventListener("error", () => {
            els.statSocket.textContent = "Error";
        });
    }

    async function boot() {
        renderPulse();
        renderBotHealth();
        try {
            const [overviewRes, botHealthRes] = await Promise.all([
                fetch("/overview"),
                fetch("/bot/health"),
            ]);
            state.overview = await readJsonResponse(overviewRes, "Overview request failed.");
            state.botHealth = await readJsonResponse(botHealthRes, "Bot health request failed.");
            renderBoard();
            renderBotHealth();
            if (state.activeSymbol) await fetchDetail(state.activeSymbol);
            connectSocket();
        } catch (error) {
            els.statusLine.textContent = error instanceof Error ? error.message : "Dashboard failed to initialize.";
            els.statSocket.textContent = "Offline";
        }
    }

    els.telegramSend.addEventListener("click", () => {
        void sendTelegramTest();
    });

    boot();
})();
