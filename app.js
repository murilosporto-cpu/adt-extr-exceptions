// Domino's Pizza Performance PWR Dashboard Logic - Evolução de Períodos
document.addEventListener('DOMContentLoaded', () => {
    let rawData = null;

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
    }

    // Filtra e Renderiza tudo
    function render() {
        if (!rawData) return;

        const consultant = consultantSelect.value;
        const franchisee = franchiseeSelect.value;
        const search = searchInput.value.toLowerCase().trim();
        
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
    }

    function renderAdtTable(storeIds) {
        const weeks = rawData.weeks || [];
        
        // Montar Cabeçalho da Tabela
        let headerHtml = `
            <tr>
                <th>Loja</th>
                <th>Consultor</th>
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

        if (rowsData.length === 0) {
            tbody.innerHTML = `<tr><td colspan="${5 + (weeks.length * 2)}" class="text-center">Nenhuma loja com dados de ADT encontrada</td></tr>`;
        } else {
            rowsData.forEach(item => {
                const { storeId, store, orders, adtVal, extVal } = item;
                const tr = document.createElement('tr');

                // Célula ADT Acumulado
                const adtStyle = getAdtStyle(adtVal);
                const cleanStoreName = store.name.replace(/domino[s]?'?\s*/gi, '').trim();
                let html = `
                    <td>${cleanStoreName}</td>
                    <td>${store.consultant || 'N/D'}</td>
                    <td class="text-center" style="border-left: 2px solid var(--border-color); font-weight: 700; ${adtStyle}">${adtVal > 0 ? adtVal.toFixed(2) : '--'}</td>
                `;

                // Células ADT Semanais
                weeks.forEach(w => {
                    const wData = adtWeeksMap[w][storeId];
                    const wAdt = wData ? wData.adt : 0;
                    const wAdtStyle = getAdtStyle(wAdt);
                    html += `<td class="text-center" style="${wAdtStyle}">${wAdt > 0 ? wAdt.toFixed(2) : '--'}</td>`;
                });

                // Célula Extremes Acumulado
                const extPct = extVal * 100;
                const extStyle = getExtremeStyle(extVal);
                html += `<td class="text-center" style="border-left: 2px solid var(--border-color); font-weight: 700; ${extStyle}">${extVal > 0 ? extPct.toFixed(2) + '%' : '--'}</td>`;

                // Células Extremes Semanais
                weeks.forEach(w => {
                    const wData = adtWeeksMap[w][storeId];
                    const wExt = wData ? wData.extreme : 0;
                    const wExtPct = wExt * 100;
                    const wExtStyle = getExtremeStyle(wExt);
                    html += `<td class="text-center" style="${wExtStyle}">${wExt > 0 ? wExtPct.toFixed(2) + '%' : '--'}</td>`;
                });

                tr.innerHTML = html;
                tbody.appendChild(tr);
            });
        }

        // Atualizar KPIs Globais
        const avgAdt = totalOrders > 0 ? (sumAdtWeight / totalOrders) : 0;
        const avgExt = totalOrders > 0 ? (sumExtWeight / totalOrders) : 0;

        kpiAdtVal.textContent = totalOrders > 0 ? `${avgAdt.toFixed(2)} min` : '--';
        kpiExtremesVal.textContent = totalOrders > 0 ? `${(avgExt * 100).toFixed(2)}%` : '--';

        kpiAdtCard.className = 'kpi-card ' + (avgAdt < 25 ? 'kpi-success' : (avgAdt < 30 ? 'kpi-warning' : 'kpi-danger'));
        kpiExtremesCard.className = 'kpi-card ' + (avgExt < 0.02 ? 'kpi-success' : (avgExt < 0.10 ? 'kpi-warning' : 'kpi-danger'));

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
                <th>Consultor</th>
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

        if (rowsData.length === 0) {
            tbody.innerHTML = `<tr><td colspan="${6 + weeks.length}" class="text-center">Nenhuma loja com dados de Exceções encontrada</td></tr>`;
        } else {
            rowsData.forEach(item => {
                const { storeId, store, delvOrders, excCount, excPct } = item;
                const tr = document.createElement('tr');

                const pctVal = excPct * 100;
                const excStyle = getExceptionStyle(excPct);

                const cleanStoreName = store.name.replace(/domino[s]?'?\s*/gi, '').trim();
                let html = `
                    <td>${cleanStoreName}</td>
                    <td>${store.consultant || 'N/D'}</td>
                    <td class="text-center" style="border-left: 2px solid var(--border-color); font-weight: 700; ${excStyle}">${excPct > 0 ? pctVal.toFixed(2) + '%' : '--'}</td>
                `;

                // Células Exceptions Semanais
                weeks.forEach(w => {
                    const wData = excWeeksMap[w][storeId];
                    const wExc = wData ? wData.exceptions : 0;
                    const wExcPct = wExc * 100;
                    const wExcStyle = getExceptionStyle(wExc);
                    html += `<td class="text-center" style="${wExcStyle}">${wExc > 0 ? wExcPct.toFixed(2) + '%' : '--'}</td>`;
                });

                tr.innerHTML = html;
                tbody.appendChild(tr);
            });
        }

        // Atualizar KPIs Globais
        const avgExc = totalDelv > 0 ? (totalExcCount / totalDelv) : 0;

        kpiExcVal.textContent = totalDelv > 0 ? `${(avgExc * 100).toFixed(2)}%` : '--';

        kpiExcCard.className = 'kpi-card ' + (avgExc < 0.10 ? 'kpi-success' : (avgExc < 0.25 ? 'kpi-warning' : 'kpi-danger'));

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

    // Configurar exportação para PNG em dois arquivos separados contemplando todas as lojas
    const btnExport = document.getElementById('btn-export');
    if (btnExport) {
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

                html2canvas(element, {
                    useCORS: true,
                    scale: 2, // Resolução de alta fidelidade
                    backgroundColor: '#ffffff'
                }).then(canvas => {
                    // Restaura estilos originais
                    wrapper.style.maxHeight = originalMaxHeight;
                    wrapper.style.overflowY = originalOverflowY;
                    element.classList.remove('export-mode');

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
                    reject(err);
                });
            });
        }

        btnExport.addEventListener('click', () => {
            btnExport.disabled = true;
            btnExport.textContent = 'Gerando...';

            const consultantName = consultantSelect.value;
            const suffix = consultantName === 'all' ? 'geral' : consultantName.toLowerCase().replace(/\s+/g, '_');

            exportSection('section-adt', `pwr_adt_e_extremos_${suffix}.png`)
                .then(() => {
                    // Aguarda 800ms para iniciar a segunda exportação e evitar bloqueio do navegador
                    setTimeout(() => {
                        exportSection('section-exceptions', `pwr_service_exceptions_${suffix}.png`)
                            .then(() => {
                                btnExport.disabled = false;
                                btnExport.textContent = 'Exportar PNG';
                            })
                            .catch(err => {
                                console.error('Erro ao exportar exceptions:', err);
                                btnExport.disabled = false;
                                btnExport.textContent = 'Exportar PNG';
                            });
                    }, 800);
                })
                .catch(err => {
                    console.error('Erro ao exportar ADT:', err);
                    alert('Erro ao gerar as imagens. Tente novamente.');
                    btnExport.disabled = false;
                    btnExport.textContent = 'Exportar PNG';
                });
        });
    }

    // Carregar inicialmente
    loadData();
});
