// Domino's Pizza Performance PWR Dashboard Logic - Evolução de Períodos
document.addEventListener('DOMContentLoaded', () => {
    let rawData = null;
    let activeTab = 'semanal';

    // Elementos DOM
    const syncTimeEl = document.getElementById('sync-time');
    const consultantSelect = document.getElementById('filter-consultant');
    const franchiseeSelect = document.getElementById('filter-franchisee');
    const searchInput = document.getElementById('search-store');

    // Helper para retornar a cor do ADT baseada nas faixas
    function getAdtStyle(adt) {
        if (!adt || adt <= 0) return '';
        if (adt < 25) return 'color: var(--success-color);'; // Verde (<25)
        if (adt < 30) return 'color: var(--warning-color);'; // Laranja claro (25-30)
        if (adt <= 40) return 'color: #f97316;'; // Laranja escuro / Coral (30-40)
        return 'color: var(--danger-color);'; // Vermelho (>40)
    }

    // Helper para retornar a cor de Extremes baseada nas faixas
    function getExtremeStyle(ext) {
        if (!ext || ext <= 0) return '';
        const pct = ext * 100;
        if (pct < 2) return 'color: var(--success-color);'; // Verde (<2%)
        if (pct < 10) return 'color: var(--warning-color);'; // Laranja claro (2%-10%)
        if (pct <= 20) return 'color: #f97316;'; // Laranja escuro / Coral (10%-20%)
        return 'color: var(--danger-color);'; // Vermelho (>20%)
    }

    // Helper para retornar a cor de Service Exceptions baseada nas faixas
    function getExceptionStyle(exc) {
        if (!exc || exc <= 0) return '';
        const pct = exc * 100;
        if (pct < 10) return 'color: var(--success-color);'; // Verde (<10%)
        if (pct < 25) return 'color: var(--warning-color);'; // Laranja claro (10%-25%)
        if (pct <= 40) return 'color: #f97316;'; // Laranja escuro / Coral (25%-40%)
        return 'color: var(--danger-color);'; // Vermelho (>40%)
    }

    // Elementos KPI ADT (Geral Acumulado)
    const kpiAdtVal = document.querySelector('#kpi-adt-avg .kpi-value');
    const kpiAdtCard = document.getElementById('kpi-adt-avg');
    const kpiExtremesVal = document.querySelector('#kpi-extremes-avg .kpi-value');
    const kpiExtremesCard = document.getElementById('kpi-extremes-avg');

    // Elementos KPI Exceptions (Geral Acumulado)
    const kpiExcVal = document.querySelector('#kpi-exceptions-avg .kpi-value');
    const kpiExcCard = document.getElementById('kpi-exceptions-avg');

    // Tabelas
    const tableAdt = document.getElementById('table-adt');
    const tableExc = document.getElementById('table-exceptions');

    // Carregar Dados
    async function loadData() {
        try {
            const response = await fetch('data.json');
            if (!response.ok) throw new Error('Não foi possível ler data.json');
            rawData = await response.json();
            
            initializeDashboard();
        } catch (error) {
            console.error('Erro ao ler base de dados:', error);
            syncTimeEl.textContent = 'Erro ao carregar dados';
        }
    }

    // Função utilitária para desenhar sparkline no background das linhas das tabelas
    function drawRowSparkline(tr, cells, values, canvasClass, maxValueDefault) {
        const firstCell = cells[0];
        const lastCell = cells[cells.length - 1];
        if (!firstCell || !lastCell) return;

        let canvas = firstCell.querySelector('.' + canvasClass);
        if (!canvas) {
            canvas = document.createElement('canvas');
            canvas.className = canvasClass;
            canvas.style.position = 'absolute';
            canvas.style.pointerEvents = 'none';
            canvas.style.zIndex = '1';
            firstCell.style.position = 'relative';
            firstCell.appendChild(canvas);
        }

        const firstRect = firstCell.getBoundingClientRect();
        const lastRect = lastCell.getBoundingClientRect();

        const width = lastRect.right - firstRect.left;
        const height = firstRect.height;

        canvas.style.left = '0px';
        canvas.style.width = width + 'px';
        canvas.style.height = height + 'px';
        canvas.style.top = '0px';

        canvas.width = width * 2;
        canvas.height = height * 2;

        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save();
        ctx.scale(2, 2);

        const points = [];
        const cellWidth = width / values.length;
        const maxValue = Math.max(maxValueDefault, ...values);

        values.forEach((val, i) => {
            const x = cellWidth * (i + 0.5);
            const padding = height * 0.15;
            const y = height - padding - ((val / maxValue) * (height - 2 * padding));
            points.push({ x, y });
        });

        let isImproving = true;
        if (values.length > 1) {
            isImproving = values[values.length - 1] <= values[0];
        }

        const lineColor = isImproving ? '#10b981' : '#ef4444';
        const fillGradStart = isImproving ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.08)';
        const fillGradEnd = isImproving ? 'rgba(16, 185, 129, 0.01)' : 'rgba(239, 68, 68, 0.01)';

        ctx.beginPath();
        ctx.moveTo(points[0].x, points[0].y);
        for (let i = 1; i < points.length; i++) {
            ctx.lineTo(points[i].x, points[i].y);
        }
        ctx.strokeStyle = lineColor;
        ctx.lineWidth = 2.5;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(points[0].x, points[0].y);
        for (let i = 1; i < points.length; i++) {
            ctx.lineTo(points[i].x, points[i].y);
        }
        ctx.lineTo(points[points.length - 1].x, height);
        ctx.lineTo(points[0].x, height);
        ctx.closePath();

        const grad = ctx.createLinearGradient(0, 0, 0, height);
        grad.addColorStop(0, fillGradStart);
        grad.addColorStop(1, fillGradEnd);
        ctx.fillStyle = grad;
        ctx.fill();
        ctx.restore();
    }

    // Função utilitária para desenhar sparkline no background dos cards de KPI
    function drawCardSparkline(cardId, canvasClass, values, maxValueDefault) {
        const card = document.getElementById(cardId);
        if (!card || values.length === 0) return;

        let canvas = card.querySelector('.' + canvasClass);
        if (!canvas) {
            canvas = document.createElement('canvas');
            canvas.className = canvasClass;
            canvas.style.position = 'absolute';
            canvas.style.top = '0';
            canvas.style.left = '0';
            canvas.style.width = '100%';
            canvas.style.height = '100%';
            canvas.style.pointerEvents = 'none';
            canvas.style.zIndex = '1';
            card.style.position = 'relative';
            card.appendChild(canvas);
        }

        const width = card.clientWidth;
        const height = card.clientHeight;
        canvas.width = width * 2;
        canvas.height = height * 2;
        canvas.style.width = width + 'px';
        canvas.style.height = height + 'px';

        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save();
        ctx.scale(2, 2);

        const points = [];
        const count = values.length;
        const stepX = width / (count > 1 ? (count - 1) : 1);
        const maxVal = Math.max(maxValueDefault, ...values);

        values.forEach((val, i) => {
            const x = stepX * i;
            const paddingY = height * 0.2;
            const y = height - paddingY - ((val / maxVal) * (height - 2 * paddingY));
            points.push({ x, y });
        });

        const cardIsImproving = values.length > 1 ? 
            values[values.length - 1] <= values[0] : 
            true;

        const lineColor = cardIsImproving ? '#10b981' : '#ef4444';
        const gradStart = cardIsImproving ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.08)';
        const gradEnd = cardIsImproving ? 'rgba(16, 185, 129, 0.00)' : 'rgba(239, 68, 68, 0.00)';

        ctx.beginPath();
        ctx.moveTo(points[0].x, points[0].y);
        for (let i = 1; i < points.length; i++) {
            ctx.lineTo(points[i].x, points[i].y);
        }
        ctx.strokeStyle = lineColor;
        ctx.lineWidth = 3;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(points[0].x, points[0].y);
        for (let i = 1; i < points.length; i++) {
            ctx.lineTo(points[i].x, points[i].y);
        }
        ctx.lineTo(width, height);
        ctx.lineTo(0, height);
        ctx.closePath();

        const grad = ctx.createLinearGradient(0, 0, 0, height);
        grad.addColorStop(0, gradStart);
        grad.addColorStop(1, gradEnd);
        ctx.fillStyle = grad;
        ctx.fill();
        ctx.restore();
    }

    // Inicializar filtros e carregar opções
    function initializeDashboard() {
        // Data de atualização
        if (rawData.updatedAt) {
            syncTimeEl.textContent = `Atualizado em: ${rawData.updatedAt}`;
        }

        // Popular Consultores
        const consultants = new Set();
        Object.values(rawData.stores).forEach(store => {
            const excludedIds = ['19680', '19707', '19733', '19792', '19964', '19967'];
            if (excludedIds.includes(store.id)) return;
            if (store.consultant) consultants.add(store.consultant.trim().toUpperCase());
        });

        // Ordenar e adicionar consultores
        Array.from(consultants).sort().forEach(c => {
            const opt = document.createElement('option');
            opt.value = c;
            opt.textContent = c;
            consultantSelect.appendChild(opt);
        });

        // Função para filtrar franqueados do consultor selecionado
        function updateFranchiseeSelect(selectedConsultant) {
            const currentFranchisee = franchiseeSelect.value;
            franchiseeSelect.innerHTML = '<option value="all">Todos os Franqueados</option>';
            
            const franchisees = new Set();
            Object.values(rawData.stores).forEach(store => {
                if (!store.franchisee) return;
                const excludedIds = ['19680', '19707', '19733', '19792', '19964', '19967'];
                if (excludedIds.includes(store.id)) return;
                
                const matchesConsultant = selectedConsultant === 'all' || 
                                          (store.consultant && store.consultant.trim().toUpperCase() === selectedConsultant);
                if (matchesConsultant) {
                    franchisees.add(store.franchisee.trim());
                }
            });

            Array.from(franchisees).sort().forEach(f => {
                const opt = document.createElement('option');
                opt.value = f;
                opt.textContent = f;
                franchiseeSelect.appendChild(opt);
            });

            if (franchisees.has(currentFranchisee)) {
                franchiseeSelect.value = currentFranchisee;
            } else {
                franchiseeSelect.value = 'all';
            }
        }

        // Inicializa o dropdown de franqueados
        updateFranchiseeSelect('all');

        // Configurar Event Listeners
        consultantSelect.addEventListener('change', () => {
            updateFranchiseeSelect(consultantSelect.value);
            render();
        });
        franchiseeSelect.addEventListener('change', render);
        searchInput.addEventListener('input', render);

        // Renderização Inicial
        render();

        // Configura as abas
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const tab = btn.getAttribute('data-tab');
                activeTab = tab;

                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                document.querySelectorAll(`.tab-content[data-view="${tab}"]`).forEach(c => c.classList.add('active'));

                render();
            });
        });
    }

    // Filtra e Renderiza tudo
    function render() {
        if (!rawData) return;

        const consultant = consultantSelect.value;
        const franchisee = franchiseeSelect.value;
        const search = searchInput.value.toLowerCase().trim();
        
        // Atualiza os títulos das seções com o nome do consultor
        const titleAdt = document.getElementById('title-adt');
        const titleExceptions = document.getElementById('title-exceptions');
        const consultantText = consultantSelect.options[consultantSelect.selectedIndex].text.toUpperCase();
        
        if (titleAdt) {
            titleAdt.textContent = consultant === 'all' ? 'Tempos de Entrega (ADT & Extremes)' : `Tempos de Entrega (ADT & Extremes) - ${consultantText}`;
        }
        if (titleExceptions) {
            titleExceptions.textContent = consultant === 'all' ? 'Service Exceptions' : `Service Exceptions - ${consultantText}`;
        }
        
        // IDs das lojas a serem excluídas (Blumenau, Joinville, Florianópolis Centro, Juiz de Fora 2, Itaipava, Pampulha)
        const excludedIds = ['19680', '19707', '19733', '19792', '19964', '19967'];

        // 1. Filtrar as lojas com base nos critérios de busca/filtros
        const filteredStoreIds = Object.keys(rawData.stores).filter(storeId => {
            if (excludedIds.includes(storeId)) return false;

            const store = rawData.stores[storeId];
            const matchConsultant = consultant === 'all' || (store.consultant && store.consultant.trim().toUpperCase() === consultant);
            const matchFranchisee = franchisee === 'all' || (store.franchisee && store.franchisee.trim() === franchisee);
            const matchSearch = !search || 
                                storeId.toLowerCase().includes(search) || 
                                store.name.toLowerCase().includes(search);
            return matchConsultant && matchFranchisee && matchSearch;
        });

        // Se a lista de lojas filtradas estiver vazia, mas houver lojas nas tabelas de dados que não foram mapeadas na aba "loja por consultor", podemos adicioná-las também caso correspondam à busca por ID
        // Para manter consistência, usamos as lojas mapeadas + lojas com dados existentes
        const allDataStoreIds = new Set([
            ...filteredStoreIds,
            ...((rawData.adt.acumulado || []).map(r => r.storeId)),
            ...((rawData.exceptions.acumulado || []).map(r => r.storeId))
        ]);

        const storesToShow = Array.from(allDataStoreIds).filter(storeId => {
            if (excludedIds.includes(storeId)) return false;

            const store = rawData.stores[storeId] || { name: `Loja ${storeId}`, consultant: 'N/D', franchisee: 'N/D' };
            const matchConsultant = consultant === 'all' || (store.consultant && store.consultant.trim().toUpperCase() === consultant);
            const matchFranchisee = franchisee === 'all' || (store.franchisee && store.franchisee.trim() === franchisee);
            const matchSearch = !search || 
                                storeId.toLowerCase().includes(search) || 
                                store.name.toLowerCase().includes(search);
            return matchConsultant && matchFranchisee && matchSearch;
        });

        // 2. Renderizar cabeçalhos e linhas
        renderAdtTable(storesToShow);
        renderExceptionsTable(storesToShow);
        renderMonthly(storesToShow);
        renderRiskAnalysis(storesToShow);
    }

    function renderAdtTable(storeIds) {
        const weeks = rawData.weeks || [];
        
        // Montar Cabeçalho da Tabela
        let headerHtml = `
            <tr>
                <th>Loja</th>
                <th class="text-center" style="border-left: 2px solid var(--border-color)">Acumulado</th>
        `;
        weeks.forEach(w => {
            headerHtml += `<th class="text-center">Sem. ${w}</th>`;
        });
        headerHtml += `<th class="text-center" style="border-left: 2px solid var(--border-color)">Acumulado</th>`;
        weeks.forEach(w => {
            headerHtml += `<th class="text-center">Sem. ${w}</th>`;
        });
        headerHtml += `</tr>`;
        tableAdt.querySelector('thead').innerHTML = headerHtml;

        // Mapear dados por loja para facilitar busca rápida
        const adtAcumMap = {};
        let totalOrders = 0;
        let sumAdtWeight = 0;
        let sumExtWeight = 0;

        (rawData.adt.acumulado || []).forEach(r => {
            adtAcumMap[r.storeId] = r;
        });

        const adtWeeksMap = {};
        weeks.forEach(w => {
            adtWeeksMap[w] = {};
            (rawData.adt.weeks[w] || []).forEach(r => {
                adtWeeksMap[w][r.storeId] = r;
            });
        });

        // Montar Linhas da Tabela
        const tbody = tableAdt.querySelector('tbody');
        tbody.innerHTML = '';

        const rowsData = [];

        storeIds.forEach(storeId => {
            const store = rawData.stores[storeId] || { name: `Loja ${storeId}`, consultant: 'N/D', franchisee: 'N/D' };
            const acum = adtAcumMap[storeId];
            
            // Só exibe se houver algum dado de ADT
            if (!acum && !weeks.some(w => adtWeeksMap[w][storeId])) return;

            const orders = acum ? (acum.orders || 0) : 0;
            const adtVal = acum ? (acum.adt || 0) : 0;
            const extVal = acum ? (acum.extreme || 0) : 0;

            if (storeIds.includes(storeId)) {
                totalOrders += orders;
                sumAdtWeight += adtVal * orders;
                sumExtWeight += extVal * orders;
            }

            rowsData.push({
                storeId,
                store,
                orders,
                adtVal,
                extVal,
                acum
            });
        });

        // Ordena lojas por pior ADT acumulado no topo
        rowsData.sort((a, b) => b.adtVal - a.adtVal);

        const groupAdtWeeklyAverages = [];
        const groupExtWeeklyAverages = [];
        weeks.forEach(w => {
            let weekTotalOrders = 0;
            let weekTotalAdtWeight = 0;
            let weekTotalExtWeight = 0;
            storeIds.forEach(storeId => {
                const store = rawData.stores[storeId];
                if (store) {
                    const wData = adtWeeksMap[w][storeId];
                    if (wData) {
                        weekTotalOrders += wData.orders || 0;
                        weekTotalAdtWeight += (wData.adt || 0) * (wData.orders || 0);
                        weekTotalExtWeight += (wData.extreme || 0) * (wData.orders || 0);
                    }
                }
            });
            const weekAvgAdt = weekTotalOrders > 0 ? (weekTotalAdtWeight / weekTotalOrders) : 0;
            const weekAvgExt = weekTotalOrders > 0 ? (weekTotalExtWeight / weekTotalOrders) : 0;
            groupAdtWeeklyAverages.push(weekAvgAdt);
            groupExtWeeklyAverages.push(weekAvgExt);
        });

        if (rowsData.length === 0) {
            tbody.innerHTML = `<tr><td colspan="${4 + (weeks.length * 2)}" class="text-center">Nenhuma loja com dados de ADT encontrada</td></tr>`;
        } else {
            rowsData.forEach(item => {
                const { storeId, store, orders, adtVal, extVal } = item;
                const tr = document.createElement('tr');

                // Célula ADT Acumulado
                const adtStyle = getAdtStyle(adtVal);
                const cleanStoreName = store.name.replace(/domino[s]?'?\s*/gi, '').trim();
                let html = `
                    <td>${cleanStoreName}</td>
                    <td class="text-center" style="border-left: 2px solid var(--border-color); font-weight: 700; ${adtStyle}">${adtVal > 0 ? adtVal.toFixed(2) : '--'}</td>
                `;

                // Células ADT Semanais
                const rowAdtVals = [];
                weeks.forEach(w => {
                    const wData = adtWeeksMap[w][storeId];
                    const wAdt = wData ? wData.adt : 0;
                    const wAdtStyle = getAdtStyle(wAdt);
                    rowAdtVals.push(wAdt);
                    html += `<td class="text-center adt-week-cell" data-value="${wAdt}" style="position: relative; z-index: 2; background: transparent; ${wAdtStyle}">${wAdt > 0 ? wAdt.toFixed(2) : '--'}</td>`;
                });

                // Célula Extremes Acumulado
                const extPct = extVal * 100;
                const extStyle = getExtremeStyle(extVal);
                html += `<td class="text-center" style="border-left: 2px solid var(--border-color); font-weight: 700; ${extStyle}">${extVal > 0 ? extPct.toFixed(2) + '%' : '--'}</td>`;

                // Células Extremes Semanais
                const rowExtVals = [];
                weeks.forEach(w => {
                    const wData = adtWeeksMap[w][storeId];
                    const wExt = wData ? wData.extreme : 0;
                    const wExtPct = wExt * 100;
                    const wExtStyle = getExtremeStyle(wExt);
                    rowExtVals.push(wExt);
                    html += `<td class="text-center ext-week-cell" data-value="${wExt}" style="position: relative; z-index: 2; background: transparent; ${wExtStyle}">${wExt > 0 ? wExtPct.toFixed(2) + '%' : '--'}</td>`;
                });

                tr.setAttribute('data-adt-values', JSON.stringify(rowAdtVals));
                tr.setAttribute('data-ext-values', JSON.stringify(rowExtVals));
                tr.innerHTML = html;
                tbody.appendChild(tr);
            });

            // Renderizar Sparklines nas Linhas (ADT e Extremes independentes)
            requestAnimationFrame(() => {
                const rows = tbody.querySelectorAll('tr');
                rows.forEach(tr => {
                    // ADT Sparkline
                    const adtValsAttr = tr.getAttribute('data-adt-values');
                    if (adtValsAttr) {
                        const adtValues = JSON.parse(adtValsAttr);
                        const adtCells = Array.from(tr.querySelectorAll('.adt-week-cell'));
                        if (adtValues.length > 0 && adtCells.length > 0) {
                            drawRowSparkline(tr, adtCells, adtValues, 'row-sparkline-adt', 25.0);
                        }
                    }

                    // Extremes Sparkline
                    const extValsAttr = tr.getAttribute('data-ext-values');
                    if (extValsAttr) {
                        const extValues = JSON.parse(extValsAttr);
                        const extCells = Array.from(tr.querySelectorAll('.ext-week-cell'));
                        if (extValues.length > 0 && extCells.length > 0) {
                            drawRowSparkline(tr, extCells, extValues, 'row-sparkline-ext', 0.02);
                        }
                    }
                });
            });
        }

        // Atualizar KPIs Globais
        const avgAdt = totalOrders > 0 ? (sumAdtWeight / totalOrders) : 0;
        const avgExt = totalOrders > 0 ? (sumExtWeight / totalOrders) : 0;

        kpiAdtVal.textContent = totalOrders > 0 ? `${avgAdt.toFixed(2)} min` : '--';
        kpiExtremesVal.textContent = totalOrders > 0 ? `${(avgExt * 100).toFixed(2)}%` : '--';

        kpiAdtCard.className = 'kpi-card ' + (avgAdt < 25 ? 'kpi-success' : (avgAdt < 30 ? 'kpi-warning' : 'kpi-danger'));
        kpiExtremesCard.className = 'kpi-card ' + (avgExt < 0.02 ? 'kpi-success' : (avgExt < 0.10 ? 'kpi-warning' : 'kpi-danger'));

        // Renderizar Sparklines nos Cards de Destaque
        requestAnimationFrame(() => {
            drawCardSparkline('kpi-adt-avg', 'card-sparkline-adt', groupAdtWeeklyAverages, 25.0);
            drawCardSparkline('kpi-extremes-avg', 'card-sparkline-ext', groupExtWeeklyAverages, 0.02);
        });

        // Renderizar Lojas Críticas (ADT > 40 e Extremes > 20%)
        const criticalAdtList = document.getElementById('kpi-adt-critical');
        const criticalExtList = document.getElementById('kpi-extremes-critical');

        // Filtrar e Ordenar
        const criticalAdt = rowsData.filter(r => r.adtVal > 40).sort((a, b) => b.adtVal - a.adtVal);
        const criticalExt = rowsData.filter(r => r.extVal > 0.20).sort((a, b) => b.extVal - a.extVal);

        if (criticalAdt.length > 0) {
            let html = '';
            criticalAdt.forEach(r => {
                const cleanName = r.store.name.replace(/domino[s]?'?\s*/gi, '').trim();
                html += `
                    <div class="kpi-critical-item">
                        <span>${cleanName}</span>
                        <span>${r.adtVal.toFixed(1)}m</span>
                    </div>
                `;
            });
            criticalAdtList.innerHTML = html;
            criticalAdtList.style.display = 'flex';
        } else {
            criticalAdtList.innerHTML = '';
            criticalAdtList.style.display = 'none';
        }

        if (criticalExt.length > 0) {
            let html = '';
            criticalExt.forEach(r => {
                const cleanName = r.store.name.replace(/domino[s]?'?\s*/gi, '').trim();
                html += `
                    <div class="kpi-critical-item">
                        <span>${cleanName}</span>
                        <span>${(r.extVal * 100).toFixed(1)}%</span>
                    </div>
                `;
            });
            criticalExtList.innerHTML = html;
            criticalExtList.style.display = 'flex';
        } else {
            criticalExtList.innerHTML = '';
            criticalExtList.style.display = 'none';
        }
    }

    function renderExceptionsTable(storeIds) {
        const weeks = rawData.weeks || [];
        
        // Montar Cabeçalho da Tabela
        let headerHtml = `
            <tr>
                <th>Loja</th>
                <th class="text-center" style="border-left: 2px solid var(--border-color)">Except. Acum.</th>
        `;
        weeks.forEach(w => {
            headerHtml += `<th class="text-center">Sem. ${w}</th>`;
        });
        headerHtml += `</tr>`;
        tableExc.querySelector('thead').innerHTML = headerHtml;

        // Mapear dados
        const excAcumMap = {};
        let totalDelv = 0;
        let totalExcCount = 0;

        (rawData.exceptions.acumulado || []).forEach(r => {
            excAcumMap[r.storeId] = r;
        });

        const excWeeksMap = {};
        weeks.forEach(w => {
            excWeeksMap[w] = {};
            (rawData.exceptions.weeks[w] || []).forEach(r => {
                excWeeksMap[w][r.storeId] = r;
            });
        });

        // Montar Linhas da Tabela
        const tbody = tableExc.querySelector('tbody');
        tbody.innerHTML = '';

        const rowsData = [];

        storeIds.forEach(storeId => {
            const store = rawData.stores[storeId] || { name: `Loja ${storeId}`, consultant: 'N/D', franchisee: 'N/D' };
            const acum = excAcumMap[storeId];

            if (!acum && !weeks.some(w => excWeeksMap[w][storeId])) return;

            const delvOrders = acum ? (acum.delvOrders || 0) : 0;
            const excCount = acum ? (acum.exceptionsCount || 0) : 0;
            const excPct = acum ? (acum.exceptions || 0) : 0;

            if (storeIds.includes(storeId)) {
                totalDelv += delvOrders;
                totalExcCount += excCount;
            }

            rowsData.push({
                storeId,
                store,
                delvOrders,
                excCount,
                excPct,
                acum
            });
        });

        // Ordena por pior % de exceção acumulada
        rowsData.sort((a, b) => b.excPct - a.excPct);

        const groupWeeklyAverages = [];
        weeks.forEach(w => {
            let weekTotalDelv = 0;
            let weekTotalExc = 0;
            storeIds.forEach(storeId => {
                const store = rawData.stores[storeId];
                if (store) {
                    const wData = excWeeksMap[w][storeId];
                    if (wData) {
                        weekTotalDelv += wData.delvOrders || 0;
                        weekTotalExc += wData.exceptionsCount || 0;
                    }
                }
            });
            const weekAvg = weekTotalDelv > 0 ? (weekTotalExc / weekTotalDelv) : 0;
            groupWeeklyAverages.push(weekAvg);
        });

        if (rowsData.length === 0) {
            tbody.innerHTML = `<tr><td colspan="${5 + weeks.length}" class="text-center">Nenhuma loja com dados de Exceções encontrada</td></tr>`;
        } else {
            rowsData.forEach(item => {
                const { storeId, store, delvOrders, excCount, excPct } = item;
                const tr = document.createElement('tr');

                const pctVal = excPct * 100;
                const excStyle = getExceptionStyle(excPct);

                const cleanStoreName = store.name.replace(/domino[s]?'?\s*/gi, '').trim();
                let html = `
                    <td>${cleanStoreName}</td>
                    <td class="text-center" style="border-left: 2px solid var(--border-color); font-weight: 700; ${excStyle}">${excPct > 0 ? pctVal.toFixed(2) + '%' : '--'}</td>
                `;

                // Coleta valores semanais para o sparkline da linha
                const weekVals = [];

                // Células Exceptions Semanais
                weeks.forEach(w => {
                    const wData = excWeeksMap[w][storeId];
                    const wExc = wData ? wData.exceptions : 0;
                    const wExcPct = wExc * 100;
                    const wExcStyle = getExceptionStyle(wExc);
                    weekVals.push(wExc);
                    html += `<td class="text-center week-cell" data-value="${wExc}" style="position: relative; z-index: 2; background: transparent; ${wExcStyle}">${wExc > 0 ? wExcPct.toFixed(2) + '%' : '--'}</td>`;
                });

                tr.setAttribute('data-weeks-values', JSON.stringify(weekVals));
                tr.innerHTML = html;
                tbody.appendChild(tr);
            });

            // Renderizar Sparklines das linhas
            requestAnimationFrame(() => {
                const rows = tbody.querySelectorAll('tr');
                rows.forEach(tr => {
                    const weekValsAttr = tr.getAttribute('data-weeks-values');
                    if (!weekValsAttr) return;
                    const values = JSON.parse(weekValsAttr);
                    if (values.length === 0) return;

                    const weekCells = Array.from(tr.querySelectorAll('.week-cell'));
                    if (weekCells.length === 0) return;

                    const firstCell = weekCells[0];
                    const lastCell = weekCells[weekCells.length - 1];

                    let canvas = firstCell.querySelector('.row-sparkline');
                    if (!canvas) {
                        canvas = document.createElement('canvas');
                        canvas.className = 'row-sparkline';
                        canvas.style.position = 'absolute';
                        canvas.style.pointerEvents = 'none';
                        canvas.style.zIndex = '1';
                        firstCell.style.position = 'relative';
                        firstCell.appendChild(canvas);
                    }

                    const firstRect = firstCell.getBoundingClientRect();
                    const lastRect = lastCell.getBoundingClientRect();

                    const width = lastRect.right - firstRect.left;
                    const height = firstRect.height;

                    canvas.style.left = '0px';
                    canvas.style.width = width + 'px';
                    canvas.style.height = height + 'px';
                    canvas.style.top = '0px';

                    canvas.width = width * 2;
                    canvas.height = height * 2;

                    const ctx = canvas.getContext('2d');
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    ctx.scale(2, 2);

                    const points = [];
                    const cellWidth = width / values.length;
                    const maxValue = Math.max(0.40, ...values);

                    values.forEach((val, i) => {
                        const x = cellWidth * (i + 0.5);
                        const padding = height * 0.15;
                        const y = height - padding - ((val / maxValue) * (height - 2 * padding));
                        points.push({ x, y });
                    });

                    let isImproving = true;
                    if (values.length > 1) {
                        isImproving = values[values.length - 1] <= values[0];
                    } else {
                        isImproving = values[0] < 0.10;
                    }

                    const lineColor = isImproving ? '#10b981' : '#ef4444';
                    const fillGradStart = isImproving ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.08)';
                    const fillGradEnd = isImproving ? 'rgba(16, 185, 129, 0.01)' : 'rgba(239, 68, 68, 0.01)';

                    ctx.beginPath();
                    ctx.moveTo(points[0].x, points[0].y);
                    for (let i = 1; i < points.length; i++) {
                        ctx.lineTo(points[i].x, points[i].y);
                    }
                    ctx.strokeStyle = lineColor;
                    ctx.lineWidth = 2.5;
                    ctx.lineCap = 'round';
                    ctx.lineJoin = 'round';
                    ctx.stroke();

                    // Gradiente de fundo
                    ctx.beginPath();
                    ctx.moveTo(points[0].x, points[0].y);
                    for (let i = 1; i < points.length; i++) {
                        ctx.lineTo(points[i].x, points[i].y);
                    }
                    ctx.lineTo(points[points.length - 1].x, height);
                    ctx.lineTo(points[0].x, height);
                    ctx.closePath();

                    const grad = ctx.createLinearGradient(0, 0, 0, height);
                    grad.addColorStop(0, fillGradStart);
                    grad.addColorStop(1, fillGradEnd);
                    ctx.fillStyle = grad;
                    ctx.fill();
                });
            });
        }

        // Atualizar KPIs Globais
        const avgExc = totalDelv > 0 ? (totalExcCount / totalDelv) : 0;

        kpiExcVal.textContent = totalDelv > 0 ? `${(avgExc * 100).toFixed(2)}%` : '--';

        kpiExcCard.className = 'kpi-card ' + (avgExc < 0.10 ? 'kpi-success' : (avgExc < 0.25 ? 'kpi-warning' : 'kpi-danger'));

        // Desenhar Sparkline no Card de Destaque
        requestAnimationFrame(() => {
            const card = document.getElementById('kpi-exceptions-avg');
            if (!card || groupWeeklyAverages.length === 0) return;

            let canvas = card.querySelector('.card-sparkline');
            if (!canvas) {
                canvas = document.createElement('canvas');
                canvas.className = 'card-sparkline';
                canvas.style.position = 'absolute';
                canvas.style.top = '0';
                canvas.style.left = '0';
                canvas.style.width = '100%';
                canvas.style.height = '100%';
                canvas.style.pointerEvents = 'none';
                canvas.style.zIndex = '1';
                card.style.position = 'relative';
                card.appendChild(canvas);
            }

            const width = card.clientWidth;
            const height = card.clientHeight;
            canvas.width = width * 2;
            canvas.height = height * 2;
            canvas.style.width = width + 'px';
            canvas.style.height = height + 'px';

            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.scale(2, 2);

            const points = [];
            const count = groupWeeklyAverages.length;
            const stepX = width / (count > 1 ? (count - 1) : 1);
            
            const maxVal = Math.max(0.20, ...groupWeeklyAverages);

            groupWeeklyAverages.forEach((val, i) => {
                const x = stepX * i;
                const paddingY = height * 0.2;
                const y = height - paddingY - ((val / maxVal) * (height - 2 * paddingY));
                points.push({ x, y });
            });

            const cardIsImproving = groupWeeklyAverages.length > 1 ? 
                groupWeeklyAverages[groupWeeklyAverages.length - 1] <= groupWeeklyAverages[0] : 
                (avgExc < 0.10);

            const lineColor = cardIsImproving ? '#10b981' : '#ef4444';
            const gradStart = cardIsImproving ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.08)';
            const gradEnd = cardIsImproving ? 'rgba(16, 185, 129, 0.00)' : 'rgba(239, 68, 68, 0.00)';

            ctx.beginPath();
            ctx.moveTo(points[0].x, points[0].y);
            for (let i = 1; i < points.length; i++) {
                ctx.lineTo(points[i].x, points[i].y);
            }
            ctx.strokeStyle = lineColor;
            ctx.lineWidth = 3;
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(points[0].x, points[0].y);
            for (let i = 1; i < points.length; i++) {
                ctx.lineTo(points[i].x, points[i].y);
            }
            ctx.lineTo(width, height);
            ctx.lineTo(0, height);
            ctx.closePath();

            const grad = ctx.createLinearGradient(0, 0, 0, height);
            grad.addColorStop(0, gradStart);
            grad.addColorStop(1, gradEnd);
            ctx.fillStyle = grad;
            ctx.fill();
        });

        // Renderizar Lojas Críticas (Exceptions > 50%)
        const criticalExcList = document.getElementById('kpi-exceptions-critical');
        const criticalExc = rowsData.filter(r => r.excPct > 0.50).sort((a, b) => b.excPct - a.excPct);

        if (criticalExc.length > 0) {
            let html = '';
            criticalExc.forEach(r => {
                const cleanName = r.store.name.replace(/domino[s]?'?\s*/gi, '').trim();
                const pctVal = r.excPct * 100;
                html += `
                    <div class="kpi-critical-item">
                        <span>${cleanName}</span>
                        <span>${pctVal.toFixed(1)}%</span>
                    </div>
                `;
            });
            criticalExcList.innerHTML = html;
            criticalExcList.style.display = 'flex';
        } else {
            criticalExcList.innerHTML = '';
            criticalExcList.style.display = 'none';
        }
    }

    // ==========================================
    // RENDERIZAÇÃO MENSAL — 3 TABELAS INDEPENDENTES
    // ==========================================

    function renderMonthly(storeIds) {
        const monthly = rawData.monthly || { adt: {}, exceptions: {}, months: [] };
        const months  = monthly.months || [];
        renderMonthlyAdtTable(storeIds, monthly, months);
        renderMonthlyExtremesTable(storeIds, monthly, months);
        renderMonthlyExceptionsTable(storeIds, monthly, months);
    }

    const MONTH_LABELS = {
        jan: 'Jan', fev: 'Fev', mar: 'Mar', abr: 'Abr',
        mai: 'Mai', jun: 'Jun', jul: 'Jul', ago: 'Ago',
        set: 'Set', out: 'Out', nov: 'Nov', dez: 'Dez'
    };

    const MONTHLY_EMPTY_HTML = `
        <tr><td>
            <div class="monthly-empty">
                <div class="empty-icon">📂</div>
                <h3>Nenhum dado mensal encontrado</h3>
                <p>Coloque os arquivos consolidados mensais na pasta<br>
                <code>pwr_reports_mensal/</code> e reinicie o script.</p>
            </div>
        </td></tr>`;

    function buildMonthlyMaps(dataArray, months) {
        const maps = {};
        months.forEach(m => {
            maps[m] = {};
            (dataArray[m] || []).forEach(r => { maps[m][r.storeId] = r; });
        });
        return maps;
    }

    function buildMonthlyHeader(months, extraCols = []) {
        let h = '<tr><th>Loja</th>';
        months.forEach(m => { h += `<th class="text-center">${MONTH_LABELS[m] || m}</th>`; });
        extraCols.forEach(c => { h += `<th class="text-center">${c}</th>`; });
        return h + '</tr>';
    }

    // ── TABELA 1: ADT ──────────────────────────────────────────────
    function renderMonthlyAdtTable(storeIds, monthly, months) {
        const table    = document.getElementById('table-adt-mensal');
        const kpiVal   = document.querySelector('#kpi-adt-avg-mensal .kpi-value');
        const kpiCard  = document.getElementById('kpi-adt-avg-mensal');
        const titleEl  = document.getElementById('title-adt-mensal');
        const consultant = consultantSelect.value;
        const consultantText = consultantSelect.options[consultantSelect.selectedIndex].text.toUpperCase();

        if (titleEl) titleEl.textContent = consultant === 'all'
            ? 'ADT Mensal (Tempo de Entrega)'
            : 'ADT Mensal — ' + consultantText;

        if (months.length === 0) {
            table.querySelector('thead').innerHTML = '';
            table.querySelector('tbody').innerHTML = MONTHLY_EMPTY_HTML;
            if (kpiVal) kpiVal.textContent = '--';
            return;
        }

        table.querySelector('thead').innerHTML = buildMonthlyHeader(months);

        const maps = buildMonthlyMaps(monthly.adt || {}, months);
        const rowsData = [];
        let totalOrders = 0, sumAdtW = 0;

        storeIds.forEach(storeId => {
            const store = rawData.stores[storeId] || { name: 'Loja ' + storeId };
            if (!months.some(m => maps[m][storeId])) return;
            let lastAdt = 0, lastOrders = 0;
            for (let i = months.length - 1; i >= 0; i--) {
                const d = maps[months[i]][storeId];
                if (d) { lastAdt = d.adt || 0; lastOrders = d.orders || 0; break; }
            }
            totalOrders += lastOrders;
            sumAdtW     += lastAdt * lastOrders;
            rowsData.push({ storeId, store, lastAdt, lastOrders });
        });

        rowsData.sort((a, b) => b.lastAdt - a.lastAdt);

        const groupAvgs = months.map(m => {
            let mo = 0, sa = 0;
            storeIds.forEach(sid => {
                const d = maps[m][sid];
                if (d) { mo += d.orders || 0; sa += (d.adt || 0) * (d.orders || 0); }
            });
            return mo > 0 ? sa / mo : 0;
        });

        const tbody = table.querySelector('tbody');
        tbody.innerHTML = '';

        if (rowsData.length === 0) {
            tbody.innerHTML = `<tr><td colspan="${1 + months.length}" class="text-center">Nenhuma loja com dados de ADT encontrada</td></tr>`;
        } else {
            rowsData.forEach(({ storeId, store }) => {
                const tr = document.createElement('tr');
                const cleanName = store.name.replace(/domino[s]?'?\s*/gi, '').trim();
                const rowVals = [];
                let html = `<td>${cleanName}</td>`;

                months.forEach(m => {
                    const d = maps[m][storeId];
                    const v = d ? (d.adt || 0) : 0;
                    rowVals.push(v);
                    html += `<td class="text-center month-adt-cell" style="position:relative;z-index:2;background:transparent;${getAdtStyle(v)}">${v > 0 ? v.toFixed(2) : '--'}</td>`;
                });

                tr.setAttribute('data-vals', JSON.stringify(rowVals));
                tr.innerHTML = html;
                tbody.appendChild(tr);
            });

            requestAnimationFrame(() => {
                tbody.querySelectorAll('tr').forEach(tr => {
                    const vals = JSON.parse(tr.getAttribute('data-vals') || '[]');
                    const cells = Array.from(tr.querySelectorAll('.month-adt-cell'));
                    if (vals.length && cells.length) drawRowSparkline(tr, cells, vals, 'row-sparkline-madt', 25.0);
                });
                const _kpiAdtCard = document.getElementById('kpi-adt-avg-mensal');
                if (_kpiAdtCard) _kpiAdtCard.setAttribute('data-sparkline-vals', JSON.stringify(groupAvgs));
                drawCardSparkline('kpi-adt-avg-mensal', 'card-sparkline-madt', groupAvgs, 25.0);
            });

            const avgAdt = totalOrders > 0 ? sumAdtW / totalOrders : 0;
            if (kpiVal)  kpiVal.textContent  = totalOrders > 0 ? avgAdt.toFixed(2) + ' min' : '--';
            if (kpiCard) kpiCard.className   = 'kpi-card ' + (avgAdt < 25 ? 'kpi-success' : avgAdt < 30 ? 'kpi-warning' : 'kpi-danger');

            const critListEl = document.getElementById('kpi-adt-critical-mensal');
            const crit = rowsData.filter(r => r.lastAdt > 40).sort((a, b) => b.lastAdt - a.lastAdt);
            if (critListEl) {
                critListEl.innerHTML = crit.map(r => {
                    const n = r.store.name.replace(/domino[s]?'?\s*/gi, '').trim();
                    return `<div class="kpi-critical-item"><span>${n}</span><span>${r.lastAdt.toFixed(1)}m</span></div>`;
                }).join('');
                critListEl.style.display = crit.length ? 'flex' : 'none';
            }
        }
    }

    // ── TABELA 2: EXTREMES % ───────────────────────────────────────
    function renderMonthlyExtremesTable(storeIds, monthly, months) {
        const table    = document.getElementById('table-extremes-mensal');
        const kpiVal   = document.querySelector('#kpi-extremes-avg-mensal .kpi-value');
        const kpiCard  = document.getElementById('kpi-extremes-avg-mensal');
        const titleEl  = document.getElementById('title-extremes-mensal');
        const consultant = consultantSelect.value;
        const consultantText = consultantSelect.options[consultantSelect.selectedIndex].text.toUpperCase();

        if (titleEl) titleEl.textContent = consultant === 'all'
            ? 'Extremes % Mensal'
            : 'Extremes % Mensal — ' + consultantText;

        if (months.length === 0) {
            table.querySelector('thead').innerHTML = '';
            table.querySelector('tbody').innerHTML = MONTHLY_EMPTY_HTML;
            if (kpiVal) kpiVal.textContent = '--';
            return;
        }

        table.querySelector('thead').innerHTML = buildMonthlyHeader(months);

        const maps = buildMonthlyMaps(monthly.adt || {}, months);
        const rowsData = [];
        let totalOrders = 0, sumExtW = 0;

        storeIds.forEach(storeId => {
            const store = rawData.stores[storeId] || { name: 'Loja ' + storeId };
            if (!months.some(m => maps[m][storeId])) return;
            let lastExt = 0, lastOrders = 0;
            for (let i = months.length - 1; i >= 0; i--) {
                const d = maps[months[i]][storeId];
                if (d) { lastExt = d.extreme || 0; lastOrders = d.orders || 0; break; }
            }
            totalOrders += lastOrders;
            sumExtW     += lastExt * lastOrders;
            rowsData.push({ storeId, store, lastExt, lastOrders });
        });

        rowsData.sort((a, b) => b.lastExt - a.lastExt);

        const groupAvgs = months.map(m => {
            let mo = 0, se = 0;
            storeIds.forEach(sid => {
                const d = maps[m][sid];
                if (d) { mo += d.orders || 0; se += (d.extreme || 0) * (d.orders || 0); }
            });
            return mo > 0 ? se / mo : 0;
        });

        const tbody = table.querySelector('tbody');
        tbody.innerHTML = '';

        if (rowsData.length === 0) {
            tbody.innerHTML = `<tr><td colspan="${1 + months.length}" class="text-center">Nenhuma loja com dados de Extremes encontrada</td></tr>`;
        } else {
            rowsData.forEach(({ storeId, store }) => {
                const tr = document.createElement('tr');
                const cleanName = store.name.replace(/domino[s]?'?\s*/gi, '').trim();
                const rowVals = [];
                let html = `<td>${cleanName}</td>`;

                months.forEach(m => {
                    const d = maps[m][storeId];
                    const v = d ? (d.extreme || 0) : 0;
                    rowVals.push(v);
                    html += `<td class="text-center month-ext-cell" style="position:relative;z-index:2;background:transparent;${getExtremeStyle(v)}">${v > 0 ? (v * 100).toFixed(2) + '%' : '--'}</td>`;
                });

                tr.setAttribute('data-vals', JSON.stringify(rowVals));
                tr.innerHTML = html;
                tbody.appendChild(tr);
            });

            requestAnimationFrame(() => {
                tbody.querySelectorAll('tr').forEach(tr => {
                    const vals = JSON.parse(tr.getAttribute('data-vals') || '[]');
                    const cells = Array.from(tr.querySelectorAll('.month-ext-cell'));
                    if (vals.length && cells.length) drawRowSparkline(tr, cells, vals, 'row-sparkline-mext', 0.02);
                });
                const _kpiExtCard = document.getElementById('kpi-extremes-avg-mensal');
                if (_kpiExtCard) _kpiExtCard.setAttribute('data-sparkline-vals', JSON.stringify(groupAvgs));
                drawCardSparkline('kpi-extremes-avg-mensal', 'card-sparkline-mext', groupAvgs, 0.02);
            });

            const avgExt = totalOrders > 0 ? sumExtW / totalOrders : 0;
            if (kpiVal)  kpiVal.textContent  = totalOrders > 0 ? (avgExt * 100).toFixed(2) + '%' : '--';
            if (kpiCard) kpiCard.className   = 'kpi-card ' + (avgExt < 0.02 ? 'kpi-success' : avgExt < 0.10 ? 'kpi-warning' : 'kpi-danger');

            const critListEl = document.getElementById('kpi-extremes-critical-mensal');
            const crit = rowsData.filter(r => r.lastExt > 0.20).sort((a, b) => b.lastExt - a.lastExt);
            if (critListEl) {
                critListEl.innerHTML = crit.map(r => {
                    const n = r.store.name.replace(/domino[s]?'?\s*/gi, '').trim();
                    return `<div class="kpi-critical-item"><span>${n}</span><span>${(r.lastExt * 100).toFixed(1)}%</span></div>`;
                }).join('');
                critListEl.style.display = crit.length ? 'flex' : 'none';
            }
        }
    }

    // ── TABELA 3: SERVICE EXCEPTIONS ───────────────────────────────
    function renderMonthlyExceptionsTable(storeIds, monthly, months) {
        const table    = document.getElementById('table-exceptions-mensal');
        const kpiVal   = document.querySelector('#kpi-exceptions-avg-mensal .kpi-value');
        const kpiCard  = document.getElementById('kpi-exceptions-avg-mensal');
        const titleEl  = document.getElementById('title-exceptions-mensal');
        const consultant = consultantSelect.value;
        const consultantText = consultantSelect.options[consultantSelect.selectedIndex].text.toUpperCase();

        if (titleEl) titleEl.textContent = consultant === 'all'
            ? 'Service Exceptions Mensal'
            : 'Service Exceptions Mensal — ' + consultantText;

        if (months.length === 0) {
            table.querySelector('thead').innerHTML = '';
            table.querySelector('tbody').innerHTML = MONTHLY_EMPTY_HTML;
            if (kpiVal) kpiVal.textContent = '--';
            return;
        }

        table.querySelector('thead').innerHTML = buildMonthlyHeader(months);

        const maps = buildMonthlyMaps(monthly.exceptions || {}, months);
        const rowsData = [];
        let totalDelv = 0, totalExcCount = 0;

        storeIds.forEach(storeId => {
            const store = rawData.stores[storeId] || { name: 'Loja ' + storeId };
            if (!months.some(m => maps[m][storeId])) return;
            let lastExcPct = 0, lastDelv = 0, lastExcCnt = 0;
            for (let i = months.length - 1; i >= 0; i--) {
                const d = maps[months[i]][storeId];
                if (d) { lastExcPct = d.exceptions || 0; lastDelv = d.delvOrders || 0; lastExcCnt = d.exceptionsCount || 0; break; }
            }
            totalDelv     += lastDelv;
            totalExcCount += lastExcCnt;
            rowsData.push({ storeId, store, lastExcPct });
        });

        rowsData.sort((a, b) => b.lastExcPct - a.lastExcPct);

        const groupAvgs = months.map(m => {
            let md = 0, me = 0;
            storeIds.forEach(sid => {
                const d = maps[m][sid];
                if (d) { md += d.delvOrders || 0; me += d.exceptionsCount || 0; }
            });
            return md > 0 ? me / md : 0;
        });

        const tbody = table.querySelector('tbody');
        tbody.innerHTML = '';

        if (rowsData.length === 0) {
            tbody.innerHTML = `<tr><td colspan="${1 + months.length}" class="text-center">Nenhuma loja com dados de Exceções encontrada</td></tr>`;
        } else {
            rowsData.forEach(({ storeId, store }) => {
                const tr = document.createElement('tr');
                const cleanName = store.name.replace(/domino[s]?'?\s*/gi, '').trim();
                const rowVals = [];
                let html = `<td>${cleanName}</td>`;

                months.forEach(m => {
                    const d = maps[m][storeId];
                    const v = d ? (d.exceptions || 0) : 0;
                    rowVals.push(v);
                    html += `<td class="text-center month-exc-cell" style="position:relative;z-index:2;background:transparent;${getExceptionStyle(v)}">${v > 0 ? (v * 100).toFixed(2) + '%' : '--'}</td>`;
                });

                tr.setAttribute('data-vals', JSON.stringify(rowVals));
                tr.innerHTML = html;
                tbody.appendChild(tr);
            });

            requestAnimationFrame(() => {
                tbody.querySelectorAll('tr').forEach(tr => {
                    const vals = JSON.parse(tr.getAttribute('data-vals') || '[]');
                    const cells = Array.from(tr.querySelectorAll('.month-exc-cell'));
                    if (vals.length && cells.length) drawRowSparkline(tr, cells, vals, 'row-sparkline-mexc', 0.40);
                });
                const _kpiExcCard = document.getElementById('kpi-exceptions-avg-mensal');
                if (_kpiExcCard) _kpiExcCard.setAttribute('data-sparkline-vals', JSON.stringify(groupAvgs));
                drawCardSparkline('kpi-exceptions-avg-mensal', 'card-sparkline-mexc', groupAvgs, 0.20);
            });

            const avgExc = totalDelv > 0 ? totalExcCount / totalDelv : 0;
            if (kpiVal)  kpiVal.textContent  = totalDelv > 0 ? (avgExc * 100).toFixed(2) + '%' : '--';
            if (kpiCard) kpiCard.className   = 'kpi-card ' + (avgExc < 0.10 ? 'kpi-success' : avgExc < 0.25 ? 'kpi-warning' : 'kpi-danger');

            const critListEl = document.getElementById('kpi-exceptions-critical-mensal');
            const crit = rowsData.filter(r => r.lastExcPct > 0.50).sort((a, b) => b.lastExcPct - a.lastExcPct);
            if (critListEl) {
                critListEl.innerHTML = crit.map(r => {
                    const n = r.store.name.replace(/domino[s]?'?\s*/gi, '').trim();
                    return `<div class="kpi-critical-item"><span>${n}</span><span>${(r.lastExcPct * 100).toFixed(1)}%</span></div>`;
                }).join('');
                critListEl.style.display = crit.length ? 'flex' : 'none';
            }
        }
    }

    // ==========================================
    // ANÁLISE DE RISCO (SEGUNDA-FEIRA)
    // Compara as 2 semanas mais recentes.
    // Crítica = ADT > 40 min OU Exceptions > 45%
    // ==========================================

    const RISK_ADT_LIMIT = 40;      // minutos
    const RISK_EXC_LIMIT = 0.45;    // 45% (fração)

    function renderRiskAnalysis(storeIds) {
        const weeks = rawData.weeks || [];
        const infoEl = document.getElementById('risk-weeks-info');

        const tables = {
            fechariam: document.getElementById('table-fechariam'),
            aviso: document.getElementById('table-aviso'),
            recuperadas: document.getElementById('table-recuperadas')
        };
        const counts = {
            fechariam: document.getElementById('count-fechariam'),
            aviso: document.getElementById('count-aviso'),
            recuperadas: document.getElementById('count-recuperadas')
        };

        // Precisa de pelo menos 2 semanas para comparar
        if (weeks.length < 2) {
            if (infoEl) infoEl.innerHTML = '⚠️ São necessárias pelo menos <strong>2 semanas</strong> de dados para a análise de risco. Atualmente há ' + weeks.length + '.';
            Object.keys(tables).forEach(k => {
                if (tables[k]) {
                    tables[k].querySelector('thead').innerHTML = '';
                    tables[k].querySelector('tbody').innerHTML = '<tr><td class="risk-empty">Dados insuficientes</td></tr>';
                }
                if (counts[k]) counts[k].textContent = '0';
            });
            return;
        }

        const prevWeek = weeks[weeks.length - 2];
        const curWeek  = weeks[weeks.length - 1];

        if (infoEl) {
            infoEl.innerHTML = 'Comparando &nbsp;<strong>Semana ' + prevWeek + '</strong> (anterior) &nbsp;→&nbsp; <strong>Semana ' + curWeek + '</strong> (atual). &nbsp; Critério de risco: ADT &gt; ' + RISK_ADT_LIMIT + ' min &nbsp;<strong>ou</strong>&nbsp; Exceptions &gt; ' + (RISK_EXC_LIMIT * 100) + '%.';
        }

        // Mapas de consulta rápida por loja
        const adtPrev = {}, adtCur = {}, excPrev = {}, excCur = {};
        (rawData.adt.weeks[prevWeek] || []).forEach(r => { adtPrev[r.storeId] = r; });
        (rawData.adt.weeks[curWeek]  || []).forEach(r => { adtCur[r.storeId]  = r; });
        (rawData.exceptions.weeks[prevWeek] || []).forEach(r => { excPrev[r.storeId] = r; });
        (rawData.exceptions.weeks[curWeek]  || []).forEach(r => { excCur[r.storeId]  = r; });

        function getMetrics(storeId, adtMap, excMap) {
            const adt = adtMap[storeId] ? (adtMap[storeId].adt || 0) : 0;
            const exc = excMap[storeId] ? (excMap[storeId].exceptions || 0) : 0;
            const hasData = !!(adtMap[storeId] || excMap[storeId]);
            return { adt, exc, hasData };
        }
        function isCritical(m) {
            return (m.adt > RISK_ADT_LIMIT) || (m.exc > RISK_EXC_LIMIT);
        }
        function triggerLabel(m) {
            const t = [];
            if (m.adt > RISK_ADT_LIMIT) t.push('ADT');
            if (m.exc > RISK_EXC_LIMIT) t.push('EXC');
            return t.join(' + ');
        }

        const fechariam = [], aviso = [], recuperadas = [];

        storeIds.forEach(storeId => {
            const store = rawData.stores[storeId] || { name: 'Loja ' + storeId };
            const mp = getMetrics(storeId, adtPrev, excPrev);
            const mc = getMetrics(storeId, adtCur, excCur);
            
            const critAdtPrev = mp.adt > RISK_ADT_LIMIT;
            const critExcPrev = mp.exc > RISK_EXC_LIMIT;
            const critAdtCur  = mc.adt > RISK_ADT_LIMIT;
            const critExcCur  = mc.exc > RISK_EXC_LIMIT;

            const critPrev = critAdtPrev || critExcPrev;
            const critCur  = critAdtCur || critExcCur;

            const item = { storeId, store, mp, mc };

            if (critCur) {
                // Para fechar o iFood, o MESMO indicador que estourou na semana passada precisa continuar estourado nesta semana.
                const persistAdt = critAdtPrev && critAdtCur;
                const persistExc = critExcPrev && critExcCur;
                
                if (persistAdt || persistExc) {
                    fechariam.push(item);
                } else {
                    // Se mudou de indicador crítico (ex: saiu do Exceptions mas estourou o ADT), ela ganha um novo aviso.
                    aviso.push(item);
                }
            } else if (critPrev) {
                // Era crítica e deixou de ser em ambos os critérios
                recuperadas.push(item);
            }
        });

        // Severidade (pior primeiro): quão longe está do limite
        const severity = (m) => Math.max(m.adt / RISK_ADT_LIMIT, m.exc / RISK_EXC_LIMIT);
        fechariam.sort((a, b) => severity(b.mc) - severity(a.mc));
        aviso.sort((a, b) => severity(b.mc) - severity(a.mc));
        recuperadas.sort((a, b) => severity(b.mp) - severity(a.mp));

        renderRiskTable(tables.fechariam, fechariam, prevWeek, curWeek, 'cur', 'Nenhuma loja fecharia o iFood 🎉');
        renderRiskTable(tables.aviso, aviso, prevWeek, curWeek, 'cur', 'Nenhuma loja em aviso nesta semana 🎉');
        renderRiskTable(tables.recuperadas, recuperadas, prevWeek, curWeek, 'prev', 'Nenhuma loja recuperada nesta semana');

        if (counts.fechariam)  counts.fechariam.textContent  = fechariam.length;
        if (counts.aviso)      counts.aviso.textContent      = aviso.length;
        if (counts.recuperadas) counts.recuperadas.textContent = recuperadas.length;
    }

    // Monta uma tabela de risco (Loja | ADT ant | ADT atual | Exc ant | Exc atual)
    // highlightWeek: 'cur' destaca a tag na semana atual, 'prev' na anterior
    function renderRiskTable(table, items, prevWeek, curWeek, highlightWeek, emptyMsg) {
        if (!table) return;
        const thead = table.querySelector('thead');
        const tbody = table.querySelector('tbody');

        thead.innerHTML =
            '<tr>' +
            '<th>Loja</th>' +
            '<th class="text-center" style="border-left: 2px solid var(--border-color)">ADT ' + prevWeek + '</th>' +
            '<th class="text-center">ADT ' + curWeek + '</th>' +
            '<th class="text-center" style="border-left: 2px solid var(--border-color)">Exc. ' + prevWeek + '</th>' +
            '<th class="text-center">Exc. ' + curWeek + '</th>' +
            '</tr>';

        if (items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="risk-empty">' + emptyMsg + '</td></tr>';
            return;
        }

        let html = '';
        items.forEach(({ store, mp, mc }) => {
            const cleanName = store.name.replace(/domino[s]?'?\s*/gi, '').trim();

            // Tag do motivo, na semana destacada
            const trigM = highlightWeek === 'cur' ? mc : mp;
            const trig = (highlightWeek !== null && (trigM.adt > RISK_ADT_LIMIT || trigM.exc > RISK_EXC_LIMIT))
                ? '<span class="risk-trigger">' + (function(m){const t=[];if(m.adt>RISK_ADT_LIMIT)t.push('ADT');if(m.exc>RISK_EXC_LIMIT)t.push('EXC');return t.join(' + ');})(trigM) + '</span>'
                : '';

            const adtPrevTxt = mp.adt > 0 ? mp.adt.toFixed(1) : '--';
            const adtCurTxt  = mc.adt > 0 ? mc.adt.toFixed(1) : '--';
            const excPrevTxt = mp.exc > 0 ? (mp.exc * 100).toFixed(1) + '%' : '--';
            const excCurTxt  = mc.exc > 0 ? (mc.exc * 100).toFixed(1) + '%' : '--';

            html +=
                '<tr>' +
                '<td>' + cleanName + trig + '</td>' +
                '<td class="text-center" style="border-left: 2px solid var(--border-color); ' + getAdtStyle(mp.adt) + '">' + adtPrevTxt + '</td>' +
                '<td class="text-center" style="font-weight: 700; ' + getAdtStyle(mc.adt) + '">' + adtCurTxt + '</td>' +
                '<td class="text-center" style="border-left: 2px solid var(--border-color); ' + getExceptionStyle(mp.exc) + '">' + excPrevTxt + '</td>' +
                '<td class="text-center" style="font-weight: 700; ' + getExceptionStyle(mc.exc) + '">' + excCurTxt + '</td>' +
                '</tr>';
        });
        tbody.innerHTML = html;
    }

    const btnExport = document.getElementById('btn-export');
    if (btnExport) {
        function redrawSparklinesInElement(element) {
            // Redesenha sparklines da tabela de Exceções
            const excRows = element.querySelectorAll('#table-exceptions tbody tr');
            excRows.forEach(tr => {
                const weekValsAttr = tr.getAttribute('data-weeks-values');
                if (weekValsAttr) {
                    const values = JSON.parse(weekValsAttr);
                    const weekCells = Array.from(tr.querySelectorAll('.week-cell'));
                    if (values.length > 0 && weekCells.length > 0) {
                        const firstCell = weekCells[0];
                        const lastCell = weekCells[weekCells.length - 1];
                        let canvas = firstCell.querySelector('.row-sparkline');
                        if (canvas) {
                            const firstRect = firstCell.getBoundingClientRect();
                            const lastRect = lastCell.getBoundingClientRect();
                            const width = lastRect.right - firstRect.left;
                            const height = firstRect.height;
                            canvas.style.width = width + 'px';
                            canvas.style.height = height + 'px';
                            canvas.width = width * 2;
                            canvas.height = height * 2;
                            const ctx = canvas.getContext('2d');
                            ctx.clearRect(0, 0, canvas.width, canvas.height);
                            ctx.scale(2, 2);
                            const points = [];
                            const cellWidth = width / values.length;
                            const maxValue = Math.max(0.40, ...values);
                            values.forEach((val, i) => {
                                const x = cellWidth * (i + 0.5);
                                const padding = height * 0.15;
                                const y = height - padding - ((val / maxValue) * (height - 2 * padding));
                                points.push({ x, y });
                            });
                            let isImproving = values.length > 1 ? (values[values.length - 1] <= values[0]) : (values[0] < 0.10);
                            const lineColor = isImproving ? '#10b981' : '#ef4444';
                            const fillGradStart = isImproving ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.08)';
                            const fillGradEnd = isImproving ? 'rgba(16, 185, 129, 0.01)' : 'rgba(239, 68, 68, 0.01)';
                            ctx.beginPath();
                            ctx.moveTo(points[0].x, points[0].y);
                            for (let i = 1; i < points.length; i++) ctx.lineTo(points[i].x, points[i].y);
                            ctx.strokeStyle = lineColor;
                            ctx.lineWidth = 2.5;
                            ctx.lineCap = 'round';
                            ctx.lineJoin = 'round';
                            ctx.stroke();
                            ctx.beginPath();
                            ctx.moveTo(points[0].x, points[0].y);
                            for (let i = 1; i < points.length; i++) ctx.lineTo(points[i].x, points[i].y);
                            ctx.lineTo(points[points.length - 1].x, height);
                            ctx.lineTo(points[0].x, height);
                            ctx.closePath();
                            const grad = ctx.createLinearGradient(0, 0, 0, height);
                            grad.addColorStop(0, fillGradStart);
                            grad.addColorStop(1, fillGradEnd);
                            ctx.fillStyle = grad;
                            ctx.fill();
                        }
                    }
                }
            });

            // Redesenha sparklines de ADT e Extremes
            const adtRows = element.querySelectorAll('#table-adt tbody tr');
            adtRows.forEach(tr => {
                const adtValsAttr = tr.getAttribute('data-adt-values');
                const adtCells = Array.from(tr.querySelectorAll('.adt-week-cell'));
                if (adtValsAttr && adtCells.length > 0) {
                    drawRowSparkline(tr, adtCells, JSON.parse(adtValsAttr), 'row-sparkline-adt', 25.0);
                }
                const extValsAttr = tr.getAttribute('data-ext-values');
                const extCells = Array.from(tr.querySelectorAll('.ext-week-cell'));
                if (extValsAttr && extCells.length > 0) {
                    drawRowSparkline(tr, extCells, JSON.parse(extValsAttr), 'row-sparkline-ext', 0.02);
                }
            });

            // Redesenha sparklines das tabelas mensais (ADT, Extremes, Exceptions)
            [
                { rowSel: '#table-adt-mensal tbody tr', cellClass: 'month-adt-cell', canvasClass: 'row-sparkline-madt', maxDefault: 25.0 },
                { rowSel: '#table-extremes-mensal tbody tr', cellClass: 'month-ext-cell', canvasClass: 'row-sparkline-mext', maxDefault: 0.02 },
                { rowSel: '#table-exceptions-mensal tbody tr', cellClass: 'month-exc-cell', canvasClass: 'row-sparkline-mexc', maxDefault: 0.40 }
            ].forEach(cfg => {
                element.querySelectorAll(cfg.rowSel).forEach(tr => {
                    const valsAttr = tr.getAttribute('data-vals');
                    if (!valsAttr) return;
                    const vals = JSON.parse(valsAttr);
                    const cells = Array.from(tr.querySelectorAll('.' + cfg.cellClass));
                    if (vals.length && cells.length) drawRowSparkline(tr, cells, vals, cfg.canvasClass, cfg.maxDefault);
                });
            });
            // Redesenha card-sparklines dos KPIs mensais
            [
                { cardId: 'kpi-adt-avg-mensal',        cls: 'card-sparkline-madt', attr: 'data-sparkline-vals', max: 25.0 },
                { cardId: 'kpi-extremes-avg-mensal',   cls: 'card-sparkline-mext', attr: 'data-sparkline-vals', max: 0.02 },
                { cardId: 'kpi-exceptions-avg-mensal', cls: 'card-sparkline-mexc', attr: 'data-sparkline-vals', max: 0.20 }
            ].forEach(cfg => {
                const card = element.querySelector ? element.querySelector('#' + cfg.cardId) : document.getElementById(cfg.cardId);
                if (!card) return;
                const valsAttr = card.getAttribute(cfg.attr);
                if (!valsAttr) return;
                drawCardSparkline(cfg.cardId, cfg.cls, JSON.parse(valsAttr), cfg.max);
            });
        }

        function exportSection(sectionId, filename) {
            return new Promise((resolve, reject) => {
                const element = document.getElementById(sectionId);
                if (!element) {
                    reject(`Elemento ${sectionId} não encontrado`);
                    return;
                }

                const wrapper = element.querySelector('.table-wrapper');
                const originalMaxHeight = wrapper.style.maxHeight;
                const originalOverflowY = wrapper.style.overflowY;

                // Remove limite de altura e rolagem temporariamente para renderizar todas as linhas
                wrapper.style.maxHeight = 'none';
                wrapper.style.overflowY = 'visible';

                // Aplica classe de exportação (tamanho otimizado, fonte maior para celular)
                element.classList.add('export-mode');
                
                // Redesenha as sparklines com a geometria correta do modo exportação
                redrawSparklinesInElement(element);

                // Aguarda 2 frames para o browser aplicar o layout antes de capturar
                await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));

                html2canvas(element, {
                    useCORS: true,
                    scale: 2, // Resolução de alta fidelidade
                    backgroundColor: '#ffffff'
                }).then(canvas => {
                    // Restaura estilos originais
                    wrapper.style.maxHeight = originalMaxHeight;
                    wrapper.style.overflowY = originalOverflowY;
                    element.classList.remove('export-mode');
                    
                    // Restaura as sparklines para o tamanho da tela
                    redrawSparklinesInElement(element);

                    // Gatilho de download
                    const link = document.createElement('a');
                    link.download = filename;
                    link.href = canvas.toDataURL('image/png');
                    link.click();
                    resolve();
                }).catch(err => {
                    // Garante que os estilos serão restaurados em caso de falha
                    wrapper.style.maxHeight = originalMaxHeight;
                    wrapper.style.overflowY = originalOverflowY;
                    element.classList.remove('export-mode');
                    redrawSparklinesInElement(element);
                    reject(err);
                });
            });
        }

        btnExport.addEventListener('click', async () => {
            btnExport.disabled = true;
            btnExport.textContent = 'Gerando...';

            const consultantName = consultantSelect.value;
            const suffix = consultantName === 'all' ? 'geral' : consultantName.toLowerCase().replace(/\s+/g, '_');

            let sections;
            if (activeTab === 'risco') {
                sections = [
                    ['section-fechariam', `pwr_risco_fechariam_ifood_${suffix}.png`],
                    ['section-aviso', `pwr_risco_aviso_${suffix}.png`],
                    ['section-recuperadas', `pwr_risco_recuperadas_${suffix}.png`]
                ];
            } else if (activeTab === 'mensal') {
                sections = [
                    ['section-adt-mensal', `pwr_adt_mensal_${suffix}.png`],
                    ['section-extremes-mensal', `pwr_extremes_mensal_${suffix}.png`],
                    ['section-exceptions-mensal', `pwr_service_exceptions_mensal_${suffix}.png`]
                ];
            } else {
                sections = [
                    ['section-adt', `pwr_adt_e_extremos_${suffix}.png`],
                    ['section-exceptions', `pwr_service_exceptions_${suffix}.png`]
                ];
            }

            try {
                for (let i = 0; i < sections.length; i++) {
                    const [sectionId, filename] = sections[i];
                    await exportSection(sectionId, filename);
                    // Aguarda 800ms entre exportações para evitar bloqueio do navegador
                    if (i < sections.length - 1) await new Promise(r => setTimeout(r, 800));
                }
            } catch (err) {
                console.error('Erro ao exportar seção:', err);
                alert('Erro ao gerar as imagens. Tente novamente.');
            } finally {
                btnExport.disabled = false;
                btnExport.textContent = 'Exportar PNG';
            }
        });
    }

    // ==========================================
    // CONTROLE DE ACESSO POR SENHA (GATEKEEPER)
    // ==========================================
    const CORRECT_HASH = '0aa8f8c610025637a5ce377cecdb9c0ee045a5d6a95da3d81a1d0865f4e0459c';
    const MASTER_HASH = '2353138e4c62f0fe72918bf785298709eaae8890d265fbe73df678954773b9f7';

    async function sha256(message) {
        const msgBuffer = new TextEncoder().encode(message);
        const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    }

    const gate = document.getElementById('password-gate');
    const input = document.getElementById('gate-password');
    const toggleBtn = document.getElementById('btn-toggle-password');
    const errorMsg = document.getElementById('password-error');
    const enterBtn = document.getElementById('btn-enter');

    function unlock() {
        if (gate) gate.classList.add('hidden');
        document.body.classList.remove('gate-locked');
        loadData();
    }

    if (toggleBtn && input) {
        toggleBtn.addEventListener('click', () => {
            if (input.type === 'password') {
                input.type = 'text';
                toggleBtn.textContent = '🙈';
            } else {
                input.type = 'password';
                toggleBtn.textContent = '👁️';
            }
        });
    }

    async function checkPassword() {
        if (!input) return;
        const password = input.value;
        const hashed = await sha256(password);
        if (hashed === CORRECT_HASH || hashed === MASTER_HASH) {
            unlock();
        } else {
            if (errorMsg) errorMsg.style.display = 'block';
            input.value = '';
            input.focus();
        }
    }

    if (enterBtn) {
        enterBtn.addEventListener('click', checkPassword);
    }
    if (input) {
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                checkPassword();
            }
        });
    }

    // Sempre exige senha ao carregar ou recarregar a página
    if (input) {
        // Pequeno delay para garantir o foco após renderização
        setTimeout(() => input.focus(), 100);
    }
});
