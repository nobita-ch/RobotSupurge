import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import os

def haritayi_gorsellestir(matris):
    """
    Girilen 0 ve 1 matrisini görselleştirir.
    """
    # Matris boşsa işlem yapma
    if not matris:
        return

    # Numpy array'e çevirelim (işlemesi daha kolay)
    np_matris = np.array(matris)

    # Renkler: 0 -> Mavi, 1 -> Yeşil
    renk_listesi = ['#42a5f5', '#66bb6a'] 
    cmap = colors.ListedColormap(renk_listesi)
    
    sinirlar = [0, 1, 2]
    norm = colors.BoundaryNorm(sinirlar, cmap.N)

    plt.figure(figsize=(8, 8))
    
    im = plt.imshow(np_matris, cmap=cmap, norm=norm)
    
    # Izgaralar
    plt.grid(which='major', color='white', linestyle='-', linewidth=2)
    plt.xticks(np.arange(-0.5, len(np_matris[0]), 1), labels=[])
    plt.yticks(np.arange(-0.5, len(np_matris), 1), labels=[])
    
    # Lejant (Renk Anahtarı)
    cbar = plt.colorbar(im, ticks=[0.5, 1.5], fraction=0.046, pad=0.04)
    cbar.ax.set_yticklabels(['0 - Engel', '1 - Boşluk'])
    
    plt.title(f"Dosyadan Yüklenen Harita ({len(np_matris)}x{len(np_matris[0])})")
    plt.tick_params(bottom=False, left=False) 
    plt.show()

def dosyadan_matris_oku():
    print("--- Dosyadan Harita Yükleyici ---")
    print("Lütfen harita verisinin olduğu txt dosyasının adını girin.")
    print("Örnek dosya formatı:")
    print("0 0 1 0")
    print("1 1 1 0")
    print("---------------------------------")
    
    dosya_yolu = input("Dosya adı (örn: harita.txt): ").strip()

    if not os.path.exists(dosya_yolu):
        print(f"\nHATA: '{dosya_yolu}' adında bir dosya bulunamadı.")
        return None

    matris = []
    
    try:
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            for satir_no, satir in enumerate(lines):
                # Satırdaki boşlukları temizle ve parçala
                satir = satir.strip()
                if not satir: continue # Boş satırları atla
                
                elemanlar = satir.split()
                
                # Sayıya çevir ve kontrol et
                try:
                    sayisal_satir = [int(x) for x in elemanlar]
                except ValueError:
                    print(f"HATA: {satir_no+1}. satırda sayı olmayan karakterler var.")
                    return None

                # Sadece 0 ve 1 kontrolü
                if any(x not in [0, 1] for x in sayisal_satir):
                    print(f"HATA: {satir_no+1}. satırda 0 ve 1 dışında rakamlar var.")
                    return None
                
                matris.append(sayisal_satir)
        
        # Matrisin dikdörtgen olup olmadığını kontrol et (tüm satırlar eşit uzunlukta mı?)
        ilk_satir_uzunlugu = len(matris[0])
        for i, satir in enumerate(matris):
            if len(satir) != ilk_satir_uzunlugu:
                print(f"HATA: Matris düzgün değil! {i+1}. satırın uzunluğu farklı.")
                return None
                
        return matris

    except Exception as e:
        print(f"Bir hata oluştu: {e}")
        return None

# --- Programı Başlat ---
if __name__ == "__main__":
    veri = dosyadan_matris_oku()
    if veri is not None:
        print("\nHarita başarıyla yüklendi, çiziliyor...")
        haritayi_gorsellestir(veri)