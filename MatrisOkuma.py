import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import os

def haritayi_gorsellestir(matris, mod):
    """
    Matrisi seçilen moda göre renklendirip görselleştirir.
    mod 1: 0 (Engel), 1 (Boşluk)
    mod 2: 0 (Engel), 1 (Boşluk), 2 (Bilinmiyor)
    """
    if not matris:
        return

    np_matris = np.array(matris)
    plt.figure(figsize=(8, 8))

    if mod == 1:
        # --- MOD 1: Sadece 0 ve 1 ---
        # 0: Siyah (Engel), 1: Beyaz (Boşluk)
        renk_listesi = ['black', 'white']
        etiketler = ['0 - Engel', '1 - Boşluk']
        sinirlar = [-0.5, 0.5, 1.5]
        ticks = [0, 1]
    
    else:
        # --- MOD 2: 0, 1 ve 2 ---
        # 0: Siyah (Engel), 1: Beyaz (Boşluk), 2: Gri (Bilinmiyor)
        renk_listesi = ['black', 'white', 'gray']
        etiketler = ['0 - Engel', '1 - Boşluk', '2 - Bilinmiyor']
        sinirlar = [-0.5, 0.5, 1.5, 2.5]
        ticks = [0, 1, 2]

    cmap = colors.ListedColormap(renk_listesi)
    norm = colors.BoundaryNorm(sinirlar, cmap.N)

    im = plt.imshow(np_matris, cmap=cmap, norm=norm)
    
    # Izgaralar
    plt.grid(which='major', color='gray', linestyle='-', linewidth=0.5)
    plt.xticks(np.arange(-0.5, len(np_matris[0]), 1), labels=[])
    plt.yticks(np.arange(-0.5, len(np_matris), 1), labels=[])
    
    # Lejant (Renk Anahtarı)
    cbar = plt.colorbar(im, ticks=ticks, fraction=0.046, pad=0.04)
    cbar.ax.set_yticklabels(etiketler)
    
    baslik = "Harita: Engel(0) - Boşluk(1)" if mod == 1 else "Harita: Engel(0) - Boşluk(1) - Bilinmiyor(2)"
    plt.title(f"{baslik}\nBoyut: {len(np_matris)}x{len(np_matris[0])}")
    plt.tick_params(bottom=False, left=False) 
    plt.show()

def dosyadan_matris_oku(mod):
    """
    Kullanıcıdan dosya adı alır, yorum satırlarını atlar 
    ve seçilen moda uygun olup olmadığını denetler.
    """
    gecerli_sayilar = [0, 1] if mod == 1 else [0, 1, 2]
    mod_adi = "0 ve 1" if mod == 1 else "0, 1 ve 2"

    print(f"\n--- {mod_adi} İçeren Dosya Okuma Modu ---")
    print(f"Lütfen sadece {mod_adi} rakamlarını içeren txt dosyasının adını girin.")
    dosya_yolu = input("Dosya adı (örn: harita.txt): ").strip()

    if not os.path.exists(dosya_yolu):
        print(f"\nHATA: '{dosya_yolu}' adında bir dosya bulunamadı.")
        return None

    matris = []
    
    try:
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            for satir_no, satir in enumerate(lines):
                satir = satir.strip()
                
                # 1. Boş satırları atla
                if not satir: continue 
                
                # 2. Yorum satırlarını atla (# ile başlayanlar) - GÜNCELLENEN KISIM
                if satir.startswith('#'): continue

                # Satır içi yorumları temizle (Örn: "0 0 1 # Bu bir duvar")
                if '#' in satir:
                    satir = satir.split('#')[0].strip()
                    if not satir: continue # Eğer yorumdan önce bir şey yoksa atla
                
                elemanlar = satir.split()
                
                try:
                    sayisal_satir = [int(x) for x in elemanlar]
                except ValueError:
                    print(f"HATA: {satir_no+1}. satırda sayı olmayan karakterler var.")
                    return None

                # Seçilen moda göre sayı kontrolü
                if any(x not in gecerli_sayilar for x in sayisal_satir):
                    print(f"HATA: {satir_no+1}. satırda {gecerli_sayilar} dışında rakamlar var.")
                    print(f"Seçilen Mod: {mod} (Sadece {mod_adi} kabul edilir)")
                    return None
                
                matris.append(sayisal_satir)
        
        # Dikdörtgenlik kontrolü
        if matris:
            ilk_satir_uzunlugu = len(matris[0])
            for i, satir in enumerate(matris):
                if len(satir) != ilk_satir_uzunlugu:
                    print(f"HATA: Matris düzgün değil! {i+1}. satırın (yorumsuz) uzunluğu farklı.")
                    return None
        else:
            print("HATA: Dosyada geçerli veri bulunamadı (Tüm satırlar boş veya yorum olabilir).")
            return None
                
        return matris

    except Exception as e:
        print(f"Bir hata oluştu: {e}")
        return None

# --- Programı Başlat ---
if __name__ == "__main__":
    while True:
        print("\n--- HARİTA GÖRSELLEŞTİRİCİ ---")
        print("1. Sadece 0 ve 1 (Engel / Boşluk)")
        print("2. 0, 1 ve 2 (Engel / Boşluk / Bilinmiyor)")
        print("Q. Çıkış")
        
        secim = input("Seçiminiz (1/2/Q): ").strip().upper()
        
        if secim == 'Q':
            print("Programdan çıkılıyor...")
            break
        elif secim == '1':
            veri = dosyadan_matris_oku(mod=1)
            if veri is not None:
                print("\nHarita başarıyla yüklendi, çiziliyor...")
                haritayi_gorsellestir(veri, mod=1)
        elif secim == '2':
            veri = dosyadan_matris_oku(mod=2)
            if veri is not None:
                print("\nHarita başarıyla yüklendi, çiziliyor...")
                haritayi_gorsellestir(veri, mod=2)
        else:
            print("Geçersiz seçim, lütfen tekrar deneyin.")
