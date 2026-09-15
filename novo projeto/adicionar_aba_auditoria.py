import os
import json
import glob
import pandas as pd
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
dados_dir = os.path.join(BASE_DIR, 'dados_all_stores')

print("1. Calculando dias faltantes por loja nos 28 dias...")
import re
days = sorted(list(set(re.findall(r'\d{4}-\d{2}-\d{2}', f)[0] for f in glob.glob(os.path.join(dados_dir, 'Keys Summary*.xlsx')) if re.findall(r'\d{4}-\d{2}-\d{2}', f))))

store_days = defaultdict(dict)
for d in days:
    filepath = os.path.join(dados_dir, f"Keys Summary - All Stores (Stores) ({d}).xlsx")
    df = pd.read_excel(filepath)
    df['Store'] = df['Store'].astype(str).str.strip().str.zfill(5)
    for _, r in df.iterrows():
        sid = r['Store']
        orders = r['Order Count'] if pd.notnull(r['Order Count']) else 0
        store_days[sid][d] = int(orders)

with open(os.path.join(ROOT_DIR, 'franquias', 'stores_mapping.json'), 'r', encoding='utf-8-sig') as f:
    fran_map = json.load(f)
with open(os.path.join(ROOT_DIR, 'lojas-proprias', 'stores_mapping.json'), 'r', encoding='utf-8-sig') as f:
    corp_map = json.load(f)

excluded_ids = {'19680', '19707', '19733', '19792', '19964', '19967', '19736'}

def get_backfill_list(mapping, is_corp=False):
    result = []
    for sid, st in mapping.items():
        if sid in excluded_ids:
            continue
        day_dict = store_days.get(sid, {})
        tot_orders = sum(day_dict.values())
        if tot_orders == 0:
            continue  # inativa
        missing = [d for d in days if day_dict.get(d, 0) == 0]
        if missing:
            clean_name = st.get('name', f"Loja {sid}").replace("DOMINOS ", "").replace("DOMINO'S ", "").strip()
            formatted = [f"{d.split('-')[2]}/{d.split('-')[1]}" for d in missing]
            result.append({
                'storeId': sid,
                'name': clean_name,
                'consultant': st.get('consultant', 'N/D'),
                'franchisee': st.get('franchisee', 'N/D'),
                'type': 'C' if is_corp else 'F',
                'missingCount': len(missing),
                'missingDays': missing,
                'formattedDays': formatted
            })
    result.sort(key=lambda x: x['missingCount'], reverse=True)
    return result

fran_backfill = get_backfill_list(fran_map, is_corp=False)
corp_backfill = get_backfill_list(corp_map, is_corp=True)

print(f"Encontradas {len(fran_backfill)} Franquias e {len(corp_backfill)} Lojas Proprias com dias faltantes.")

# 2. Atualizar data.json e data.js em franquias e lojas-proprias
for panel, bf_list in [('franquias', fran_backfill), ('lojas-proprias', corp_backfill)]:
    p_dir = os.path.join(BASE_DIR, panel)
    json_path = os.path.join(p_dir, 'data.json')
    js_path = os.path.join(p_dir, 'data.js')

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    data['backfill'] = bf_list

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with open(js_path, 'w', encoding='utf-8') as f:
        f.write('window.PWR_DATA = ' + json.dumps(data, ensure_ascii=False) + ';\n')

    print(f"data.json e data.js atualizados com backfill em {panel}")

print("3. Atualizando HTML dos paineis para incluir aba de Auditoria de Subida...")

tab_button_html = '''            <button id="tab-risco" class="tab-btn" data-tab="risco">
                <span class="tab-icon">⚠️</span> Análise de Risco
            </button>
            <button id="tab-backfill" class="tab-btn" data-tab="backfill">
                <span class="tab-icon">🔄</span> Auditoria de Subida (Dias Faltantes)
            </button>'''

backfill_view_html = '''        <!-- Visão Auditoria de Subida (Dias Faltantes) -->
        <div id="backfill-view" class="tab-content" data-view="backfill">
            <section id="section-backfill" class="dashboard-section card">
                <div class="section-header blue-accent">
                    <h2>Auditoria de Subida de Vendas (Detecção de Dias Faltantes)</h2>
                    <span class="goal-badge">28 Dias Analisados (17/08 a 13/09)</span>
                </div>
                
                <div class="kpi-grid">
                    <div class="kpi-card" id="kpi-backfill-stores">
                        <div class="kpi-info">
                            <h3>Lojas com Dias Faltantes</h3>
                            <div class="kpi-value" id="kpi-backfill-stores-val">0</div>
                            <p class="kpi-subtitle">Vendas zeradas ou subida pendente no PWR</p>
                        </div>
                    </div>
                    <div class="kpi-card" id="kpi-backfill-days">
                        <div class="kpi-info">
                            <h3>Total de Dias Ausentes</h3>
                            <div class="kpi-value" id="kpi-backfill-days-val">0</div>
                            <p class="kpi-subtitle">Dias para re-extração automática (backfill)</p>
                        </div>
                    </div>
                </div>

                <div class="table-wrapper">
                    <table id="table-backfill">
                        <thead>
                            <tr>
                                <th>Loja</th>
                                <th>Consultor / Coordenador</th>
                                <th>Franqueado</th>
                                <th class="text-center">Dias sem Vendas</th>
                                <th>Datas Faltantes Detectadas</th>
                                <th class="text-center">Ação Recomendada</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td colspan="6" class="text-center">Carregando dados de auditoria...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>
        </div>'''

for panel in ['franquias', 'lojas-proprias']:
    idx_path = os.path.join(BASE_DIR, panel, 'index.html')
    with open(idx_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Inserir o botão da aba se ainda não inserido
    if 'data-tab="backfill"' not in html:
        old_btn = '''            <button id="tab-risco" class="tab-btn" data-tab="risco">
                <span class="tab-icon">⚠️</span> Análise de Risco
            </button>'''
        html = html.replace(old_btn, tab_button_html)

    # Inserir a seção se ainda não inserida
    if 'id="backfill-view"' not in html:
        # Inserir antes de </main>
        html = html.replace('</main>', backfill_view_html + '\n    </main>')

    with open(idx_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"index.html atualizado em {panel}")

print("4. Atualizando app.js para renderizar e filtrar a tabela de Auditoria de Subida...")

render_backfill_js = '''
    // =============================================================
    // RENDERIZAÇÃO DA ABA AUDITORIA DE SUBIDA (DIAS FALTANTES)
    // =============================================================
    function renderBackfillTable(storeIds) {
        const tbody = document.querySelector('#table-backfill tbody');
        const kpiStoresVal = document.getElementById('kpi-backfill-stores-val');
        const kpiDaysVal = document.getElementById('kpi-backfill-days-val');
        if (!tbody) return;

        const backfillList = rawData.backfill || [];
        const filtered = backfillList.filter(item => storeIds.includes(item.storeId));

        let totalMissingDays = 0;
        filtered.forEach(item => { totalMissingDays += item.missingCount; });

        if (kpiStoresVal) kpiStoresVal.textContent = filtered.length;
        if (kpiDaysVal) kpiDaysVal.textContent = totalMissingDays;

        if (filtered.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center" style="padding: 2rem; color: var(--success-color); font-weight: 700;">Nenhuma loja encontrada com dias faltantes nos filtros selecionados!</td></tr>';
            return;
        }

        let html = '';
        filtered.forEach(item => {
            const badgeBg = item.missingCount >= 10 ? '#fee2e2' : (item.missingCount >= 5 ? '#ffedd5' : '#fef3c7');
            const badgeColor = item.missingCount >= 10 ? '#dc2626' : (item.missingCount >= 5 ? '#c2410c' : '#b45309');
            
            const datePills = item.formattedDays.map(d => 
                `<span style="background: #f1f5f9; color: #1e293b; padding: 2px 7px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; margin: 2px; display: inline-block; border: 1px solid #e2e8f0;">${d}</span>`
            ).join('');

            html += `
                <tr>
                    <td><strong>${item.storeId}</strong> - ${item.name}</td>
                    <td>${item.consultant || 'N/D'}</td>
                    <td>${item.franchisee || 'N/D'}</td>
                    <td class="text-center">
                        <span class="badge" style="background-color: ${badgeBg}; color: ${badgeColor}; font-weight: 800; padding: 4px 10px; border-radius: 8px; font-size: 0.85rem;">
                            ${item.missingCount} dia(s)
                        </span>
                    </td>
                    <td><div style="display: flex; flex-wrap: wrap; gap: 4px; max-width: 650px;">${datePills}</div></td>
                    <td class="text-center">
                        <span class="badge" style="background-color: #dbeafe; color: #1e40af; font-weight: 700; padding: 5px 12px; border-radius: 8px; font-size: 0.82rem; white-space: nowrap;">
                            🔄 Subida Pendente (Backfill)
                        </span>
                    </td>
                </tr>
            `;
        });
        tbody.innerHTML = html;
    }
'''

for panel in ['franquias', 'lojas-proprias']:
    app_path = os.path.join(BASE_DIR, panel, 'app.js')
    with open(app_path, 'r', encoding='utf-8') as f:
        js = f.read()

    # Adicionar chamada renderBackfillTable(storesToShow) dentro de render()
    if 'renderBackfillTable(' not in js:
        js = js.replace('renderRiskAnalysis(storesToShow);', 'renderRiskAnalysis(storesToShow);\n        renderBackfillTable(storesToShow);')
        js = js.replace('renderRiskAnalysis(storesToShow)', 'renderRiskAnalysis(storesToShow);\n        renderBackfillTable(storesToShow);')
        js += '\n' + render_backfill_js

    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(js)
    print(f"app.js atualizado em {panel}")

print("\nConcluído com sucesso!")
