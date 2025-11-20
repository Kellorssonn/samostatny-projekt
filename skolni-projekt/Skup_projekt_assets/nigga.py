import pygame
import math
import random
import json
import os

# Inicializace Pygame
pygame.init()

# --- Nastavení okna ---
SIRKA_OKNA, VYSKA_OKNA = 1280, 720
okno = pygame.display.set_mode((SIRKA_OKNA, VYSKA_OKNA))
pygame.display.set_caption("Farmářský Kliker - Finální oprava")

# --- Stavy hry ---
herni_stav = "menu"

# --- Barvy ---
HNEDA = (139, 69, 19)
HNEDA_POZADI = (210, 180, 140)
ZELENA_TRAVA = (34, 139, 34)
MODRA_OBLOHA = (135, 206, 235)
BILA = (255, 255, 255)
CERNA = (0, 0, 0)
ZLATA = (255, 215, 0)
ORANZOVA_MRKEV = (255, 140, 0)
SEDA_PANEL = (200, 200, 200)
SEDA_TLACITKO = (170, 170, 170)
SEDA_TLACITKO_NAJETI = (190, 190, 190)
CERVENA_TLACITKO = (200, 50, 50)
ZELENA_USPECH = (60, 179, 113)

# --- Fonty ---
font_titulek = pygame.font.Font(None, 100)
font_velky = pygame.font.Font(None, 74)
font_stredni = pygame.font.Font(None, 50)
font_maly = pygame.font.Font(None, 36)
font_nejmensi = pygame.font.Font(None, 24)

# --- Herní proměnné (deklarace) ---
zlataky = 0.0
sila_kliku = 1
pasivni_prijem = 0
vylepseni = {}
statistiky = {}
uspechy = {}

# --- Herní data a funkce ---
def reset_dat():
    """Funkce pro resetování všech herních dat na výchozí hodnoty."""
    global zlataky, sila_kliku, pasivni_prijem, vylepseni, statistiky, uspechy
    zlataky = 0.0
    sila_kliku = 1
    pasivni_prijem = 0
    vylepseni = {
        'lepsi_konev': [0, 15, 1.15, 1], 'kvalitni_hnojivo': [0, 100, 1.2, 5],
        'obilne_pole': [0, 50, 1.18, 1], 'kurnik': [0, 500, 1.22, 10], 'kravin': [0, 2500, 1.25, 50]
    }
    statistiky = {'celkem_kliku': 0, 'celkem_zlataku': 0.0, 'zlate_mrkve': 0}
    uspechy = {
        'První sklizeň': {'podminka': ('celkem_kliku', 1), 'odemceno': False, 'popis': "Klikni jednou"},
        'Workoholik': {'podminka': ('celkem_kliku', 100), 'odemceno': False, 'popis': "Klikni 100krát"},
        'První tisícovka': {'podminka': ('celkem_zlataku', 1000), 'odemceno': False, 'popis': "Vydělej 1000 zlaťáků"},
        'Farmář milionář': {'podminka': ('celkem_zlataku', 1000000), 'odemceno': False, 'popis': "Vydělej 1 000 000 zlaťáků"},
        'Štěstí v neštěstí': {'podminka': ('zlate_mrkve', 1), 'odemceno': False, 'popis': "Najdi Zlatou mrkev"}
    }

NAZEV_SAVE_SOUBORU = "savegame.json"

def save_game():
    data_k_ulozeni = { 'zlataky': zlataky, 'vylepseni': vylepseni, 'statistiky': statistiky, 'uspechy': uspechy }
    with open(NAZEV_SAVE_SOUBORU, 'w') as f: json.dump(data_k_ulozeni, f)

def load_game():
    global zlataky, sila_kliku, pasivni_prijem, vylepseni, statistiky, uspechy
    if not os.path.exists(NAZEV_SAVE_SOUBORU): return False
    try:
        with open(NAZEV_SAVE_SOUBORU, 'r') as f:
            data = json.load(f)
            zlataky = data.get('zlataky', 0.0)
            vylepseni = data.get('vylepseni', {})
            statistiky = data.get('statistiky', {})
            uspechy = data.get('uspechy', {})
            sila_kliku = 1 + sum(d[3] * d[0] for k, d in vylepseni.items() if k in ['lepsi_konev', 'kvalitni_hnojivo'])
            pasivni_prijem = sum(d[3] * d[0] for k, d in vylepseni.items() if k in ['obilne_pole', 'kurnik', 'kravin'])
            return True
    except (json.JSONDecodeError, KeyError): return False

def spocitej_cenu(nazev):
    level, zakladni_cena, cena_nasobic, _ = vylepseni[nazev]
    return math.ceil(zakladni_cena * (cena_nasobic ** level))

def kup_vylepseni(nazev):
    global zlataky, sila_kliku, pasivni_prijem
    cena = spocitej_cenu(nazev)
    if zlataky >= cena:
        zlataky -= cena
        vylepseni[nazev][0] += 1
        if nazev in ['lepsi_konev', 'kvalitni_hnojivo']: sila_kliku += vylepseni[nazev][3]
        else: pasivni_prijem += vylepseni[nazev][3]
        pygame.time.delay(100)

def zkontroluj_uspechy():
    for nazev, data in uspechy.items():
        if not data['odemceno']:
            stat, hodnota = data['podminka']
            if statistiky.get(stat, 0) >= hodnota:
                data['odemceno'] = True
                notifikace_uspechu.append([f"Úspěch: {nazev}", 5])

def vykresli_text(text, font, barva, x, y, stred=False, alpha=255):
    text_surface = font.render(text, True, barva)
    text_surface.set_alpha(alpha)
    text_rect = text_surface.get_rect()
    if stred: text_rect.center = (x, y)
    else: text_rect.topleft = (x, y)
    okno.blit(text_surface, text_rect)

# OPRAVA: Chybějící funkce pro vykreslení pozadí byla vrácena
def vykresli_pozadi_menu():
    """Vykreslí stylizované pozadí pro hlavní menu."""
    okno.fill(MODRA_OBLOHA)
    pygame.draw.rect(okno, ZELENA_TRAVA, (0, VYSKA_OKNA - 200, SIRKA_OKNA, 200))
    pygame.draw.rect(okno, HNEDA_POZADI, (0, VYSKA_OKNA - 250, SIRKA_OKNA, 50))
    pygame.draw.circle(okno, ZLATA, (SIRKA_OKNA - 100, 100), 60)

# Inicializace herních dat při spuštění
reset_dat()
obchod_tlacitka_rects = {}
plovouci_texty = []
notifikace_uspechu = []
zlata_mrkev = {'aktivni': False, 'rect': None, 'casovac': 0}

# --- Hlavní herní smyčka ---
casovac = pygame.time.Clock()
bezi = True
cas_od_posledniho_prijmu = 0.0

while bezi:
    delta_time = casovac.tick(60) / 1000.0
    pozice_mysi = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: bezi = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and herni_stav != "menu":
                if herni_stav == "hra": save_game()
                herni_stav = "menu"
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if herni_stav == "hra":
                if 80 < pozice_mysi[0] < 520 and 130 < pozice_mysi[1] < 570:
                    zlataky += sila_kliku; statistiky['celkem_kliku'] += 1; statistiky['celkem_zlataku'] += sila_kliku
                    plovouci_texty.append([f"+{sila_kliku}", pozice_mysi[0] + random.randint(-20, 20), pozice_mysi[1] - 30, 1.0])
                if zlata_mrkev['aktivni'] and zlata_mrkev['rect'].collidepoint(pozice_mysi):
                    bonus = math.ceil((pasivni_prijem + sila_kliku) * 30) + 50
                    zlataky += bonus; statistiky['celkem_zlataku'] += bonus; statistiky['zlate_mrkve'] += 1
                    plovouci_texty.append([f"BONUS +{bonus}", pozice_mysi[0], pozice_mysi[1]-40, 2.0])
                    zlata_mrkev['aktivni'] = False
                for nazev, rect in obchod_tlacitka_rects.items():
                    if rect.collidepoint(pozice_mysi): kup_vylepseni(nazev)
            elif herni_stav == "menu":
                sirka_tl, vyska_tl, x_tl = 350, 80, SIRKA_OKNA/2 - 175
                if os.path.exists(NAZEV_SAVE_SOUBORU) and pygame.Rect(x_tl, 280, sirka_tl, vyska_tl).collidepoint(pozice_mysi):
                    if load_game(): herni_stav = "hra"
                if pygame.Rect(x_tl, 370, sirka_tl, vyska_tl).collidepoint(pozice_mysi):
                    reset_dat(); herni_stav = "hra"
                if pygame.Rect(x_tl, 460, sirka_tl, vyska_tl).collidepoint(pozice_mysi): herni_stav = "uspechy"
                if pygame.Rect(x_tl, 550, sirka_tl, vyska_tl).collidepoint(pozice_mysi): herni_stav = "nastaveni"
                if pygame.Rect(x_tl, 640, sirka_tl, vyska_tl).collidepoint(pozice_mysi): bezi = False
            elif herni_stav == "nastaveni":
                if pygame.Rect(SIRKA_OKNA/2 - 175, VYSKA_OKNA - 240, 350, 80).collidepoint(pozice_mysi):
                    reset_dat()
                    if os.path.exists(NAZEV_SAVE_SOUBORU): os.remove(NAZEV_SAVE_SOUBORU)
                    notifikace_uspechu.append(["Postup byl resetován!", 3]); herni_stav = "menu"
                if pygame.Rect(SIRKA_OKNA/2 - 175, VYSKA_OKNA - 140, 350, 80).collidepoint(pozice_mysi):
                    herni_stav = "menu"
            elif herni_stav == "uspechy":
                if pygame.Rect(SIRKA_OKNA/2 - 175, VYSKA_OKNA - 140, 350, 80).collidepoint(pozice_mysi):
                    herni_stav = "menu"
    
    # --- Logika a vykreslování ---
    if herni_stav == "hra":
        cas_od_posledniho_prijmu += delta_time
        if cas_od_posledniho_prijmu >= 1.0:
            pocet_sekund = math.floor(cas_od_posledniho_prijmu)
            prijem = pasivni_prijem * pocet_sekund
            zlataky += prijem; statistiky['celkem_zlataku'] += prijem
            cas_od_posledniho_prijmu -= pocet_sekund
        
        zkontroluj_uspechy()

        if not zlata_mrkev['aktivni'] and random.random() < 0.002:
            zlata_mrkev.update({'aktivni': True, 'rect': pygame.Rect(random.randint(100, SIRKA_OKNA*2//3-100), random.randint(VYSKA_OKNA-140, VYSKA_OKNA-80), 40, 60), 'casovac': 5})
        elif zlata_mrkev['aktivni']:
            zlata_mrkev['casovac'] -= delta_time
            if zlata_mrkev['casovac'] <= 0: zlata_mrkev['aktivni'] = False

        okno.fill(MODRA_OBLOHA)
        pygame.draw.rect(okno, ZELENA_TRAVA, (0, VYSKA_OKNA - 150, SIRKA_OKNA, 150))
        SIRKA_HERNI_PLOCHY = SIRKA_OKNA * 2 // 3
        pygame.draw.rect(okno, HNEDA, (80, 130, 440, 440), border_radius=20)
        
        uroven_rustu = sum(v[0] for v in vylepseni.values()); velikost_rostliny = min(200 + uroven_rustu, 380)
        stred_pole = (300, 350);
        pygame.draw.rect(okno, (0, 100, 0), (stred_pole[0] - 15, stred_pole[1] - velikost_rostliny/2 + 30, 30, velikost_rostliny))
        pygame.draw.circle(okno, ZLATA, (stred_pole[0], stred_pole[1] - velikost_rostliny/2), 60)
        pygame.draw.circle(okno, (128, 64, 0), (stred_pole[0], stred_pole[1] - velikost_rostliny/2), 30)
        
        if zlata_mrkev['aktivni']:
            pygame.draw.ellipse(okno, ORANZOVA_MRKEV, zlata_mrkev['rect'])
            pygame.draw.rect(okno, ZELENA_TRAVA, (zlata_mrkev['rect'].centerx-5, zlata_mrkev['rect'].y-10, 10, 20))
        
        vykresli_text("ESC pro návrat do menu", font_nejmensi, BILA, 10, 10)

        SIRKA_PANELU = SIRKA_OKNA // 3
        pygame.draw.rect(okno, SEDA_PANEL, (SIRKA_HERNI_PLOCHY, 0, SIRKA_PANELU, VYSKA_OKNA))
        vykresli_text(f"Zlaťáky: {math.floor(zlataky)}", font_velky, ZLATA, SIRKA_HERNI_PLOCHY + SIRKA_PANELU/2, 60, stred=True)
        vykresli_text(f"{pasivni_prijem}/s | Síla kliku: {sila_kliku}", font_maly, CERNA, SIRKA_HERNI_PLOCHY + SIRKA_PANELU/2, 120, stred=True)
        vykresli_text("Obchod", font_stredni, CERNA, SIRKA_HERNI_PLOCHY + SIRKA_PANELU / 2, 180, stred=True)
        
        poz_y, sirka_tl, vyska_tl, mezera = 220, SIRKA_PANELU - 40, 70, 15
        nazvy_cz = {'lepsi_konev': 'Lepší konev', 'kvalitni_hnojivo': 'Hnojivo', 'obilne_pole': 'Pole', 'kurnik': 'Kurník', 'kravin': 'Kravín'}
        for i, nazev in enumerate(vylepseni.keys()):
            rect = pygame.Rect(SIRKA_HERNI_PLOCHY + 20, poz_y + i * (vyska_tl + mezera), sirka_tl, vyska_tl)
            obchod_tlacitka_rects[nazev] = rect
            cena = spocitej_cenu(nazev); dostatek = zlataky >= cena
            barva = SEDA_TLACITKO
            if rect.collidepoint(pozice_mysi) and dostatek: barva = SEDA_TLACITKO_NAJETI
            elif not dostatek: barva = (100, 100, 100)
            pygame.draw.rect(okno, barva, rect, border_radius=10)
            vykresli_text(f"{nazvy_cz.get(nazev)} (Lvl {vylepseni[nazev][0]})", font_maly, CERNA, rect.centerx, rect.centery - 10, stred=True)
            vykresli_text(f"Cena: {cena}", font_nejmensi, CERNA, rect.centerx, rect.centery + 15, stred=True)
    else:
        vykresli_pozadi_menu()
        sirka_tl, vyska_tl, x_tl = 350, 80, SIRKA_OKNA/2-175
        if herni_stav == "menu":
            vykresli_text("Farmářský Kliker", font_titulek, ZELENA_TRAVA, SIRKA_OKNA/2, 150, stred=True)
            if os.path.exists(NAZEV_SAVE_SOUBORU):
                pygame.draw.rect(okno, SEDA_TLACITKO, (x_tl, 280, sirka_tl, vyska_tl), border_radius=15); vykresli_text("Pokračovat", font_stredni, CERNA, x_tl + sirka_tl/2, 280+vyska_tl/2, stred=True)
            pygame.draw.rect(okno, SEDA_TLACITKO, (x_tl, 370, sirka_tl, vyska_tl), border_radius=15); vykresli_text("Nová hra" if os.path.exists(NAZEV_SAVE_SOUBORU) else "Spustit hru", font_stredni, CERNA, x_tl + sirka_tl/2, 370+vyska_tl/2, stred=True)
            pygame.draw.rect(okno, SEDA_TLACITKO, (x_tl, 460, sirka_tl, vyska_tl), border_radius=15); vykresli_text("Úspěchy", font_stredni, CERNA, x_tl + sirka_tl/2, 460+vyska_tl/2, stred=True)
            pygame.draw.rect(okno, SEDA_TLACITKO, (x_tl, 550, sirka_tl, vyska_tl), border_radius=15); vykresli_text("Nastavení", font_stredni, CERNA, x_tl + sirka_tl/2, 550+vyska_tl/2, stred=True)
            pygame.draw.rect(okno, SEDA_TLACITKO, (x_tl, 640, sirka_tl, vyska_tl), border_radius=15); vykresli_text("Ukončit", font_stredni, CERNA, x_tl + sirka_tl/2, 640+vyska_tl/2, stred=True)
        elif herni_stav == "nastaveni":
            vykresli_text("Nastavení", font_titulek, CERNA, SIRKA_OKNA/2, 150, stred=True)
            vykresli_text("Zde budou herní možnosti...", font_maly, CERNA, SIRKA_OKNA/2, 300, stred=True)
            pygame.draw.rect(okno, CERVENA_TLACITKO, (x_tl, VYSKA_OKNA-240, sirka_tl, vyska_tl), border_radius=15); vykresli_text("Resetovat postup", font_stredni, CERNA, x_tl + sirka_tl/2, VYSKA_OKNA-200, stred=True)
            pygame.draw.rect(okno, SEDA_TLACITKO, (x_tl, VYSKA_OKNA-140, sirka_tl, vyska_tl), border_radius=15); vykresli_text("Zpět", font_stredni, CERNA, x_tl+sirka_tl/2, VYSKA_OKNA-100, stred=True)
        elif herni_stav == "uspechy":
            vykresli_text("Úspěchy", font_titulek, CERNA, SIRKA_OKNA/2, 80, stred=True)
            y_pos = 180
            for nazev, data in uspechy.items():
                if data['odemceno']: vykresli_text(f"✔ {nazev}: {data['popis']}", font_maly, ZELENA_USPECH, SIRKA_OKNA/2, y_pos, stred=True)
                else: vykresli_text(f"🔒 ???", font_maly, CERNA, SIRKA_OKNA/2, y_pos, stred=True)
                y_pos += 50
            pygame.draw.rect(okno, SEDA_TLACITKO, (x_tl, VYSKA_OKNA-140, sirka_tl, vyska_tl), border_radius=15); vykresli_text("Zpět", font_stredni, CERNA, x_tl+sirka_tl/2, VYSKA_OKNA-100, stred=True)

    if notifikace_uspechu:
        notifikace_uspechu[0][1] -= delta_time
        if notifikace_uspechu[0][1] <= 0: notifikace_uspechu.pop(0)
        else:
            alpha = min(255, int(notifikace_uspechu[0][1] * 255 / 2))
            s = pygame.Surface((500, 60), pygame.SRCALPHA); s.set_alpha(alpha)
            pygame.draw.rect(s, ZELENA_USPECH, s.get_rect(), border_radius=15)
            okno.blit(s, (SIRKA_OKNA/2 - 250, 20))
            vykresli_text(notifikace_uspechu[0][0], font_maly, BILA, SIRKA_OKNA/2, 50, stred=True, alpha=alpha)

    nove_plovouci_texty = []
    for item in plovouci_texty:
        item[2] -= 1; item[3] -= delta_time
        if item[3] > 0:
            alpha = min(255, int(item[3] * 255))
            vykresli_text(item[0], font_maly, ZLATA, item[1], item[2], alpha=alpha)
            nove_plovouci_texty.append(item)
    plovouci_texty = nove_plovouci_texty

    pygame.display.flip()

if herni_stav == "hra": save_game()
pygame.quit()

