# Kodlar Hakkında:
## -)"kod1" Hakkında:
- Rastgele oluşturulmuş bir haritada manuel olarak (ok tuşları kullanılarak) haritalama yapılır.
- Cismin bir engele doğru yaklaştığında engelin üzerinde beliren kırmızı renk menzili temsile eder.
- 's' harfine basınca haritayı matris (.txt) olarak kaydeder(matris örneği sonda bulunuyor). Sadece taranan alanları kaydeder (Kayıt işleminden önce hafıza 2 ile doludur. Eğer ki boş alan görürse 1, engel ile karşılaşırsa 0 ile 2'leri değiştirir).
- Renklerin temsil ettiği şeyler:
  Siyah: Engel
  Kırmızı: Engel var
  Gri: Boş alan
    ## 'kod1'de kullanılan yapılar:
  - Occupancy Grid Mapping (Izgara Tabanlı Haritalama):  Ortam (oda), eşit boyutlu küçük karelere (hücrelere/piksellere) bölünür. Bu kodda GRID_SIZE = 20 ile bu ızgara oluşturulmuştur.
  - Haritalama yapabilmesi için cismin nerde olduğunu bilmesi gerekir. Bunu için de SLAM algoritması kullanıldı.
  - Alan Tarama (Area Scanning) Algoritması: Cismin yerini belirledikten sonra bu algoritma ile haritalama yapılır.
(Burda kullanılan haritalama algoritması, Lidar simülasyonlarında kullanılan Raycasting (Işın Gönderme) algoritmasının işlemciyi yormayan çok daha basit bir alternatifidir. Gerçek bir Lidar simülasyonu olsaydı, robot merkezinden dışarı doğru ışınlar gönderip (Bresenham Algoritması ile) ilk çarptığı duvarı bulmamız gerekirdi.)
  - A* (A-Star) Algoritması: Yol planlama (path planning) için kullanılan algortimadır.

 ## -) "kod2" Hakkında:
 - Alan önceden ayarlıdır ve haritalama otomatik olarak yapılır.
 - Cisim sol üst köşeden başalayacak şekilde ayarlıdır. 
 - Kod içeriğinde alan belirtilmiş olsa da haritalama bu içerikten bağımsız yapılır.
 - Alanın hepsi tarandığında harita matris (.txt) olarak otomatikman kayıtedilir.
 
## -) Matris Örneği:
<img width="803" height="605" alt="resim" src="https://github.com/user-attachments/assets/c61877c4-4edf-4fdb-b9f3-8f8caba858f1" />

Yukardaki alanın matris karşılığı:

<img width="590" height="614" alt="resim" src="https://github.com/user-attachments/assets/94db43ba-322d-436f-9536-915383f2138d" />

