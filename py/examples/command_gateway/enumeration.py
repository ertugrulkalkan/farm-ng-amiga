from enum import Enum


class EnMessageType(Enum):
    Task = 0                  # Görev mesajları (Merkez → Araç)
    LivePosition = 1          # Canlı konum mesajı (Araç → Merkez)
    TaskStatus = 2            # Görev durumu mesajı (Araç → Merkez)
    InventoryRequest = 3      # Envanter sorgulama isteği (Merkez → Araç)
    InventoryResponse = 4     # Envanter bilgisi yanıtı (Araç → Merkez)
    DeviceInfoRequest = 5     # Cihaz ID ve yazılım versiyonu sorgulama (Merkez → Araç)
    DeviceInfoResponse = 6    # Cihaz bilgisi yanıtı (Araç → Merkez)
    ErrorMessage = 7          # Hata mesajı (Araç → Merkez)


class EnTaskType(Enum):
    TrackTask = 0          # Belirli noktaları takip etme
    Cultivation = 1        # Çapalama görevi
    Transport = 2          # Yük taşıma görevi
    Scanning = 3           # Sensörle tarama (örneğin toprak analizi)
    Spraying = 4           # İlaç püskürtme görevi
    ReturnToBase = 5       # Ana noktaya dönüş
    Charging = 6           # Şarj istasyonuna gitme
    Maintenance = 7        # Bakım noktasına gitme


class EnTaskStatus(Enum):
    Pending = 0       # Beklemede
    InProgress = 1    # Devam ediyor
    Completed = 2     # Tamamlandı
    Failed = 3        # Hata oluştu


class EnHbridgeStatus(Enum):
    IdleUp = 0        # Beklemede
    IdleDown = 1      # Devam ediyor
    MovingUp = 2      # Tamamlandı
    MovingDown = 3    # Hata oluştu


class EnTrackType(Enum):
    None_ = 0         # None is a reserved keyword in Python, so using None_
    Move = 1
    Rotate = 2
