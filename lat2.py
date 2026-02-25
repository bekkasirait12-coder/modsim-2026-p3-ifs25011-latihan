import streamlit as st
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime

random.seed(42)

st.set_page_config(page_title="Simulasi Piket IT Del", layout="wide")

# ===============================
# SIDEBAR WAKTU
# ===============================
st.sidebar.header("⏰ Pengaturan Waktu")

jam_mulai = st.sidebar.time_input(
    "Pilih Jam Mulai Piket:",
    value=datetime.time(7, 0)
)

# ===============================
# SIDEBAR PARAMETER
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
# STYLE SIDEBAR
# ===============================
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #ffc0cb;
        }
    </style>
""", unsafe_allow_html=True)

# ===============================
# HEADER
# ===============================
st.title("📊 Simulasi Sistem Piket IT Del")
st.markdown("Simulasi proses pengisian ompreng untuk sistem piket.")

# ===============================
# CARD INFORMASI
# ===============================
st.markdown(f"""
<div style="
    background-color:#e6eaf2;
    padding:30px;
    border-radius:15px;
    margin-bottom:25px;
">

<h1>🚀 Mulai Simulasi</h1>

<h3>Parameter Saat Ini:</h3>
<ul>
<li><b>Jumlah Mahasiswa Piket:</b> {total_mahasiswa_yang_piket}</li>
<li><b>Jumlah Meja:</b> {total_meja}</li>
<li><b>Mahasiswa per Meja:</b> {mahasiswa_per_meja}</li>
<li><b>Waktu Lauk:</b> {min_lauk} - {max_lauk} detik</li>
<li><b>Waktu Nasi:</b> {min_nasi} - {max_nasi} detik</li>
<li><b>Waktu Angkat:</b> {min_angkat} - {max_angkat} detik</li>
<li><b>Jam Mulai:</b> {jam_mulai.strftime("%H:%M")}</li>
</ul>

</div>
""", unsafe_allow_html=True)

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
    batch_size = random.randint(4, 7)
    counter_batch = 0

    for i in range(TOTAL_OMPRENG):

        # LAUK
        waktu_lauk = random.uniform(min_lauk, max_lauk)
        total_lauk += waktu_lauk
        waktu_lauk_selesai += waktu_lauk / total_mahasiswa_yang_piket

        # ANGKAT (BATCH)
        counter_batch += 1
        if counter_batch >= batch_size:
            waktu_angkat = random.uniform(min_angkat, max_angkat)
            total_angkat += waktu_angkat
            waktu_angkat_selesai = max(
                waktu_lauk_selesai, waktu_angkat_selesai
            ) + (waktu_angkat / total_mahasiswa_yang_piket)

            counter_batch = 0
            batch_size = random.randint(4, 7)

        # NASI
        waktu_nasi = random.uniform(min_nasi, max_nasi)
        total_nasi += waktu_nasi
        waktu_nasi_selesai = max(
            waktu_angkat_selesai, waktu_nasi_selesai
        ) + (waktu_nasi / total_mahasiswa_yang_piket)

        data.append({
            "Ompreng": i + 1,
            "Waktu Selesai (detik)": waktu_nasi_selesai
        })

    # ===============================
    # PERHITUNGAN WAKTU
    # ===============================
    total_detik = round(waktu_nasi_selesai)
    total_menit = total_detik / 60

    waktu_mulai_datetime = datetime.datetime.combine(
        datetime.date.today(), jam_mulai
    )

    waktu_selesai_datetime = waktu_mulai_datetime + datetime.timedelta(
        seconds=total_detik
    )

    jam_selesai_str = waktu_selesai_datetime.strftime("%H:%M:%S")

    # ===============================
    # UTILISASI & RATA-RATA LAYANAN
    # ===============================
    total_waktu_proses = total_lauk + total_angkat + total_nasi
    kapasitas_maks = total_mahasiswa_yang_piket * total_detik
    utilisasi = (total_waktu_proses / kapasitas_maks) * 100 if kapasitas_maks > 0 else 0

    # Rata-rata layanan gabungan per ompreng (MENIT)
    rata_total_layanan_menit = (total_waktu_proses / TOTAL_OMPRENG) / 60

    st.success("Simulasi Selesai!")

    # ===============================
    # METRIC
    # ===============================
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Ompreng", TOTAL_OMPRENG)
    col2.metric("Total Waktu (menit)", f"{total_menit:.2f}")
    col3.metric("Selesai Pukul", jam_selesai_str)
    col4.metric("Utilisasi (%)", f"{utilisasi:.2f}%")
    col5.metric("Layanan per Ompreng (menit)", f"{rata_total_layanan_menit:.2f}")

        # ===============================
    # DATAFRAME
    # ===============================
    df = pd.DataFrame(data)

    # ===============================
    # LINE CHART
    # ===============================
    st.subheader("📈 Grafik Progres Penyelesaian Ompreng")
    fig_line = px.line(df, x="Ompreng", y="Waktu Selesai (detik)")
    st.plotly_chart(fig_line, use_container_width=True)

    # ===============================
    # DISTRIBUSI WAKTU PER MEJA
    # ===============================
    st.subheader("📊 Distribusi Waktu Total per Meja")

    data_meja = []
    for meja in range(total_meja):
        end_index = (meja + 1) * mahasiswa_per_meja - 1
        waktu_meja = df.iloc[end_index]["Waktu Selesai (detik)"]
        data_meja.append({
            "Meja": meja + 1,
            "Waktu Selesai (detik)": waktu_meja
        })

    df_meja = pd.DataFrame(data_meja)

    fig_bar_meja = px.bar(df_meja, x="Meja", y="Waktu Selesai (detik)")
    st.plotly_chart(fig_bar_meja, use_container_width=True)

    # ===============================
    # TIMELINE MEJA
    # ===============================
    st.subheader("📅 Timeline Penyelesaian Meja")
    df_meja["Waktu (menit)"] = df_meja["Waktu Selesai (detik)"] / 60
    fig_timeline = px.line(df_meja, x="Meja", y="Waktu (menit)", markers=True)
    st.plotly_chart(fig_timeline, use_container_width=True)

    # ===============================
    # PERBANDINGAN WAKTU TAHAPAN
    # ===============================
    st.subheader("📊 Perbandingan Total Waktu per Tahapan")

    df_proses = pd.DataFrame({
        "Proses": ["Lauk", "Angkat", "Nasi"],
        "Total Waktu (detik)": [total_lauk, total_angkat, total_nasi]
    })

    fig_proses = px.bar(
        df_proses,
        x="Proses",
        y="Total Waktu (detik)",
        color="Proses"
    )

    st.plotly_chart(fig_proses, use_container_width=True)

    # ===============================
    # GAUGE UTILISASI
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
    # DATA HASIL
    # ===============================
    st.subheader("📋 Data Hasil Simulasi")
    df["Waktu (menit)"] = df["Waktu Selesai (detik)"] / 60
    st.dataframe(df, use_container_width=True)

    # ===============================
    # BOTTLENECK
    # ===============================
    bottleneck = max(
        [("Lauk", total_lauk),
         ("Angkat", total_angkat),
         ("Nasi", total_nasi)],
        key=lambda x: x[1]
    )

    st.warning(f"⚠️ Bottleneck sistem berada pada proses: **{bottleneck[0]}**")