import streamlit as st
import random
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Simulasi Piket IT Del", layout="wide")

st.title("📊 Simulasi Sistem Piket IT Del")
st.markdown("Simulasi proses pengisian ompreng untuk sistem piket.")

# ===============================
# KONSTANTA SESUAI KETENTUAN
# ===============================
JUMLAH_MAHASISWA_PIKET = 7
TOTAL_MEJA = 60
MAHASISWA_PER_MEJA = 3
TOTAL_OMPRENG = TOTAL_MEJA * MAHASISWA_PER_MEJA

# Rentang waktu sesuai narasi
MIN_LAUK, MAX_LAUK = 30, 60
MIN_NASI, MAX_NASI = 30, 60
MIN_ANGKAT, MAX_ANGKAT = 20, 60

# ===============================
# SIMULASI
# ===============================
if st.button("🚀 Jalankan Simulasi"):

    waktu_lauk_selesai = 0
    waktu_angkat_selesai = 0
    waktu_nasi_selesai = 0

    total_lauk = 0
    total_nasi = 0
    total_angkat = 0

    data = []
    batch_counter_data = []

    batch_size = random.randint(4, 7)
    counter_batch = 0

    for i in range(TOTAL_OMPRENG):

        # ===============================
        # PROSES LAUK
        # ===============================
        waktu_lauk = random.uniform(MIN_LAUK, MAX_LAUK)
        total_lauk += waktu_lauk
        waktu_lauk_selesai += waktu_lauk

        # ===============================
        # PROSES ANGKAT (BATCH 4–7)
        # ===============================
        counter_batch += 1

        if counter_batch >= batch_size:
            waktu_angkat = random.uniform(MIN_ANGKAT, MAX_ANGKAT)
            total_angkat += waktu_angkat
            waktu_angkat_selesai = max(waktu_lauk_selesai, waktu_angkat_selesai) + waktu_angkat

            batch_counter_data.append(batch_size)

            counter_batch = 0
            batch_size = random.randint(4, 7)

        # ===============================
        # PROSES NASI
        # ===============================
        waktu_nasi = random.uniform(MIN_NASI, MAX_NASI)
        total_nasi += waktu_nasi
        waktu_nasi_selesai = max(waktu_angkat_selesai, waktu_nasi_selesai) + waktu_nasi

        data.append({
            "Ompreng": i + 1,
            "Waktu Selesai (detik)": waktu_nasi_selesai
        })

    # ===============================
    # OUTPUT
    # ===============================
    total_detik = waktu_nasi_selesai
    total_menit = total_detik / 60
    jam_selesai = 7 + (total_menit / 60)

    st.success("Simulasi Selesai!")

    st.info(
        f"""
        👥 Mahasiswa Piket: {JUMLAH_MAHASISWA_PIKET} orang  
        🍱 Total Ompreng: {TOTAL_OMPRENG} ompreng  
        🏫 Total Meja: {TOTAL_MEJA} meja  
        🕖 Mulai: 07.00 WIB
        """
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Waktu (menit)", f"{total_menit:.2f}")
    col2.metric("Estimasi Selesai", f"{jam_selesai:.2f} WIB")
    col3.metric("Rata-rata per Ompreng", f"{total_detik/TOTAL_OMPRENG:.2f} detik")

    df = pd.DataFrame(data)

    # ===============================
    # LINE CHART
    # ===============================
    st.subheader("📈 Grafik Progres Penyelesaian Ompreng")

    fig_line = px.line(
        df,
        x="Ompreng",
        y="Waktu Selesai (detik)",
        title="Progres Penyelesaian Ompreng"
    )

    st.plotly_chart(fig_line, use_container_width=True)

    # ===============================
    # TOTAL WAKTU PER PROSES
    # ===============================
    st.subheader("📊 Total Waktu per Proses")

    df_proses = pd.DataFrame({
        "Proses": ["Lauk", "Angkat", "Nasi"],
        "Total Waktu (detik)": [total_lauk, total_angkat, total_nasi]
    })

    fig_proses = px.bar(
        df_proses,
        x="Proses",
        y="Total Waktu (detik)",
        title="Total Waktu per Tahap Proses"
    )

    st.plotly_chart(fig_proses, use_container_width=True)

    # ===============================
    # DISTRIBUSI BATCH
    # ===============================
    st.subheader("📊 Distribusi Ukuran Batch Angkat")

    if len(batch_counter_data) > 0:
        df_batch = pd.DataFrame({
            "Ukuran Batch": batch_counter_data
        })

        df_batch_count = df_batch.value_counts().reset_index()
        df_batch_count.columns = ["Ukuran Batch", "Frekuensi"]

        fig_batch = px.bar(
            df_batch_count,
            x="Ukuran Batch",
            y="Frekuensi",
            title="Distribusi Ukuran Batch"
        )

        st.plotly_chart(fig_batch, use_container_width=True)

    # ===============================
    # IDENTIFIKASI BOTTLENECK
    # ===============================
    bottleneck = max(
        [("Lauk", total_lauk),
         ("Angkat", total_angkat),
         ("Nasi", total_nasi)],
        key=lambda x: x[1]
    )

    st.warning(f"⚠️ Bottleneck sistem berada pada proses: **{bottleneck[0]}**")