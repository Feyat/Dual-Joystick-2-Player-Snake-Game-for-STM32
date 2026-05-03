# STM32 Çift Joystick ile 2 Oyunculu Yılan Oyunu

Bir STM32 mikrodenetleyici projesi. İki joystick'ten okunan analog veriler ADC + DMA ile işlenir, UART üzerinden bilgisayara aktarılır ve Python/Pygame ile çalışan iki kişilik bir yılan oyununu kontrol eder.

---

## İçindekiler

- [Proje Özeti](#proje-özeti)
- [Sistem Mimarisi](#sistem-mimarisi)
- [Donanım Gereksinimleri](#donanım-gereksinimleri)
- [STM32 Tarafı](#stm32-tarafı)
- [Python Tarafı](#python-tarafı)
- [Kurulum ve Çalıştırma](#kurulum-ve-çalıştırma)
- [Oyun Kuralları](#oyun-kuralları)
- [Lisans](#lisans)

---

## Proje Özeti

Bu proje, STM32 mikrodenetleyicisi üzerinde iki adet analog joystick'ten ADC (Analog-Dijital Dönüştürücü) ve DMA (Direct Memory Access) kullanılarak veri okunmasını, bu verilerin UART protokolü ile seri port üzerinden bilgisayara aktarılmasını ve Python ortamında Pygame kütüphanesi ile görselleştirilen 2 oyunculu bir Snake (yılan) oyununun kontrol edilmesini kapsamaktadır.

**Temel Özellikler:**
- ADC + DMA ile doğrudan RAM'e yazılan joystick verileri
- DMA kesmesi içinde yapılandırılmış UART veri gönderimi
- 2 oyunculu gerçek zamanlı yılan oyunu
- Seri port üzerinden 115200 baud hızında iletişim

---

## Sistem Mimarisi

```
┌─────────────────────────────────┐         ┌──────────────────────────────┐
│          STM32 MCU              │         │        Bilgisayar (Mac)      │
│                                 │         │                              │
│  Joystick 1 (X, Y)             │         │  Python + Pygame             │
│      │                          │  UART   │                              │
│      ▼                          │ ──────► │  Seri Port Okuma             │
│  ADC ──► DMA ──► RAM            │115200   │      │                       │
│                   │             │  baud   │      ▼                       │
│  Joystick 2 (X, Y)             │         │  Yön Hesaplama               │
│      │             │            │         │      │                       │
│      ▼             ▼            │         │      ▼                       │
│  ADC ──► DMA   UART TX          │         │  Snake Oyunu Render          │
└─────────────────────────────────┘         └──────────────────────────────┘
```

Veri akışı: `Joystick → ADC → DMA → RAM → DMA Kesmesi → UART → Seri Port → Python`

---

## Donanım Gereksinimleri

| Bileşen | Adet | Açıklama |
|--------|------|----------|
| STM32 geliştirme kartı | 1 | (F4 veya benzeri serisi önerilir) |
| Analog joystick modülü | 2 | X ve Y eksenli, 3.3V uyumlu |
| USB-UART dönüştürücü | 1 | `/dev/tty.usbserial-0001` portu |
| Bağlantı kabloları | — | |

**Joystick Bağlantı Pinleri:**
- Oyuncu 1 → ADC Kanal 1 (X ekseni), ADC Kanal 2 (Y ekseni)
- Oyuncu 2 → ADC Kanal 3 (X ekseni), ADC Kanal 4 (Y ekseni)

---

## STM32 Tarafı

### ADC + DMA Yapılandırması

- İki joystick'in X ve Y eksenleri olmak üzere toplam **4 kanal** ADC ile okunur.
- DMA, ADC verilerini doğrudan RAM'e taşır; bu sayede CPU yükü minimize edilir.
- Tüm örnekleme işlemi **DMA kesmesi** tamamlandığında tetiklenir.

### UART Veri Gönderimi

- DMA kesmesi içinde 4 ADC değeri virgülle ayrılmış format olarak UART'tan gönderilir.
- **Baud rate:** 115200
- **Format:** `P1_X,P1_Y,P2_X,P2_Y\n`
- **Örnek:** `512,10,300,1020\n`

---

## Python Tarafı

### Bağımlılıklar

```bash
pip install pygame pyserial
```

### Dosya: `play.py`

| Fonksiyon | Açıklama |
|-----------|----------|
| `normalize(value)` | Ham ADC değerini 0 / 1 / 2 (sol/sağ/nötr, yukarı/aşağı/nötr) olarak yorumlar |
| `update_direction(x, y, current_dir)` | Normalize edilmiş değerden yılanın hareket yönünü günceller |
| `move_snake(snake, direction)` | Yılanı bir adım ilerletir |
| `grow_snake(snake, direction)` | Yılana yeni segment ekler |
| `check_collision(snake, other_snake)` | Duvar ve yılan çarpışmalarını kontrol eder |
| `spawn_food(snake1, snake2)` | Yılanların üstüne denk gelmeyecek şekilde yem oluşturur |
| `reset_game()` | Oyunu başlangıç durumuna getirir |

### ADC Normalize Mantığı

```
Ham değer < 7      → 0  (minimum → sol veya aşağı)
Ham değer > 300    → 1  (maksimum → sağ veya yukarı)
Arada kalan        → 2  (nötr → yön değişmez)
```

### Ekran Ayarları

| Parametre | Değer |
|-----------|-------|
| Ekran boyutu | 600 × 400 piksel |
| Hücre boyutu | 20 × 20 piksel |
| FPS | 1 (yavaş mod, artırılabilir) |
| Oyuncu 1 rengi | Yeşil |
| Oyuncu 2 rengi | Mavi |
| Yem rengi | Kırmızı |

---

## Kurulum ve Çalıştırma

### 1. STM32 Firmware

1. STM32CubeIDE ile projeyi açın (`stm32project-main 2`).
2. ADC, DMA ve UART yapılandırmalarını kontrol edin.
3. Firmware'i karta yükleyin.

### 2. Python Oyununu Başlatma

```bash
# Bağımlılıkları kur
pip install pygame pyserial

# Seri port adını kontrol et (Mac için)
ls /dev/tty.usbserial-*

# Gerekirse play.py içindeki port adını güncelle
# ser = serial.Serial('/dev/tty.usbserial-0001', 115200, timeout=0.01)

# Oyunu çalıştır
python play.py
```

> **Not:** Windows'ta port adı `COM3`, `COM4` vb. olacaktır. Linux'ta `/dev/ttyUSB0` şeklinde görünebilir.

---

## Oyun Kuralları

- Her oyuncu kendi joystick'i ile yılanını yönlendirir.
- Kırmızı yeme ulaşan yılan büyür ve 1 puan kazanır.
- Yılan duvara veya herhangi bir yılana (kendi dahil) çarparsa **o oyuncu kaybeder** ve oyun sıfırlanır.
- Skor ekranın sol üst köşesinde `P1: X  P2: Y` şeklinde gösterilir.

---

## Lisans

Bu proje **Apache License 2.0** ile lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakınız.
