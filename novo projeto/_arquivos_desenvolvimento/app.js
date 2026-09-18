// Domino's Pizza Performance PWR - Dashboard Diário Consolidado
document.addEventListener('DOMContentLoaded', async () => {
    let rawData = null;
    let currentSegment = 'all'; // 'all', 'F', 'C'
    let activeTab = 'semanal';

    // Elementos DOM
    const syncTimeEl = document.getElementById('sync-time');
    const consultantSelect = document.getElementById('filter-consultant');
    const franchiseeSelect = document.getElementById('filter-franchisee');
    const searchInput = document.getElementById('search-store');
    const segmentBtns = document.querySelectorAll('.segment-btn');
    const tabBtns = document.querySelectorAll('.tab-btn');

    // Elementos KPI
    const kpiAdtVal = document.getElementById('kpi-adt-num');
    const kpiAdtCard = document.getElementById('kpi-adt-avg');
    const kpiExtremesVal = document.getElementById('kpi-extremes-num');
    const kpiExtremesCard = document.getElementById('kpi-extremes-avg');
    const kpiExcVal = document.getElementById('kpi-exceptions-num');
    const kpiExcCard = document.getElementById('kpi-exceptions-avg');

    const kpiAdtCritical = document.getElementById('kpi-adt-critical');
    const kpiExtremesCritical = document.getElementById('kpi-extremes-critical');
    const kpiExceptionsCritical = document.getElementById('kpi-exceptions-critical');

    // Tabelas
    const tableAdt = document.getElementById('table-adt');
    const tableExc = document.getElementById('table-exceptions');
    const tbodyRisk = document.getElementById('tbody-risk');
    const tbodyBackfill = document.getElementById('tbody-backfill');

    // Contadores de Lojas
    const countAllEl = document.getElementById('count-all');
    const countFranEl = document.getElementById('count-fran');
    const countCorpEl = document.getElementById('count-corp');

    // Formatadores e Cores de Meta
    function getAdtStyle(adt) {
        if (!adt || adt <= 0) return 'color: #94a3b8;';
        if (adt < 25) return 'color: var(--success-color); font-weight: 700;';
        if (adt < 30) return 'color: var(--warning-color); font-weight: 700;';
        if (adt <= 40) return 'color: #f97316; font-weight: 700;';
        return 'color: var(--danger-color); font-weight: 800;';
    }

    function getExtremeStyle(ext) {
        if (ext === undefined || ext === null || ext < 0) return 'color: #94a3b8;';
        const pct = ext * 100;
        if (pct < 2) return 'color: var(--success-color); font-weight: 700;';
        if (pct < 10) return 'color: var(--warning-color); font-weight: 700;';
        if (pct <= 20) return 'color: #f97316; font-weight: 700;';
        return 'color: var(--danger-color); font-weight: 800;';
    }

    function getExceptionStyle(exc) {
        if (exc === undefined || exc === null || exc < 0) return 'color: #94a3b8;';
        const pct = exc * 100;
        if (pct < 10) return 'color: var(--success-color); font-weight: 700;';
        if (pct < 25) return 'color: var(--warning-color); font-weight: 700;';
        if (pct <= 40) return 'color: #f97316; font-weight: 700;';
        return 'color: var(--danger-color); font-weight: 800;';
    }

    // Carregar Dados
    async function loadData() {
        if (window.PWR_DATA) {
            rawData = window.PWR_DATA;
        } else {
            try {
                const res = await fetch('data.json');
                rawData = await res.json();
            } catch (err) {
                console.error("Erro ao carregar dados:", err);
                syncTimeEl.textContent = "Erro ao carregar dados";
                return;
            }
        }
        syncTimeEl.textContent = `Atualizado: ${rawData.updatedAt || 'Hoje'}`;
        initDashboard();
    }

    function initDashboard() {
        populateFilters();
        updateSegmentCounts();
        setupEvents();
        renderCurrentView();
    }

    function updateSegmentCounts() {
        let total = 0, fran = 0, corp = 0;
        for (const sid in rawData.stores) {
            total++;
            if (rawData.stores[sid].type === 'C') corp++;
            else fran++;
        }
        if (countAllEl) countAllEl.textContent = total;
        if (countFranEl) countFranEl.textContent = fran;
        if (countCorpEl) countCorpEl.textContent = corp;
    }

    function populateFilters() {
        const consultants = new Set();
        const franchisees = new Set();

        for (const sid in rawData.stores) {
            const st = rawData.stores[sid];
            if (st.consultant && st.consultant !== 'N/D') consultants.add(st.consultant);
            if (st.franchisee && st.franchisee !== 'N/D') franchisees.add(st.franchisee);
        }

        consultantSelect.innerHTML = '<option value="all">Todos os Consultores</option>';
        Array.from(consultants).sort().forEach(c => {
            const opt = document.createElement('option');
            opt.value = c;
            opt.textContent = c;
            consultantSelect.appendChild(opt);
        });

        franchiseeSelect.innerHTML = '<option value="all">Todos os Franqueados</option>';
        Array.from(franchisees).sort().forEach(f => {
            const opt = document.createElement('option');
            opt.value = f;
            opt.textContent = f;
            franchiseeSelect.appendChild(opt);
        });
    }

    function setupEvents() {
        segmentBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                segmentBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentSegment = btn.getAttribute('data-segment');
                renderCurrentView();
            });
        });

        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                tabBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                activeTab = btn.getAttribute('data-tab');

                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                if (activeTab === 'semanal') document.getElementById('capture-area').classList.add('active');
                if (activeTab === 'risco') document.getElementById('risk-view').classList.add('active');
                if (activeTab === 'backfill') document.getElementById('backfill-view').classList.add('active');

                renderCurrentView();
            });
        });

        consultantSelect.addEventListener('change', renderCurrentView);
        franchiseeSelect.addEventListener('change', renderCurrentView);
        searchInput.addEventListener('input', renderCurrentView);

        const btnExport = document.getElementById('btn-export');
        if (btnExport) {
            btnExport.addEventListener('click', exportToPng);
        }
    }

    function getFilteredStores() {
        const selCons = consultantSelect.value;
        const selFran = franchiseeSelect.value;
        const term = searchInput.value.toLowerCase().trim();

        const filtered = [];
        for (const sid in rawData.stores) {
            const st = rawData.stores[sid];
            
            // Segmento
            if (currentSegment !== 'all' && st.type !== currentSegment) continue;
            // Consultor
            if (selCons !== 'all' && st.consultant !== selCons) continue;
            // Franqueado
            if (selFran !== 'all' && st.franchisee !== selFran) continue;
            // Busca
            if (term) {
                const matchId = sid.includes(term);
                const matchName = (st.name || '').toLowerCase().includes(term);
                const matchCons = (st.consultant || '').toLowerCase().includes(term);
                const matchFran = (st.franchisee || '').toLowerCase().includes(term);
                if (!matchId && !matchName && !matchCons && !matchFran) continue;
            }

            filtered.push(sid);
        }

        return filtered;
    }

    function renderCurrentView() {
        const stores = getFilteredStores();
        renderKPIs(stores);
        if (activeTab === 'semanal') {
            renderAdtTable(stores);
            renderExceptionsTable(stores);
        } else if (activeTab === 'risco') {
            renderRiskTable(stores);
        } else if (activeTab === 'backfill') {
            renderBackfillTable(stores);
        }
    }

    function drawSparkline(canvas, values, isGoodLow = true) {
        if (!canvas || values.length < 2) return;
        const ctx = canvas.getContext('2d');
        const w = canvas.width;
        const h = canvas.height;
        ctx.clearRect(0, 0, w, h);

        const validVals = values.filter(v => v !== null && v !== undefined && !isNaN(v));
        if (validVals.length < 2) return;

        let localMin = Math.min(...validVals);
        let localMax = Math.max(...validVals);
        if (localMin === localMax) { localMin -= 1; localMax += 1; }

        ctx.lineWidth = 2.5;
        const lastVal = validVals[validVals.length - 1];
        const prevVal = validVals[validVals.length - 2];
        const isBetter = isGoodLow ? (lastVal <= prevVal) : (lastVal >= prevVal);
        ctx.strokeStyle = isBetter ? '#10b981' : '#ef4444';

        ctx.beginPath();
        const step = (w - 12) / (values.length - 1);

        values.forEach((v, idx) => {
            const x = 6 + idx * step;
            const norm = (v - localMin) / (localMax - localMin);
            const y = h - 6 - norm * (h - 12);
            if (idx === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        });
        ctx.stroke();

        const lastX = 6 + (values.length - 1) * step;
        const lastNorm = (lastVal - localMin) / (localMax - localMin);
        const lastY = h - 6 - lastNorm * (h - 12);
        ctx.fillStyle = ctx.strokeStyle;
        ctx.beginPath();
        ctx.arc(lastX, lastY, 3.5, 0, Math.PI * 2);
        ctx.fill();
    }

    function renderKPIs(storeIds) {
        const acumList = rawData.adt.acumulado || [];
        const excAcumList = rawData.exceptions.acumulado || [];

        let totalDelv = 0;
        let sumAdtWeight = 0;
        let sumExtWeight = 0;
        let sumExcWeight = 0;

        const criticalAdt = [];
        const criticalExt = [];
        const criticalExc = [];

        const storeSet = new Set(storeIds);

        acumList.forEach(r => {
            if (!storeSet.has(r.storeId)) return;
            const delv = r.delvOrders || r.orders || 0;
            totalDelv += delv;
            sumAdtWeight += (r.adt || 0) * delv;
            sumExtWeight += (r.extreme || 0) * delv;

            if (r.adt >= 40) criticalAdt.push(r.storeId);
            if ((r.extreme * 100) >= 10) criticalExt.push(r.storeId);
        });

        excAcumList.forEach(r => {
            if (!storeSet.has(r.storeId)) return;
            const delv = r.delvOrders || 0;
            sumExcWeight += (r.exceptions || 0) * delv;
            if ((r.exceptions * 100) >= 20) criticalExc.push(r.storeId);
        });

        const avgAdt = totalDelv > 0 ? (sumAdtWeight / totalDelv) : 0;
        const avgExt = totalDelv > 0 ? (sumExtWeight / totalDelv * 100) : 0;
        const avgExc = totalDelv > 0 ? (sumExcWeight / totalDelv * 100) : 0;

        kpiAdtVal.textContent = avgAdt > 0 ? `${avgAdt.toFixed(1)} min` : '--';
        kpiAdtVal.style = getAdtStyle(avgAdt);

        kpiExtremesVal.textContent = avgExt > 0 ? `${avgExt.toFixed(1)}%` : '0.0%';
        kpiExtremesVal.style = getExtremeStyle(avgExt / 100.0);

        kpiExcVal.textContent = avgExc > 0 ? `${avgExc.toFixed(1)}%` : '0.0%';
        kpiExcVal.style = getExceptionStyle(avgExc / 100.0);

        kpiAdtCritical.innerHTML = criticalAdt.length > 0
            ? `<span class="badge" style="background-color: var(--danger-bg); color: var(--danger-color); font-weight: 700;">${criticalAdt.length} lojas &gt; 40 min</span>`
            : `<span class="badge" style="background-color: var(--success-bg); color: var(--success-color); font-weight: 700;">Nenhuma loja crítica</span>`;

        kpiExtremesCritical.innerHTML = criticalExt.length > 0
            ? `<span class="badge" style="background-color: var(--danger-bg); color: var(--danger-color); font-weight: 700;">${criticalExt.length} lojas &gt; 10%</span>`
            : `<span class="badge" style="background-color: var(--success-bg); color: var(--success-color); font-weight: 700;">Nenhuma loja crítica</span>`;

        kpiExceptionsCritical.innerHTML = criticalExc.length > 0
            ? `<span class="badge" style="background-color: var(--danger-bg); color: var(--danger-color); font-weight: 700;">${criticalExc.length} lojas &gt; 20%</span>`
            : `<span class="badge" style="background-color: var(--success-bg); color: var(--success-color); font-weight: 700;">Nenhuma loja crítica</span>`;
    }

    // -------------------------------------------------------------
    // RENDERIZAÇÃO DA TABELA DE eADT & % EXTREMOS
    // -------------------------------------------------------------
    function renderAdtTable(storeIds) {
        const weeks = rawData.weeks || [];
        const adtWeeks = rawData.adt.weeks || {};
        const adtAcum = rawData.adt.acumulado || [];
        const acumTitle = rawData.acumuladoTitle || 'Acumulado';

        let theadHtml = `
            <tr>
                <th rowspan="2" style="vertical-align: bottom; min-width: 240px;">Loja</th>
                <th colspan="${weeks.length + 1}" class="th-group" style="border-left: 2px solid var(--border-color); color: var(--dominos-blue);">Tempo de Entrega (eADT min)</th>
                <th colspan="${weeks.length + 1}" class="th-group" style="border-left: 2px solid var(--border-color); color: #0284c7;">% Entregas Extremas (&gt; 45 min)</th>
                <th rowspan="2" style="border-left: 2px solid var(--border-color); text-align: center; width: 90px; vertical-align: bottom;">Evolução</th>
            </tr>
            <tr>
                <th class="text-center" style="border-left: 2px solid var(--border-color); background: #f1f5f9; font-weight: 800;">${acumTitle}</th>
        `;
        weeks.forEach(w => {
            theadHtml += `<th class="text-center">Sem. ${w}</th>`;
        });
        theadHtml += `<th class="text-center" style="border-left: 2px solid var(--border-color); background: #f1f5f9; font-weight: 800;">${acumTitle}</th>`;
        weeks.forEach(w => {
            theadHtml += `<th class="text-center">Sem. ${w}</th>`;
        });
        theadHtml += `</tr>`;
        tableAdt.querySelector('thead').innerHTML = theadHtml;

        const acumMap = {};
        adtAcum.forEach(r => { acumMap[r.storeId] = r; });

        const weeksMap = {};
        weeks.forEach(w => {
            weeksMap[w] = {};
            (adtWeeks[w] || []).forEach(r => { weeksMap[w][r.storeId] = r; });
        });

        const rowsData = [];
        storeIds.forEach(sid => {
            const st = rawData.stores[sid] || { name: `Loja ${sid}`, consultant: 'N/D', franchisee: 'N/D', type: 'F' };
            const ac = acumMap[sid];

            // Verifica se a loja tem algum pedido no período
            const hasDataInWeeks = weeks.some(w => weeksMap[w][sid] && weeksMap[w][sid].orders > 0);
            const hasDataInAcum = ac && ac.orders > 0;
            if (!hasDataInWeeks && !hasDataInAcum) return;

            const acAdt = ac ? ac.adt : 0;
            const acExt = ac ? ac.extreme : 0;

            rowsData.push({
                storeId: sid,
                store: st,
                acAdt: acAdt,
                acExt: acExt,
                ac: ac
            });
        });

        // Ordena por pior ADT acumulado no topo (igual painel oficial)
        rowsData.sort((a, b) => b.acAdt - a.acAdt);

        const tbody = tableAdt.querySelector('tbody');
        tbody.innerHTML = '';

        if (rowsData.length === 0) {
            tbody.innerHTML = `<tr><td colspan="${weeks.length * 2 + 4}" class="text-center" style="padding: 2rem;">Nenhuma loja encontrada com os filtros selecionados.</td></tr>`;
            return;
        }

        const fragment = document.createDocumentFragment();
        const sparklineQueue = [];

        rowsData.forEach(item => {
            const sid = item.storeId;
            const st = item.store;
            const ac = item.ac;

            const tr = document.createElement('tr');
            const badgeType = st.type === 'C'
                ? '<span class="badge-type badge-corp">Própria</span>'
                : '<span class="badge-type badge-fran">Franquia</span>';

            let rowHtml = `
                <td>
                    <div style="font-weight: 800; font-size: 0.95rem; display: flex; align-items: center;">
                        ${sid} - ${st.name} ${badgeType}
                    </div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 2px;">
                        <span>Consultor: <strong>${st.consultant || 'N/D'}</strong></span> | 
                        <span>Franqueado: <strong>${st.franchisee || 'N/D'}</strong></span>
                    </div>
                </td>
            `;

            // Bloco eADT
            rowHtml += `<td class="text-center" style="border-left: 2px solid var(--border-color); background: #fafafa; ${getAdtStyle(item.acAdt)}">${item.acAdt > 0 ? item.acAdt.toFixed(1) : '-'}</td>`;

            const adtHistory = [];
            weeks.forEach(w => {
                const wData = weeksMap[w][sid];
                const adt = wData ? wData.adt : 0;
                adtHistory.push(adt > 0 ? adt : null);
                rowHtml += `<td class="text-center" style="${getAdtStyle(adt)}">${adt > 0 ? adt.toFixed(1) : '-'}</td>`;
            });

            // Bloco Extremos
            rowHtml += `<td class="text-center" style="border-left: 2px solid var(--border-color); background: #fafafa; ${getExtremeStyle(item.acExt)}">${item.ac ? (item.acExt * 100).toFixed(1) + '%' : '-'}</td>`;

            weeks.forEach(w => {
                const wData = weeksMap[w][sid];
                const ext = wData ? (wData.extreme * 100) : 0;
                rowHtml += `<td class="text-center" style="${getExtremeStyle(wData ? wData.extreme : 0)}">${wData && wData.orders > 0 ? ext.toFixed(1) + '%' : '-'}</td>`;
            });

            // Coluna Sparkline
            rowHtml += `<td class="text-center" style="border-left: 2px solid var(--border-color); padding: 2px 8px; position: relative;">
                <canvas class="sparkline-canvas" width="80" height="28" style="width: 80px; height: 28px; display: block; margin: 0 auto;"></canvas>
            </td>`;

            tr.innerHTML = rowHtml;
            fragment.appendChild(tr);

            sparklineQueue.push({
                tr: tr,
                values: adtHistory
            });
        });

        tbody.appendChild(fragment);

        requestAnimationFrame(() => {
            sparklineQueue.forEach(item => {
                const canvas = item.tr.querySelector('.sparkline-canvas');
                drawSparkline(canvas, item.values, true);
            });
        });
    }

    // -------------------------------------------------------------
    // RENDERIZAÇÃO DA TABELA DE SERVICE EXCEPTIONS
    // -------------------------------------------------------------
    function renderExceptionsTable(storeIds) {
        const weeks = rawData.weeks || [];
        const excWeeks = rawData.exceptions.weeks || {};
        const excAcum = rawData.exceptions.acumulado || [];
        const acumTitle = rawData.acumuladoTitle || 'Acumulado';

        let theadHtml = `
            <tr>
                <th style="min-width: 240px;">Loja</th>
                <th class="text-center" style="border-left: 2px solid var(--border-color); background: #f1f5f9; font-weight: 800;">Except. ${acumTitle}</th>
        `;
        weeks.forEach(w => {
            theadHtml += `<th class="text-center">Sem. ${w}</th>`;
        });
        theadHtml += `<th class="text-center" style="border-left: 2px solid var(--border-color); width: 90px;">Evolução</th></tr>`;
        tableExc.querySelector('thead').innerHTML = theadHtml;

        const acumMap = {};
        excAcum.forEach(r => { acumMap[r.storeId] = r; });

        const weeksMap = {};
        weeks.forEach(w => {
            weeksMap[w] = {};
            (excWeeks[w] || []).forEach(r => { weeksMap[w][r.storeId] = r; });
        });

        const rowsData = [];
        storeIds.forEach(sid => {
            const st = rawData.stores[sid] || { name: `Loja ${sid}`, consultant: 'N/D', franchisee: 'N/D', type: 'F' };
            const ac = acumMap[sid];

            const hasDataInWeeks = weeks.some(w => weeksMap[w][sid] && weeksMap[w][sid].totalOrders > 0);
            const hasDataInAcum = ac && ac.totalOrders > 0;
            if (!hasDataInWeeks && !hasDataInAcum) return;

            const acExc = ac ? ac.exceptions : 0;

            rowsData.push({
                storeId: sid,
                store: st,
                acExc: acExc,
                ac: ac
            });
        });

        // Ordena por pior % de exceção no topo
        rowsData.sort((a, b) => b.acExc - a.acExc);

        const tbody = tableExc.querySelector('tbody');
        tbody.innerHTML = '';

        if (rowsData.length === 0) {
            tbody.innerHTML = `<tr><td colspan="${weeks.length + 3}" class="text-center" style="padding: 2rem;">Nenhuma loja encontrada com os filtros selecionados.</td></tr>`;
            return;
        }

        const fragment = document.createDocumentFragment();
        const sparklineQueue = [];

        rowsData.forEach(item => {
            const sid = item.storeId;
            const st = item.store;
            const ac = item.ac;

            const tr = document.createElement('tr');
            const badgeType = st.type === 'C'
                ? '<span class="badge-type badge-corp">Própria</span>'
                : '<span class="badge-type badge-fran">Franquia</span>';

            let rowHtml = `
                <td>
                    <div style="font-weight: 800; font-size: 0.95rem; display: flex; align-items: center;">
                        ${sid} - ${st.name} ${badgeType}
                    </div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 2px;">
                        <span>Consultor: <strong>${st.consultant || 'N/D'}</strong></span> | 
                        <span>Franqueado: <strong>${st.franchisee || 'N/D'}</strong></span>
                    </div>
                </td>
            `;

            const acExc = ac ? (ac.exceptions * 100) : 0;
            const acTip = ac ? `${ac.exceptionsCount || 0} exceções em ${ac.delvOrders || 0} pedidos delivery` : '';
            rowHtml += `<td class="text-center" title="${acTip}" style="border-left: 2px solid var(--border-color); background: #fafafa; ${getExceptionStyle(ac ? ac.exceptions : 0)}">${ac ? acExc.toFixed(1) + '%' : '-'}</td>`;

            const excHistory = [];
            weeks.forEach(w => {
                const wData = weeksMap[w][sid];
                const exc = wData ? (wData.exceptions * 100) : 0;
                const tip = wData ? `${wData.exceptionsCount || 0} exceções em ${wData.delvOrders || 0} pedidos delivery` : '';
                excHistory.push(wData && wData.delvOrders > 0 ? exc : null);
                rowHtml += `<td class="text-center" title="${tip}" style="${getExceptionStyle(wData ? wData.exceptions : 0)}">${wData && wData.delvOrders > 0 ? exc.toFixed(1) + '%' : '-'}</td>`;
            });

            rowHtml += `<td class="text-center" style="border-left: 2px solid var(--border-color); padding: 2px 8px; position: relative;">
                <canvas class="sparkline-canvas" width="80" height="28" style="width: 80px; height: 28px; display: block; margin: 0 auto;"></canvas>
            </td>`;

            tr.innerHTML = rowHtml;
            fragment.appendChild(tr);

            sparklineQueue.push({
                tr: tr,
                values: excHistory
            });
        });

        tbody.appendChild(fragment);

        requestAnimationFrame(() => {
            sparklineQueue.forEach(item => {
                const canvas = item.tr.querySelector('.sparkline-canvas');
                drawSparkline(canvas, item.values, true);
            });
        });
    }

    // -------------------------------------------------------------
    // RENDERIZAÇÃO DA TABELA DE ANÁLISE DE RISCO
    // -------------------------------------------------------------
    function renderRiskTable(storeIds) {
        const weeks = rawData.weeks || [];
        const latestWeek = weeks[weeks.length - 1]; // '07 a 13'
        const adtLatest = rawData.adt.weeks[latestWeek] || [];
        const excLatest = rawData.exceptions.weeks[latestWeek] || [];

        const adtMap = {};
        adtLatest.forEach(r => { adtMap[r.storeId] = r; });
        const excMap = {};
        excLatest.forEach(r => { excMap[r.storeId] = r; });

        tbodyRisk.innerHTML = '';
        const riskStores = [];

        storeIds.forEach(sid => {
            const a = adtMap[sid];
            const e = excMap[sid];
            const adt = a ? a.adt : 0;
            const ext = a ? (a.extreme * 100) : 0;
            const exc = e ? (e.exceptions * 100) : 0;

            const triggers = [];
            if (adt >= 40) triggers.push(`eADT Crítico (${adt.toFixed(1)}m)`);
            if (ext >= 10) triggers.push(`Extremos Altos (${ext.toFixed(1)}%)`);
            if (exc >= 25) triggers.push(`Exceções Altas (${exc.toFixed(1)}%)`);

            if (triggers.length > 0) {
                riskStores.push({
                    storeId: sid,
                    adt,
                    ext,
                    exc,
                    triggers
                });
            }
        });

        if (riskStores.length === 0) {
            tbodyRisk.innerHTML = `<tr><td colspan="8" class="text-center" style="padding: 2rem; color: var(--success-color); font-weight: 700;">Nenhuma loja em alerta crítico na semana ${latestWeek}!</td></tr>`;
            return;
        }

        riskStores.sort((x, y) => (y.triggers.length - x.triggers.length) || (y.adt - x.adt));

        riskStores.forEach(item => {
            const sid = item.storeId;
            const st = rawData.stores[sid] || { name: `Loja ${sid}`, consultant: 'N/D', franchisee: 'N/D', type: 'F' };
            const tr = document.createElement('tr');

            tr.innerHTML = `
                <td><strong>${sid}</strong> - ${st.name}</td>
                <td><span class="badge-type ${st.type === 'C' ? 'badge-corp' : 'badge-fran'}">${st.type === 'C' ? 'Própria' : 'Franquia'}</span></td>
                <td>${st.consultant || 'N/D'}</td>
                <td>${st.franchisee || 'N/D'}</td>
                <td class="text-center" style="${getAdtStyle(item.adt)}">${item.adt > 0 ? item.adt.toFixed(1) + ' min' : '-'}</td>
                <td class="text-center" style="${getExtremeStyle(item.ext / 100)}">${item.ext.toFixed(1)}%</td>
                <td class="text-center" style="${getExceptionStyle(item.exc / 100)}">${item.exc.toFixed(1)}%</td>
                <td>
                    ${item.triggers.map(t => `<span class="risk-trigger">${t}</span>`).join(' ')}
                </td>
            `;
            tbodyRisk.appendChild(tr);
        });
    }

    // -------------------------------------------------------------
    // RENDERIZAÇÃO DA TABELA DE AUDITORIA DE BACKFILL
    // -------------------------------------------------------------
    function renderBackfillTable(storeIds) {
        tbodyBackfill.innerHTML = '';

        const weeks = rawData.weeks || [];
        const adtWeeks = rawData.adt.weeks || {};

        const backfillItems = [];
        storeIds.forEach(sid => {
            let activeWeeks = 0;
            weeks.forEach(w => {
                const list = adtWeeks[w] || [];
                const found = list.find(x => x.storeId === sid && x.orders > 0);
                if (found) activeWeeks++;
            });

            if (activeWeeks > 0 && activeWeeks < weeks.length) {
                const st = rawData.stores[sid] || { name: `Loja ${sid}`, consultant: 'N/D', type: 'F' };
                backfillItems.push({
                    storeId: sid,
                    name: st.name,
                    type: st.type,
                    consultant: st.consultant,
                    missingWeeks: weeks.length - activeWeeks
                });
            }
        });

        if (backfillItems.length === 0) {
            tbodyBackfill.innerHTML = `<tr><td colspan="6" class="text-center" style="padding: 2rem; color: var(--success-color); font-weight: 700;">Todas as lojas selecionadas operaram com dados completos em todas as semanas!</td></tr>`;
            return;
        }

        backfillItems.sort((a, b) => b.missingWeeks - a.missingWeeks);

        backfillItems.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${item.storeId}</strong> - ${item.name}</td>
                <td><span class="badge-type ${item.type === 'C' ? 'badge-corp' : 'badge-fran'}">${item.type === 'C' ? 'Própria' : 'Franquia'}</span></td>
                <td>${item.consultant || 'N/D'}</td>
                <td class="text-center"><span style="color: var(--warning-color); font-weight: 800;">${item.missingWeeks} semana(s) incompleta(s)</span></td>
                <td><span style="font-size: 0.8rem; color: var(--text-secondary);">Subida tardia no PWR ou fechamento temporário em dias pontuais</span></td>
                <td><span class="badge" style="background-color: #dbeafe; color: #1e40af; font-weight: 700;">Backfill Monitorado</span></td>
            `;
            tbodyBackfill.appendChild(tr);
        });
    }

    async function exportToPng() {
        const area = document.getElementById('capture-area');
        if (!area) return;
        try {
            syncTimeEl.textContent = 'Gerando imagem...';
            const canvas = await html2canvas(area, {
                scale: 2,
                useCORS: true,
                backgroundColor: '#f4f6f9'
            });
            const link = document.createElement('a');
            link.download = `Dominos_Performance_PWR_${new Date().toISOString().slice(0, 10)}.png`;
            link.href = canvas.toDataURL('image/png');
            link.click();
            syncTimeEl.textContent = `Atualizado: ${rawData.updatedAt || 'Hoje'}`;
        } catch (err) {
            console.error("Erro ao exportar PNG:", err);
            alert("Não foi possível gerar a imagem.");
            syncTimeEl.textContent = `Atualizado: ${rawData.updatedAt || 'Hoje'}`;
        }
    }

    loadData();
});
