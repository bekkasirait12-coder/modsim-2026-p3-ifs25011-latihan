import streamlit as st
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 
import datetime

st.set_page_config(page_title="Simulasi Piket IT Del", layout="wide")

# ===============================
# SIDEBAR WAKTU
# ===============================
st.sidebar.header("⏰ Pengaturan Waktu")

jam_mulai = st.sidebar.time_input(
    "Pilih Jam Mulai Piket:",
    value=datetime.time(7, 0)
)

# Styling Sidebar
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #ffc0cb;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Simulasi Sistem Piket IT Del")
st.markdown("Simulasi proses pengisian ompreng untuk sistem piket.")

# ===============================
# Sidebar Parameter
# ===============================
st.sidebar.header("⚙️ Parameter Simulasi")

total_mahasiswa_yang_piket = st.sidebar.number_input("Jumlah Mahasiswa yang Piket", value=7)
total_meja = st.sidebar.number_input("Jumlah Meja", value=60)
mahasiswa_per_meja = st.sidebar.number_input("Mahasiswa per Meja", value=3)

min_lauk = st.sidebar.number_input("Min Waktu Lauk (detik)", value=30)
max_lauk = st.sidebar.number_input("Max Waktu Lauk (detik)", value=60)

min_nasi = st.sidebar.number_input("Min Waktu Nasi (detik)", value=30)
max_nasi = st.sidebar.number_input("Max Waktu Nasi (detik)", value=60)

min_angkat = st.sidebar.number_input("Min Waktu Angkat (detik)", value=20)
max_angkat = st.sidebar.number_input("Max Waktu Angkat (detik)", value=60)

# ===============================
# SIMULASI
# ===============================
if st.button("🚀 Jalankan Simulasi"):

    TOTAL_OMPRENG = total_meja * mahasiswa_per_meja

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
        waktu_lauk = random.uniform(min_lauk, max_lauk)
        total_lauk += waktu_lauk
        waktu_lauk_selesai += waktu_lauk / total_mahasiswa_yang_piket

        # ===============================
        # PROSES ANGKAT (BATCH)
        # ===============================
        counter_batch += 1

        if counter_batch >= batch_size:
            waktu_angkat = random.uniform(min_angkat, max_angkat)
            total_angkat += waktu_angkat
            waktu_angkat_selesai = max(waktu_lauk_selesai, waktu_angkat_selesai) + (waktu_angkat / total_mahasiswa_yang_piket)

            batch_counter_data.append(batch_size)

            counter_batch = 0
            batch_size = random.randint(4, 7)

        # ===============================
        # PROSES NASI
        # ===============================
        waktu_nasi = random.uniform(min_nasi, max_nasi)
        total_nasi += waktu_nasi
        waktu_nasi_selesai = max(waktu_angkat_selesai, waktu_nasi_selesai) + (waktu_nasi / total_mahasiswa_yang_piket)

        data.append({
            "Ompreng": i + 1,
            "Waktu Selesai (detik)": waktu_nasi_selesai
        })

    # ===============================
    # PERHITUNGAN WAKTU SELESAI REAL
    # ===============================
    total_detik = waktu_nasi_selesai
    total_menit = total_detik / 60

    waktu_mulai_datetime = datetime.datetime.combine(
        datetime.date.today(), jam_mulai
    )

    waktu_selesai_datetime = waktu_mulai_datetime + datetime.timedelta(
        seconds=total_detik
    )

    jam_selesai_str = waktu_selesai_datetime.strftime("%H:%M:%S")

    # ===============================
    # PERHITUNGAN UTILISASI
    # ===============================
    total_waktu_proses = total_lauk + total_angkat + total_nasi
    kapasitas_maks = total_mahasiswa_yang_piket * total_detik

    utilisasi = (total_waktu_proses / kapasitas_maks) * 100 if kapasitas_maks > 0 else 0

    st.success("Simulasi Selesai!")

    # ===============================
    # METRIC
    # ===============================
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Ompreng", TOTAL_OMPRENG)
    col2.metric("Total Waktu (menit)", f"{total_menit:.2f}")
    col3.metric("Selesai Pukul", jam_selesai_str)
    col4.metric("Utilisasi (%)", f"{utilisasi:.2f}%")

    # ===============================
    # DATAFRAME
    # ===============================
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
    # BAR CHART - TOTAL WAKTU
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
    # GAUGE CHART UTILISASI
    # ===============================
    st.subheader("📈 Gauge Utilisasi Sistem")

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=utilisasi,
        title={'text': "Utilisasi Sistem (%)"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgreen"},
                {'range': [50, 80], 'color': "yellow"},
                {'range': [80, 100], 'color': "red"},
            ],
        }
    ))

    st.plotly_chart(fig_gauge, use_container_width=True)

    # ===============================
    # RATA-RATA WAKTU
    # ===============================
    st.subheader("📊 Rata-rata Waktu per Proses")

    estimasi_batch = len(batch_counter_data) if len(batch_counter_data) > 0 else 1

    df_avg = pd.DataFrame({
        "Proses": ["Lauk", "Angkat", "Nasi"],
        "Rata-rata Waktu (detik)": [
            total_lauk / TOTAL_OMPRENG,
            total_angkat / estimasi_batch,
            total_nasi / TOTAL_OMPRENG
        ]
    })

    fig_avg = px.bar(
        df_avg,
        x="Proses",
        y="Rata-rata Waktu (detik)",
        title="Rata-rata Waktu per Proses"
    )

    st.plotly_chart(fig_avg, use_container_width=True)

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
    # STATISTIK TAMBAHAN
    # ===============================
    st.subheader("📊 Statistik Tambahan")

    st.write(f"Rata-rata waktu per ompreng: {total_detik/TOTAL_OMPRENG:.2f} detik")
    st.write(f"Total waktu dalam jam: {total_menit/60:.2f} jam")
    st.write(f"Waktu selesai terakhir: {jam_selesai_str}")
    st.write(f"Rata-rata utilisasi sistem: {utilisasi:.2f}%")

    # Identifikasi Bottleneck
    bottleneck = max(
        [("Lauk", total_lauk), 
         ("Angkat", total_angkat), 
         ("Nasi", total_nasi)],
        key=lambda x: x[1]
    )

    st.warning(f"⚠️ Bottleneck sistem berada pada proses: **{bottleneck[0]}**")