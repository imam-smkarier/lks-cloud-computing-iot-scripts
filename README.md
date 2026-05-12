# LKS Cloud Computing — IoT Scripts (Topic II)

Repository ini berisi source code pendukung untuk **Topic II — IoT Sensor Monitoring System** pada Lomba Kompetensi Siswa (LKS) SMK Cloud Computing **Tingkat Kabupaten Bogor 2026**.

Disediakan oleh **PT SMKarier Inovasi Digital** sebagai panitia penyelenggara & penyedia infrastruktur lomba, agar peserta dan pembimbing memiliki referensi satu sumber yang stabil selama pelaksanaan simulasi maupun hari-H lomba.

> **Acknowledgement:** Repository ini diadaptasi dari repository publik
> [`adhimaswisnuyudo/lks-jabar-2025-cloud-computing-iot`](https://github.com/adhimaswisnuyudo/lks-jabar-2025-cloud-computing-iot)
> dengan perubahan penamaan file, penambahan dokumentasi, serta konteks lomba Kabupaten Bogor 2026.

---

## 📋 Ringkasan Soal Topic II

Peserta membangun pipeline IoT serverless end-to-end di AWS:

```
Python Sensor Simulator  →  AWS IoT Core (MQTT)
         → IoT Rule  →  AWS Lambda (Write)  →  Amazon DynamoDB
                      ↓
                AWS Lambda (Read)  →  Amazon API Gateway  →  Dashboard
```

Semua resource AWS **WAJIB** dibuat di region **`ap-southeast-1` (Asia Pacific — Singapore)**.

---

## 📂 Daftar File

| File | Fungsi |
|------|--------|
| [`pubsub.py`](pubsub.py) | Sensor simulator utama menggunakan AWS IoT Device SDK v2 (AWS CRT). Dipakai setelah men-download *Connection Kit* dari AWS IoT Core. Mem-publish payload JSON berisi `device_id`, `lux`, dan `timestamp`. |
| [`sensor-push.py`](sensor-push.py) | Alternatif sensor simulator sederhana menggunakan library `paho-mqtt`. Cocok jika peserta kesulitan setup AWS CRT. |
| [`lambda_write.py`](lambda_write.py) | Kode Lambda function untuk menulis data sensor ke DynamoDB (dipicu oleh IoT Rule). |
| [`lambda_read.py`](lambda_read.py) | Kode Lambda function untuk membaca data sensor dari DynamoDB (dipublish via API Gateway). |
| [`dashboard.html`](dashboard.html) | Halaman dashboard real-time memakai Chart.js yang menampilkan data sensor dari endpoint API Gateway. |

### 📎 Mapping Perubahan Nama dari Repo Referensi

| Nama Lama (repo referensi) | Nama Baru (repo ini) |
|---|---|
| `Lambda Function.py` | `lambda_write.py` |
| `Lambda Api.py` | `lambda_read.py` |
| `pubsub.py` | `pubsub.py` (tidak berubah) |
| `sensor-push.py` | `sensor-push.py` (tidak berubah) |
| `dashboard.html` | `dashboard.html` (tidak berubah) |

> Nama file Python dibuat tanpa spasi dan memakai format `snake_case` agar konsisten dengan konvensi Python dan lebih mudah di-import/rename oleh peserta.

---

## 🔧 Cara Menggunakan

### 1. Sensor Simulator (`pubsub.py` atau `sensor-push.py`)

**Prasyarat di laptop peserta (sudah diinstall sebelum hari-H):**
- Python 3.x
- pip
- `paho-mqtt==1.5.0`
- Code editor (VSCode, Sublime, dll)

**Langkah:**
1. Buat `IoT Thing` di AWS IoT Core → klik **Connect one device** → pilih **Python SDK**.
2. Download **Connection Kit** → extract ke folder kerja.
3. Ganti `pubsub.py` bawaan SDK dengan file [`pubsub.py`](pubsub.py) dari repository ini.
4. Sesuaikan variabel `device_id` di dalam `pubsub.py` dengan ID peserta, contoh:
   ```python
   "device_id": "sensor-smkn1cibinong-01"
   ```
5. Pastikan IoT Policy mengizinkan `iot:Connect`, `iot:Publish`, `iot:Receive`, `iot:Subscribe`.
6. Set topic publish ke format: `sdk/sensor/{candidate-id}`, contoh `sdk/sensor/smkn1cibinong-01`.
7. Jalankan `start.sh` (Linux/macOS) atau `start.exe` (Windows) dari Connection Kit.

### 2. Lambda Write (`lambda_write.py`)

1. Buat Lambda function dengan runtime **Python 3.12** (atau terbaru).
2. Copy isi [`lambda_write.py`](lambda_write.py) ke dalam code editor Lambda.
3. **Wajib:** ganti nilai `'Your Table Name'` dengan nama tabel DynamoDB milik peserta, contoh:
   ```python
   table = dynamodb.Table('DynamoDBSmkn1cibinong01')
   ```
4. Attach IAM Policy custom yang mengizinkan `dynamodb:PutItem` pada tabel tersebut.
5. Tambah trigger dari **IoT Rule** yang memilih pesan dari topic yang sesuai.

### 3. Lambda Read (`lambda_read.py`)

1. Buat Lambda function baru (runtime Python 3.12 atau terbaru).
2. Copy isi [`lambda_read.py`](lambda_read.py).
3. Ganti nilai `'Your Table Name'` dengan nama tabel DynamoDB peserta.
4. Attach IAM Policy custom yang mengizinkan `dynamodb:Scan` atau `dynamodb:Query`.
5. Tambahkan trigger **API Gateway** (REST atau HTTP API, dengan security **Open**).

### 4. Dashboard (`dashboard.html`)

1. Download / save file [`dashboard.html`](dashboard.html).
2. Edit bagian `fetch('Your Endpoint')` → ganti dengan URL API Gateway peserta.
3. Ganti judul `<h2>(NamaKota/Kab)</h2>` dengan identitas peserta.
4. Buka file di browser. Dashboard akan meng-fetch data setiap 5 detik.
5. **Bonus:** host file ini di Amazon S3 + CloudFront untuk poin tambahan.

---

## 🏷️ Aturan Penamaan IAM (Wajib Diikuti Peserta)

Untuk keamanan akun AWS panitia, **IAM Role dan custom IAM Policy yang dibuat peserta untuk Lambda WAJIB menggunakan prefix `LKS-`**. Contoh yang benar:

| Resource | Contoh Nama |
|---|---|
| Lambda Execution Role | `LKS-LambdaSensor-smkn1cibinong-01` |
| Lambda Execution Role (API) | `LKS-LambdaApiGateway-smkn1cibinong-01` |
| Custom Policy (Write) | `LKS-LambdaPutDataIntoDynamoDB-smkn1cibinong-01` |
| Custom Policy (Read) | `LKS-LambdaApiGetDynamoDB-smkn1cibinong-01` |

> Jika peserta **tidak** memakai prefix `LKS-`, AWS akan menolak (Access Denied) saat:
> - Membuat role
> - Attach policy ke role
> - Pass role ke Lambda

Penamaan resource AWS lainnya (IoT Thing, DynamoDB Table, Lambda, API Gateway, IoT Rule) mengikuti konvensi dokumen **Exam Blueprint Topic II**.

---

## 🌏 Region Wajib

Semua resource AWS harus dibuat di:

```
Asia Pacific (Singapore) — ap-southeast-1
```

Pembuatan resource di region lain akan ditolak oleh policy IAM panitia.

---

## 🚫 Catatan Keamanan

Repository ini **TIDAK** berisi:
- ❌ AWS Access Key / Secret Key
- ❌ Certificate `.pem`, `.crt`, `.key`
- ❌ File `.env` atau credential lainnya
- ❌ Endpoint AWS IoT / API Gateway yang spesifik

Semua credential & endpoint akan didapatkan peserta saat membuat resource sendiri di akun AWS masing-masing.

---

## 📞 Kontak

**PT SMKarier Inovasi Digital**
- 🌐 Website: [smkarier.co.id](https://smkarier.co.id)
- 🎓 Portal LKS: [lksbogor.smkarier.co.id](https://lksbogor.smkarier.co.id)
- ✉️ Head Judge: imam@smkarier.co.id (Imam Najmudin, S.Kom)
- ✉️ Assistant Judge: Alfian Maulana, S.Kom

---

## 📄 Lisensi

Kode pada repository ini diadaptasi dari repo publik untuk kepentingan pendidikan & kompetisi. Silakan digunakan secara bebas oleh peserta LKS untuk latihan dan pelaksanaan lomba.

_Disusun oleh tim panitia LKS Cloud Computing — Kabupaten Bogor 2026._
