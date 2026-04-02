(function () {
    const boot = window.GOLDBOT_BOOTSTRAP || {};
    const trackedSymbols = boot.symbols || [];
    const symbolMeta = boot.symbolMeta || {};
    const ruleSummary = boot.ruleSummary || {};
    const staleAfterSeconds = 15 * 60;
    const alertStorageKey = "goldbot.alertPrefs";
    const defaultPrefs = { notifications: false, sound: true, buyOnly: false };

    const state = {
        activeSymbol: trackedSymbols[0] || null,
        overview: [],
        botHealth: null,
        riskRegime: null,
        pulse: [],
        socket: null,
        socketStatus: "Connecting",
        lastGeneratedAt: null,
        alertStates: {},
        alertPrefs: loadPrefs(),
        audioContext: null,
    };

    const els = {
        board: document.getElementById("board"),
        statusLine: document.getElementById("status-line"),
        statBuy: document.getElementById("stat-buy"),
        statRiskMode: document.getElementById("stat-risk-mode"),
        statRiskMeta: document.getElementById("stat-risk-meta"),
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
        metricMa20Note: document.getElementById("metric-ma20-note"),
        metricMa50: document.getElementById("metric-ma50"),
        metricMa50Note: document.getElementById("metric-ma50-note"),
        metricRsi: document.getElementById("metric-rsi"),
        metricRsiNote: document.getElementById("metric-rsi-note"),
        metricRows: document.getElementById("metric-rows"),
        metricRowsNote: document.getElementById("metric-rows-note"),
        reasonList: document.getElementById("reason-list"),
        timeframes: document.getElementById("timeframes"),
        pulseList: document.getElementById("pulse-list"),
        priceChart: document.getElementById("price-chart"),
        chartRange: document.getElementById("chart-range"),
        telegramMessage: document.getElementById("telegram-message"),
        telegramSend: document.getElementById("telegram-send"),
        telegramStatus: document.getElementById("telegram-status"),
        toolsToggle: document.getElementById("tools-toggle"),
        toolsDrawer: document.getElementById("tools-drawer"),
        toolsBackdrop: document.getElementById("tools-backdrop"),
        toolsClose: document.getElementById("tools-close"),
        alertConfigButton: document.getElementById("alert-config-button"),
        alertConfigModal: document.getElementById("alert-config-modal"),
        alertConfigBackdrop: document.getElementById("alert-config-backdrop"),
        alertConfigClose: document.getElementById("alert-config-close"),
        configNotifications: document.getElementById("config-notifications"),
        configSound: document.getElementById("config-sound"),
        configBuyOnly: document.getElementById("config-buy-only"),
        configTestSound: document.getElementById("config-test-sound"),
        configStatus: document.getElementById("config-status"),
        logicVelocityName: document.getElementById("logic-velocity-name"),
        logicVelocityFormula: document.getElementById("logic-velocity-formula"),
        logicVelocityNote: document.getElementById("logic-velocity-note"),
        logicCoreRules: document.getElementById("logic-core-rules"),
        logicTimeframes: document.getElementById("logic-timeframes"),
    };

    function loadPrefs() {
        try {
            const raw = window.localStorage.getItem(alertStorageKey);
            return raw ? { ...defaultPrefs, ...JSON.parse(raw) } : { ...defaultPrefs };
        } catch {
            return { ...defaultPrefs };
        }
    }

    function savePrefs() {
        window.localStorage.setItem(alertStorageKey, JSON.stringify(state.alertPrefs));
    }

    function toggleBodyLock() {
        const open = !els.toolsDrawer.classList.contains("hidden") || !els.alertConfigModal.classList.contains("hidden");
        document.body.classList.toggle("drawer-open", open);
    }

    function openTools() {
        els.toolsDrawer.classList.remove("hidden");
        els.toolsDrawer.setAttribute("aria-hidden", "false");
        toggleBodyLock();
    }

    function closeTools() {
        els.toolsDrawer.classList.add("hidden");
        els.toolsDrawer.setAttribute("aria-hidden", "true");
        toggleBodyLock();
    }

    function openAlertConfig() {
        els.alertConfigModal.classList.remove("hidden");
        els.alertConfigModal.setAttribute("aria-hidden", "false");
        toggleBodyLock();
        syncAlertControls();
    }

    function closeAlertConfig() {
        els.alertConfigModal.classList.add("hidden");
        els.alertConfigModal.setAttribute("aria-hidden", "true");
        toggleBodyLock();
    }

    function formatPrice(value) {
        if (value == null || Number.isNaN(Number(value))) return "--";
        return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: Number(value) >= 100 ? 2 : 4 }).format(value);
    }

    function formatNumber(value) {
        return value == null || Number.isNaN(Number(value)) ? "--" : Number(value).toFixed(2);
    }

    function formatPct(value) {
        return value == null || Number.isNaN(Number(value)) ? "--" : `${(Number(value) * 100).toFixed(2)}%`;
    }

    function formatTime(value) {
        if (!value) return "--";
        const date = new Date(value);
        return Number.isNaN(date.getTime()) ? "--" : date.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
    }

    function formatDuration(seconds) {
        if (seconds == null || Number.isNaN(Number(seconds))) return "--";
        const numeric = Number(seconds);
        if (numeric % 3600 === 0) return `${numeric / 3600}h`;
        if (numeric % 60 === 0) return `${numeric / 60}m`;
        return `${numeric}s`;
    }

    function ageSeconds(value) {
        if (!value) return null;
        const date = new Date(value);
        return Number.isNaN(date.getTime()) ? null : Math.max(0, Math.round((Date.now() - date.getTime()) / 1000));
    }

    async function readJson(response, fallback) {
        const raw = await response.text();
        let payload = null;
        if (raw) {
            try {
                payload = JSON.parse(raw);
            } catch {
                if (!response.ok) throw new Error(raw.trim() || fallback);
                throw new Error(fallback);
            }
        }
        if (!response.ok) {
            throw new Error((payload && (payload.detail || payload.message)) || raw || fallback);
        }
        return payload;
    }

    function renderRuleSummary() {
        els.logicVelocityName.textContent = ruleSummary.velocity_name || "Directional change";
        els.logicVelocityFormula.textContent = ruleSummary.velocity_formula || "(latest_price - oldest_price) / oldest_price";
        els.logicVelocityNote.textContent = ruleSummary.velocity_note || "Velocity uses the oldest-to-latest move inside the selected window.";
        const core = [
            ["Fast drop window", `${ruleSummary.fast_drop_minutes ?? "--"}m`],
            ["Fast drop trigger", formatPct(ruleSummary.fast_drop_threshold)],
            ["RSI oversold", ruleSummary.rsi_oversold == null ? "--" : Number(ruleSummary.rsi_oversold).toFixed(1)],
            ["Minimum confidence", ruleSummary.minimum_confidence ?? "--"],
            ["Signal cooldown", `${ruleSummary.signal_cooldown_hours ?? "--"}h`],
            ["Stale timer", formatDuration(ruleSummary.stale_after_seconds)],
        ];
        els.logicCoreRules.innerHTML = core.map(([label, value]) => `<div class="logic-item"><span class="logic-item-label">${label}</span><span class="logic-item-value">${value}</span></div>`).join("");
        const windows = Array.isArray(ruleSummary.timeframes) ? ruleSummary.timeframes : [];
        els.logicTimeframes.innerHTML = windows.map((item) => `<div class="logic-item"><span class="logic-item-label">${item.key} window (${item.minutes}m)</span><span class="logic-item-value">${formatPct(item.drop_threshold)}</span></div>`).join("");
    }

    function syncAlertControls() {
        els.configNotifications.checked = Boolean(state.alertPrefs.notifications);
        els.configSound.checked = Boolean(state.alertPrefs.sound);
        els.configBuyOnly.checked = Boolean(state.alertPrefs.buyOnly);
        if (!("Notification" in window)) {
            els.configStatus.textContent = "This browser does not support desktop notifications. Sound still works.";
            return;
        }
        if (Notification.permission === "denied") {
            els.configStatus.textContent = "Browser notifications are blocked in this browser. Sound alerts still work.";
            return;
        }
        if (state.alertPrefs.notifications && Notification.permission !== "granted") {
            els.configStatus.textContent = "Enable browser permission to allow dashboard notifications.";
            return;
        }
        els.configStatus.textContent = "Settings are saved in this browser.";
    }

    function ensureAudioContext() {
        if (!("AudioContext" in window) && !("webkitAudioContext" in window)) return null;
        if (!state.audioContext) {
            const AudioCtor = window.AudioContext || window.webkitAudioContext;
            state.audioContext = new AudioCtor();
        }
        if (state.audioContext.state === "suspended") void state.audioContext.resume();
        return state.audioContext;
    }

    function playAlertSound(kind) {
        if (!state.alertPrefs.sound) return;
        const audio = ensureAudioContext();
        if (!audio) return;
        const now = audio.currentTime;
        const notes = kind === "STALE" ? [294, 247] : [523, 659, 784];
        notes.forEach((frequency, index) => {
            const osc = audio.createOscillator();
            const gain = audio.createGain();
            osc.type = kind === "STALE" ? "triangle" : "sine";
            osc.frequency.value = frequency;
            gain.gain.setValueAtTime(0.0001, now + index * 0.12);
            gain.gain.exponentialRampToValueAtTime(0.05, now + index * 0.12 + 0.02);
            gain.gain.exponentialRampToValueAtTime(0.0001, now + index * 0.12 + 0.18);
            osc.connect(gain);
            gain.connect(audio.destination);
            osc.start(now + index * 0.12);
            osc.stop(now + index * 0.12 + 0.2);
        });
    }

    function sendBrowserNotification(title, body) {
        if (!state.alertPrefs.notifications || !("Notification" in window) || Notification.permission !== "granted") return;
        const notification = new Notification(title, { body, silent: true });
        window.setTimeout(() => notification.close(), 7000);
    }

    function getAlertState(item) {
        if (!item) return { status: "WAIT", summary: "WAIT" };
        const summary = item.signal_summary || item.signals?.summary || "WAIT";
        return { status: item.is_stale ? "STALE" : summary, summary };
    }

    function primeAlertStates(items) {
        items.forEach((item) => {
            state.alertStates[item.symbol] = getAlertState(item);
        });
    }

    function shouldEmitAlert(symbol, nextState) {
        const prevState = state.alertStates[symbol];
        state.alertStates[symbol] = nextState;
        if (!prevState || prevState.status === nextState.status) return false;
        if (state.alertPrefs.buyOnly && nextState.status !== "BUY") return false;
        return nextState.status === "BUY" || nextState.status === "STALE";
    }

    function pushPulse(kind, title, body) {
        state.pulse = [{ kind, title, body }, ...state.pulse].slice(0, 6);
        renderPulse();
    }

    function renderPulse() {
        els.pulseList.innerHTML = state.pulse.map((item) => `<article class="pulse ${item.kind}"><strong>${item.title}</strong><span>${item.body}</span></article>`).join("");
    }

    function emitAlert(symbol, nextState, detail) {
        const label = detail?.label || symbolMeta[symbol]?.label || detail?.symbol || symbol;
        const activeWindows = detail?.signals?.active_timeframes || [];
        const title = nextState.status === "STALE" ? `${symbol} data stale` : `${symbol} buy setup`;
        const body = nextState.status === "STALE"
            ? `${label} has not refreshed recently. Check bot health and latest saves.`
            : `${label} is active on ${activeWindows.length ? activeWindows.join(", ") : "at least one timeframe"}.`;
        pushPulse("alert", title, body);
        playAlertSound(nextState.status);
        sendBrowserNotification(title, body);
    }

    function renderStatusLine() {
        const parts = [];
        if (state.socketStatus) parts.push(`Stream ${state.socketStatus}`);
        if (state.activeSymbol) parts.push(`Focus ${state.activeSymbol}`);
        if (state.lastGeneratedAt) parts.push(`Updated ${formatTime(state.lastGeneratedAt)}`);
        els.statusLine.textContent = parts.join(" | ") || "Preparing first market snapshot.";
    }

    function renderRiskRegime() {
        const risk = state.riskRegime || {};
        els.statRiskMode.textContent = risk.label || "Neutral";
        els.statRiskMeta.textContent = risk.summary || "Risk regime";
    }

    function renderBotHealth() {
        const health = state.botHealth || {};
        const stale = ageSeconds(health.updated_at);
        const status = stale && stale > staleAfterSeconds ? "Stale" : (health.status || "Idle");
        let meta = health.current_symbol || health.last_symbol || "Waiting for first fetch";
        if (health.last_error) meta = health.last_error;
        else if (health.last_price_save_at) meta = `Last save ${formatTime(health.last_price_save_at)}`;
        els.statBotHealth.textContent = status;
        els.statBotHealthMeta.textContent = meta;
    }

    function renderBoard() {
        els.statBuy.textContent = String(state.overview.filter((item) => item.signal_summary === "BUY").length);
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
            return `<article class="card ${active} ${stale}" data-symbol="${item.symbol}"><div class="card-top"><div><div class="symbol">${item.symbol}</div><div class="label">${item.label || symbolMeta[item.symbol]?.label || item.name || item.symbol}</div></div>${tinyPill}</div><div class="price">${formatPrice(item.price)}</div><div class="sub">RSI ${formatNumber(item.rsi)} | 1h ${formatPct(item.change_1h)}</div><div class="card-meta"><span>Updated ${formatTime(item.updated_at)}</span><span>${item.active_timeframes.length} windows</span></div>${badge}</article>`;
        }).join("");
        els.board.classList.remove("loading");
        for (const card of els.board.querySelectorAll(".card")) {
            card.addEventListener("click", () => {
                state.activeSymbol = card.dataset.symbol;
                renderBoard();
                renderStatusLine();
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
        const pad = { top: 22, right: 74, bottom: 34, left: 58 };
        const chartW = canvas.width - pad.left - pad.right;
        const chartH = canvas.height - pad.top - pad.bottom;
        const latestPrice = prices[prices.length - 1];
        els.chartRange.textContent = `Range ${formatPrice(min)} to ${formatPrice(max)}`;
        const pointX = (index) => pad.left + (index / Math.max(series.length - 1, 1)) * chartW;
        const pointY = (value) => pad.top + chartH - ((value - min) / range) * chartH;
        ctx.fillStyle = "rgba(255,255,255,0.72)";
        ctx.fillRect(pad.left, pad.top, chartW, chartH);
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
        const drawLine = (values, color, width) => {
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
        };
        drawLine(prices, "#8b5e1c", 3.2);
        drawLine(ma20, "#0d7a72", 2.2);
        drawLine(ma50, "#a64b3c", 2);
        const latestX = pointX(prices.length - 1);
        const latestY = pointY(latestPrice);
        ctx.beginPath();
        ctx.arc(latestX, latestY, 5, 0, Math.PI * 2);
        ctx.fillStyle = "#8b5e1c";
        ctx.fill();
        ctx.strokeStyle = "#fff8ef";
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.fillStyle = "#8b5e1c";
        ctx.textAlign = "left";
        ctx.textBaseline = "middle";
        ctx.font = "bold 12px Trebuchet MS";
        ctx.fillText(formatPrice(latestPrice), latestX + 10, latestY);
    }

    function renderTimeframes(detail) {
        const rows = detail?.signals?.timeframes || [];
        els.timeframes.innerHTML = rows.map((item) => {
            const magnitude = Math.min(Math.abs(Number(item.change || 0)) / 0.05, 1);
            const signal = item.signal || "WAIT";
            const reasons = item.reasons && item.reasons.length ? item.reasons.join(" | ").replaceAll("_", " ") : "No strong alignment yet";
            return `<div class="tf-row ${signal === "BUY" ? "buy" : "wait"}"><div class="tf-head"><div class="tf-tag">${item.timeframe}</div><div class="tf-chip ${signal === "BUY" ? "buy" : ""}">${signal}</div></div><div class="tf-bar"><div class="tf-fill" style="width:${Math.max(magnitude * 100, 4)}%"></div></div><div class="tf-meta"><div class="tf-value">${formatPct(item.change)}</div><div class="tf-confidence">Confidence ${item.confidence}</div></div><div class="tf-reasons">${reasons}</div></div>`;
        }).join("");
    }

    function renderReasons(detail) {
        const rows = detail?.signals?.timeframes || [];
        const active = rows.filter((item) => item.reasons && item.reasons.length);
        const cards = active.length ? active : [{ timeframe: "No edge", reasons: ["WAIT"], confidence: 0 }];
        els.reasonList.innerHTML = cards.map((item) => `<article class="reason"><strong>${item.timeframe} | ${item.signal || "WAIT"} | confidence ${item.confidence}</strong><span>${item.reasons.join(", ")}</span></article>`).join("");
    }

    function renderDetail(detail) {
        const indicators = detail.indicators || {};
        const summary = detail.signals?.summary || "WAIT";
        const activeTimeframes = detail.signals?.active_timeframes || [];
        const stale = detail.is_stale;
        els.detailSymbol.textContent = detail.label || detail.symbol;
        els.detailTitle.textContent = detail.name || detail.symbol;
        els.detailCopy.textContent = stale ? `${detail.symbol} looks stale. Check the bot health panel while reviewing the latest saved data.` : summary === "BUY" ? `${detail.symbol} is active across ${activeTimeframes.length} timeframe${activeTimeframes.length === 1 ? "" : "s"}.` : `${detail.symbol} has not reached the current buy threshold across the timeframe stack.`;
        els.detailChip.textContent = stale ? "Stale" : summary;
        els.detailChip.className = `signal-chip ${summary === "BUY" && !stale ? "" : "wait"}`.trim();
        els.detailPrice.textContent = formatPrice(detail.price);
        els.summarySignal.textContent = stale ? "STALE" : summary;
        els.summaryWindows.textContent = activeTimeframes.length ? activeTimeframes.join(", ") : "None";
        els.summaryRefresh.textContent = formatTime(detail.updated_at);
        els.metricMa20.textContent = formatPrice(indicators.ma20);
        els.metricMa20Note.textContent = indicators.ma20 == null ? "Not enough data for MA20 yet" : "20-period average";
        els.metricMa50.textContent = indicators.ma50 == null ? "Building" : formatPrice(indicators.ma50);
        els.metricMa50Note.textContent = indicators.ma50 == null ? "Need 50 rows before MA50 appears" : "50-period average";
        els.metricRsi.textContent = formatNumber(indicators.rsi);
        els.metricRsiNote.textContent = indicators.rsi == null ? "Waiting for RSI history" : Number(indicators.rsi) <= 35 ? "Oversold zone" : Number(indicators.rsi) >= 65 ? "Strong momentum" : "Neutral momentum";
        const rowCount = (detail.history || []).length;
        els.metricRows.textContent = String(rowCount);
        els.metricRowsNote.textContent = rowCount < 50 ? `${50 - rowCount} more rows to unlock MA50` : "Enough history for full stack";
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
            const payload = await readJson(response, "Telegram test failed.");
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
        const detail = await readJson(response, "Snapshot request failed.");
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
        if (frame.risk_regime) {
            state.riskRegime = frame.risk_regime;
            renderRiskRegime();
        }
        if (frame.generated_at) {
            state.lastGeneratedAt = frame.generated_at;
            renderStatusLine();
        }
    }

    async function updateNotificationPreference(enabled) {
        if (!enabled) {
            state.alertPrefs.notifications = false;
            savePrefs();
            syncAlertControls();
            return;
        }
        if (!("Notification" in window)) {
            state.alertPrefs.notifications = false;
            syncAlertControls();
            return;
        }
        const permission = await Notification.requestPermission();
        state.alertPrefs.notifications = permission === "granted";
        savePrefs();
        syncAlertControls();
    }

    function connectSocket() {
        const protocol = window.location.protocol === "https:" ? "wss" : "ws";
        const socket = new WebSocket(`${protocol}://${window.location.host}/ws/market`);
        state.socket = socket;
        socket.addEventListener("open", () => {
            state.socketStatus = "Live";
            renderStatusLine();
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
            const detail = frame.detail;
            const summary = detail?.signals?.summary || "WAIT";
            const title = `${detail?.symbol || state.activeSymbol} ${summary}`;
            const body = detail?.is_stale ? "Latest saved data looks stale." : summary === "BUY" ? `Active windows: ${(detail?.signals?.active_timeframes || []).join(", ")}` : "Monitoring for stronger alignment across timeframes.";
            let emittedAlert = false;
            if (detail) {
                const nextState = getAlertState(detail);
                if (shouldEmitAlert(detail.symbol, nextState)) {
                    emitAlert(detail.symbol, nextState, detail);
                    emittedAlert = true;
                }
            }
            if (!emittedAlert) pushPulse(summary === "BUY" ? "alert" : "live", title, body);
        });
        socket.addEventListener("close", () => {
            state.socketStatus = "Retrying";
            renderStatusLine();
            pushPulse("alert", "Socket closed", "Attempting to reconnect in 3 seconds.");
            window.setTimeout(connectSocket, 3000);
        });
        socket.addEventListener("error", () => {
            state.socketStatus = "Error";
            renderStatusLine();
        });
    }

    async function bootDashboard() {
        renderPulse();
        syncAlertControls();
        renderRuleSummary();
        renderRiskRegime();
        renderBotHealth();
        renderStatusLine();
        try {
            const [overviewRes, botHealthRes, riskRes] = await Promise.all([
                fetch("/overview"),
                fetch("/bot/health"),
                fetch("/market/risk"),
            ]);
            state.overview = await readJson(overviewRes, "Overview request failed.");
            state.botHealth = await readJson(botHealthRes, "Bot health request failed.");
            state.riskRegime = await readJson(riskRes, "Risk regime request failed.");
            primeAlertStates(state.overview);
            renderBoard();
            renderBotHealth();
            renderRiskRegime();
            if (state.activeSymbol) await fetchDetail(state.activeSymbol);
            connectSocket();
        } catch (error) {
            state.socketStatus = "Offline";
            els.statusLine.textContent = error instanceof Error ? error.message : "Dashboard failed to initialize.";
        }
    }

    els.telegramSend.addEventListener("click", () => { void sendTelegramTest(); });
    els.toolsToggle.addEventListener("click", openTools);
    els.toolsClose.addEventListener("click", closeTools);
    els.toolsBackdrop.addEventListener("click", closeTools);
    els.alertConfigButton.addEventListener("click", openAlertConfig);
    els.alertConfigClose.addEventListener("click", closeAlertConfig);
    els.alertConfigBackdrop.addEventListener("click", closeAlertConfig);
    els.configNotifications.addEventListener("change", () => { void updateNotificationPreference(els.configNotifications.checked); });
    els.configSound.addEventListener("change", () => {
        state.alertPrefs.sound = els.configSound.checked;
        savePrefs();
        syncAlertControls();
    });
    els.configBuyOnly.addEventListener("change", () => {
        state.alertPrefs.buyOnly = els.configBuyOnly.checked;
        savePrefs();
        syncAlertControls();
    });
    els.configTestSound.addEventListener("click", () => {
        playAlertSound("BUY");
        els.configStatus.textContent = "Played the dashboard alert chime.";
    });
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeAlertConfig();
            closeTools();
        }
    });

    bootDashboard();
})();
