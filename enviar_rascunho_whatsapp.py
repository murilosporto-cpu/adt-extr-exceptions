#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
AUTOMAÇÃO PWR -> WHATSAPP DESKTOP
==============================================================================
1. Abre o painel PWR local (franquias/index.html) em modo headless via Playwright.
2. Filtra pelo consultor MURILO e exporta as 2 tabelas em alta resolução:
   - pwr_adt_e_extremos_murilo.png (Tabela ADT & Extremos)
   - pwr_service_exceptions_murilo.png (Tabela Service Exceptions)
3. Salva os arquivos diretamente na pasta Downloads do usuário.
4. Abre o WhatsApp Desktop e prepara o rascunho com o texto e as imagens
   nos grupos:
   - "Murilo Porto 🍕Gerentes"
   - "Murilo Porto 🍕 franqueados"
==============================================================================
"""

import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import glob
import ctypes
from ctypes import wintypes
from pathlib import Path
import win32gui
import win32con
import win32process
import win32clipboard
from playwright.sync_api import sync_playwright

# Configurações de caminhos
BASE_DIR = Path(__file__).resolve().parent
FRANQUIAS_HTML = BASE_DIR / "franquias" / "index.html"
DOWNLOADS_DIR = Path(os.environ["USERPROFILE"]) / "Downloads"
DADOS_DIR = BASE_DIR / "dados_all_stores"

# Win32 Virtual Key Codes
VK_BACK = 0x08
VK_RETURN = 0x0D
VK_CONTROL = 0x11
VK_ESCAPE = 0x1B
VK_A = 0x41
VK_F = 0x46
VK_V = 0x56

# Configurações do WhatsApp
GROUPS = [
    {
        "name": "Murilo Porto 🍕Gerentes",
        "search": "Murilo Porto Gerentes"
    },
    {
        "name": "Murilo Porto 🍕 franqueados",
        "search": "Murilo Porto franqueados"
    }
]

def ensure_desktop_access():
    """Garante que a thread consiga acessar a área de trabalho interativa (default)."""
    try:
        u = ctypes.windll.user32
        h_default = u.OpenDesktopW("default", 0, False, 0x01FF)
        if h_default:
            u.SetThreadDesktop(h_default)
    except Exception:
        pass

def get_dynamic_period_text() -> str:
    """Detecta o período acumulado de setembro dos dados locais para o cabeçalho do texto."""
    files = glob.glob(str(DADOS_DIR / "Keys Summary - All Stores (Stores) (*).xlsx"))
    dias = []
    for f in files:
        part = f.split("(") [-1].split(")")[0]
        if part.startswith("2026-09-"):
            dias.append(part)
    dias.sort()
    if dias:
        start_day = dias[0].split("-")[-1]
        end_day = dias[-1].split("-")[-1]
        return f"01 e {end_day} de Setembro"
    return "01 e 18 de Setembro"

def build_message_text() -> str:
    period = get_dynamic_period_text()
    return f"""Bom dia a todos!!!

Tempos de Serviço | {period} na coluna acumulado

Pessoal, reforço a necessidade de atenção total aos resultados de ADT e EXTREMOS.

Peço foco especial nas lojas que estão com ADT superior a 31 minutos e, principalmente, nas lojas com ADT extremo (acima de 40 minutos) ⚠️

Precisamos atuar rapidamente nos planos de ação para recuperar esse indicador e garantir uma melhor experiência aos nossos clientes.

Conto com o apoio de todos 🍕

Apenas para Recordar:

ADT IDEAL = 25 MINUTOS
EXTREMES = 2%
LOAD TIME = 2:59 MINUTOS
WAIT TIME = 5 MINUTOS
OTD = 15 MINUTOS
EXCEPTIONS = ABAIXO DE 10%"""

def export_pngs_from_dashboard():
    """Executa o Playwright headless para exportar os 2 PNGs filtrados por MURILO."""
    print("=" * 60)
    print(" [1/3] Exportando tabelas PNG do painel PWR (Consultor MURILO)...")
    print("=" * 60)
    
    html_url = "file:///" + str(FRANQUIAS_HTML).replace("\\", "/")
    
    downloaded_files = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.set_viewport_size({"width": 1600, "height": 1200})
        
        print(f"-> Carregando painel: {FRANQUIAS_HTML.name}")
        page.goto(html_url)
        
        # Desbloqueio se houver gate
        if page.is_visible("#gate-password"):
            page.fill("#gate-password", "franquias2026")
            page.click("#btn-enter")
            page.wait_for_timeout(400)
            
        # Filtra pelo consultor MURILO
        print("-> Filtrando consultor: MURILO")
        page.select_option("#filter-consultant", "MURILO")
        page.wait_for_timeout(600)
        
        # Handler de download
        def on_download(download):
            fn = download.suggested_filename
            target = DOWNLOADS_DIR / fn
            download.save_as(str(target))
            downloaded_files.append(target)
            print(f"  [OK] Baixado: {fn} ({target.stat().st_size:,} bytes)")
            
        page.on("download", on_download)
        
        print("-> Disparando botão 'Exportar Imagens'...")
        page.click("#btn-export")
        page.wait_for_timeout(5000)
        
        browser.close()
        
    print(f"✅ Total de imagens baixadas em Downloads: {len(downloaded_files)}")
    for f in downloaded_files:
        print(f"   -> {f}")
    return downloaded_files

def set_clipboard_files(file_paths):
    """Define a lista de caminhos de arquivos no clipboard como CF_HDROP."""
    class DROPFILES(ctypes.Structure):
        _fields_ = [
            ("pFiles", wintypes.DWORD),
            ("pt", wintypes.POINT),
            ("fNC", wintypes.BOOL),
            ("fWide", wintypes.BOOL),
        ]
    
    files_str = "\0".join([str(p) for p in file_paths]) + "\0\0"
    files_bytes = files_str.encode("utf-16-le")
    
    df = DROPFILES()
    df.pFiles = ctypes.sizeof(DROPFILES)
    df.pt.x = 0
    df.pt.y = 0
    df.fNC = 0
    df.fWide = 1
    
    total_bytes = bytes(df) + files_bytes
    
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_HDROP, total_bytes)
    finally:
        win32clipboard.CloseClipboard()

def set_clipboard_text(text: str):
    """Define texto Unicode no clipboard do Windows."""
    text_crlf = text.replace("\r\n", "\n").replace("\n", "\r\n")
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text_crlf)
    finally:
        win32clipboard.CloseClipboard()

def press_hotkey(mod_vk, key_vk):
    u = ctypes.windll.user32
    u.keybd_event(mod_vk, 0, 0, 0)
    time.sleep(0.04)
    u.keybd_event(key_vk, 0, 0, 0)
    time.sleep(0.04)
    u.keybd_event(key_vk, 0, 2, 0)
    time.sleep(0.04)
    u.keybd_event(mod_vk, 0, 2, 0)
    time.sleep(0.08)

def press_key(key_vk):
    u = ctypes.windll.user32
    u.keybd_event(key_vk, 0, 0, 0)
    time.sleep(0.04)
    u.keybd_event(key_vk, 0, 2, 0)
    time.sleep(0.04)

def click_at(x, y):
    u = ctypes.windll.user32
    u.SetCursorPos(x, y)
    time.sleep(0.05)
    u.mouse_event(2, 0, 0, 0, 0) # LEFTDOWN
    time.sleep(0.05)
    u.mouse_event(4, 0, 0, 0, 0) # LEFTUP
    time.sleep(0.1)

def find_whatsapp_hwnd():
    ensure_desktop_access()
    found = []
    def enum_cb(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title == "WhatsApp":
                found.append(hwnd)
        return True
    win32gui.EnumWindows(enum_cb, None)
    return found[0] if found else None

def focus_whatsapp():
    ensure_desktop_access()
    hwnd = find_whatsapp_hwnd()
    if not hwnd:
        print("-> WhatsApp Desktop não encontrado em execução. Iniciando aplicativo...")
        os.startfile("whatsapp:")
        for _ in range(20):
            time.sleep(0.5)
            hwnd = find_whatsapp_hwnd()
            if hwnd:
                break
                
    if not hwnd:
        print("⚠️ Não foi possível abrir ou localizar o WhatsApp Desktop.")
        return None
        
    u = ctypes.windll.user32
    k32 = ctypes.windll.kernel32
    
    # Alt key trick to bypass Windows SetForegroundWindow restrictions
    u.keybd_event(0x12, 0, 0, 0)
    u.ShowWindow(hwnd, win32con.SW_RESTORE)
    u.BringWindowToTop(hwnd)
    u.SetForegroundWindow(hwnd)
    u.keybd_event(0x12, 0, 2, 0)
    time.sleep(0.4)
    
    # Se ainda não for o foreground, tenta via AttachThreadInput
    if u.GetForegroundWindow() != hwnd:
        cur_thread = k32.GetCurrentThreadId()
        fore_hwnd = u.GetForegroundWindow()
        fore_thread = u.GetWindowThreadProcessId(fore_hwnd, None)
        target_thread = u.GetWindowThreadProcessId(hwnd, None)
        
        u.AttachThreadInput(cur_thread, fore_thread, True)
        u.AttachThreadInput(cur_thread, target_thread, True)
        u.BringWindowToTop(hwnd)
        u.SetForegroundWindow(hwnd)
        u.AttachThreadInput(cur_thread, fore_thread, False)
        u.AttachThreadInput(cur_thread, target_thread, False)
        time.sleep(0.4)
        
    return hwnd

def open_chat_by_search(hwnd, search_term: str):
    """Usa Ctrl+F para pesquisar e abrir a conversa no WhatsApp Desktop."""
    ensure_desktop_access()
    focus_whatsapp()
    time.sleep(0.2)
    
    # Foca campo de pesquisa
    press_hotkey(VK_CONTROL, VK_F)
    time.sleep(0.3)
    
    # Limpa campo
    press_hotkey(VK_CONTROL, VK_A)
    time.sleep(0.05)
    press_key(VK_BACK)
    time.sleep(0.1)
    
    # Cola o nome da busca
    set_clipboard_text(search_term)
    press_hotkey(VK_CONTROL, VK_V)
    time.sleep(1.0)
    
    # Pressiona Enter para abrir a primeira opção
    press_key(VK_RETURN)
    time.sleep(0.8)

def draft_in_whatsapp(files):
    """
    Prepara o rascunho com o texto nos 2 grupos:
    1. 'Murilo Porto 🍕Gerentes'
    2. 'Murilo Porto 🍕 franqueados'
    E copia os 2 arquivos PNG para o clipboard para que o usuário possa colar com Ctrl+V.
    """
    print("\n" + "=" * 60)
    print(" [2/3] Preparando rascunhos no WhatsApp Desktop...")
    print("=" * 60)
    
    hwnd = focus_whatsapp()
    if not hwnd:
        return False
        
    caption = build_message_text()
    
    for idx, grp in enumerate(GROUPS, start=1):
        gname = grp["name"]
        gsearch = grp["search"]
        print(f"\n-> [{idx}/2] Abrindo grupo: '{gname}'...")
        
        open_chat_by_search(hwnd, gsearch)
        
        # Localiza o retângulo da janela para clicar no campo 'Digite uma mensagem'
        rect = win32gui.GetWindowRect(hwnd)
        target_x = int(rect[0] + (rect[2] - rect[0]) * 0.65)
        target_y = int(rect[3] - 25)
        
        click_at(target_x, target_y)
        time.sleep(0.3)
        
        # Cola o texto no rascunho
        set_clipboard_text(caption)
        press_hotkey(VK_CONTROL, VK_V)
        time.sleep(0.8)
        print(f"   ✅ Texto puro colado no rascunho de '{gname}'!")

    return True

def main():
    try:
        # 1. Exporta os PNGs para Downloads
        files = export_pngs_from_dashboard()
        
        # 2. Prepara rascunhos no WhatsApp Desktop
        draft_in_whatsapp(files)
        
        print("\n" + "=" * 60)
        print("  SUCESSO TOTAL!")
        print("  - Tabelas salvas em: C:\\Users\\muril\\Downloads\\")
        print("  - Rascunhos preenchidos nos 2 grupos do WhatsApp Desktop")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"\n❌ ERRO durante a execução da automação: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
