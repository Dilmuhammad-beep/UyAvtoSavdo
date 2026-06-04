# CareTrack Clinic — Tibbiy Yozuvlarni Boshqarish Tizimi (TYBT)

CareTrack Clinic uchun veb-asosidagi tibbiy yozuvlarni boshqarish tizimi. Django + Django REST Framework asosida qurilgan.

## Xususiyatlar

- **Shifokor boshqaruvi** — CRUD: ism, mutaxassislik, bo'lim, aloqa ma'lumotlari
- **Bemor boshqaruvi** — CRUD: shaxsiy ma'lumotlar, biriktirilgan shifokor
- **Kasallik/Tashxis boshqaruvi** — CRUD: ICD kodi, tavsif, og'irlik darajasi
- **To'liq bemor profili** — shifokor + barcha tashxislar ko'rinishi
- **Qidirish va filtrlash** — shifokorlar, bemorlar va kasalliklar bo'ylab
- **Rol asosidagi kirish boshqaruvi:**
  - Administrator — to'liq kirish
  - Klinitsist — bemorlar va kasalliklarni ko'rish/yangilash
  - Qabulxona xodimi — bemorlarni ro'yxatga olish, shifokorlarni ko'rish
- **REST API** — barcha ma'lumotlar uchun to'liq API

## Ma'lumotlar modeli

```
Shifokor (1) ←→ (N) Bemor (1) ←→ (N) Kasallik/Tashxis
```

## O'rnatish

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Testlarni ishga tushirish

```bash
python manage.py test clinic
```

## API Endpointlari

| Endpoint | Tavsif |
|---|---|
| `GET/POST /api/doctors/` | Shifokorlar ro'yxati / yaratish |
| `GET/PUT/PATCH/DELETE /api/doctors/{id}/` | Shifokor tafsilotlari |
| `GET /api/doctors/{id}/patients/` | Shifokor bemorlari |
| `GET/POST /api/patients/` | Bemorlar ro'yxati / yaratish |
| `GET/PUT/PATCH/DELETE /api/patients/{id}/` | Bemor profili (tashxislar bilan) |
| `GET /api/patients/{id}/diseases/` | Bemor kasalliklari |
| `GET/POST /api/diseases/` | Kasalliklar ro'yxati / yaratish |
| `GET/PUT/PATCH/DELETE /api/diseases/{id}/` | Kasallik tafsilotlari |

## Texnologiyalar

- Python / Django 6.x
- Django REST Framework
- django-filter
- SQLite (dev) / PostgreSQL (production)
- Bootstrap 5
