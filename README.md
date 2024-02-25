# User Management FastAPI

Proyek ini adalah sebuah aplikasi web menggunakan FastAPI untuk manajemen pengguna dan tugas. Aplikasi ini dilengkapi dengan otentikasi token JWT untuk melindungi API-nya.

## Instalasi

1. **Buat Virtual Environment Python:**

    ```bash
    python -m venv env
    ```

2. **Aktifkan Virtual Environment:**

    - Di Windows:

        ```bash
        env\Scripts\activate
        ```

    - Di macOS dan Linux:

        ```bash
        source env/bin/activate
        ```

3. **Install Dependensi dari requirements.txt:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Siapkan Database dengan PostgreSQL:**

    - Pastikan Anda memiliki instalasi PostgreSQL yang berjalan.
    - Buatlah sebuah database baru dengan nama yang diinginkan.

5. **Konfigurasi Koneksi Database:**

    - Buat berkas bernama `.env` di direktori proyek Anda jika belum ada.
    - Tambahkan koneksi database Anda ke dalam berkas `.env`. Contoh:

        ```
        URL_DATABASE=postgresql://username:password@localhost:5432/database_name
        ```

6. **Jalankan Aplikasi:**

    Jalankan aplikasi menggunakan Uvicorn:

    ```bash
    uvicorn main:app --reload
    ```

    Aplikasi akan berjalan di `http://localhost:8000`.

## Dokumentasi API

Anda dapat menemukan dokumentasi API lengkap di `http://localhost:8000/docs`.
