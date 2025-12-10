# Kodlar Hakkında:
## -)"kod1" Hakkında:
- Rastgele oluşturulmuş bir haritada manuel olarak (ok tuşları kullanılarak) haritalama yapılır.
- Cismin bir engele doğru yaklaştığında engelin üzerinde beliren kırmızı renk menzili temsile eder.
- 's' harfine basınca haritayı matris (.txt) olarak kaydeder(matris örneği sonda bulunuyor). Sadece taranan alanları kaydeder (Kayıt işleminden önce hafıza 2 ile doludur. Eğer ki boş alan görürse 1, engel ile karşılaşırsa 0 ile 2'leri değiştirir).
- Tarama işlemi bitmeden taranan yerlerden bir yer seçerek cismin o yere gitmesi sağlanır. Eğer ki yol boyunca (mavi ile belirtilen çizgi boyunca) taranmamış bir alan görünürse taranır.
- Renklerin temsil ettiği şeyler:
  Siyah: Engel
  Kırmızı: Engel var
  Gri: Boş alan

  
 ## -)"kod2" Hakkında:
 - Alan önceden ayarlıdır ve haritalama otomatik olarak yapılır.
 - Cisim sol üst köşeden başalayacak şekilde ayarlıdır. 
 - Kod içeriğinde alan belirtilmiş olsa da haritalama bu içerikten bağımsız yapılır.
 - Alanın hepsi tarandığında harita matris (.txt) olarak otomatikman kayıtedilir.
 - Tarama işlemi bitmeden yol oluşturmak için seçim yapılamaz. Tarama işlemi bittikten sonra gidilmesi istenilen yer seçilir (mavi çizgi yolu temsil eder.).
 - Renklerin temsil ettiği şeyler:
  Siyah: Engel
  Gri: Boş alan

## -)"kod3" Hakkında:
- 'kod2' ile aynı çalışma mantığına sahiptir. Tek farkı belirlenmiş tuşa basınca keşif işleminin durdurulmasıdır.
- Keşif işlemi durdurulduğu zaman gidilecek yerin seçilmesi istenilir ve 'kod1'deki gibi tarama ve haritalama işlemlerine devam eder.
- Renklerin temsil ettiği şeyler:
  Siyah: Engel
  Gri: Boş alan
 
## -) Matris Örneği:
- 'MatrisOkuma' adlı sayfada, haritalama sonucunda ortaya çıkmış txt belgelerini görsele çevirme işlemi yapılmaktadır
- Kod çalıştırıldığı zaman txt belgesinin ismini ister
  
<img width="803" height="605" alt="resim" src="https://github.com/user-attachments/assets/c61877c4-4edf-4fdb-b9f3-8f8caba858f1" />

Yukardaki alanın matris karşılığı:

<img width="590" height="614" alt="resim" src="https://github.com/user-attachments/assets/94db43ba-322d-436f-9536-915383f2138d" />

