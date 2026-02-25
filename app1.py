import streamlit as st
import simpy
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Simulasi Piket IT Del", layout="wide")

st.title("🍱 Simulasi Sistem Piket IT Del (DES Lengkap + Visualisasi)")

class SistemPiketDES:
    def __init__(self):
        self.env = simpy.Environment()
        self.petugas = simpy.Resource(self.env, capacity=7)
        
        self.total_meja = 60
        self.mahasiswa_per_meja = 3
        self.total_ompreng = self.total_meja * self.mahasiswa_per_meja
        
        self.start_time = datetime(2024, 1, 1, 7, 0)
        self.data = []
        random.seed(42)

    def waktu_ke_jam(self, menit):
        return self.start_time + timedelta(minutes=menit)

    def proses_ompreng(self, id_ompreng):
        
        # LAUK
        with self.petugas.request() as req:
            yield req
            waktu_lauk = random.uniform(0.5, 1.0)  # 30-60 detik
            yield self.env.timeout(waktu_lauk)

        # ANGKAT (batch)
        batch_size = random.randint(4, 7)
        waktu_angkat = random.uniform(0.33, 1.0)
        yield self.env.timeout(waktu_angkat / batch_size)

        # NASI
        with self.petugas.request() as req2:
            yield req2
            waktu_nasi = random.uniform(0.5, 1.0)
            yield self.env.timeout(waktu_nasi)

        selesai = self.env.now
        
        self.data.append({
            "Ompreng": id_ompreng,
            "Waktu Selesai (menit)": selesai,
            "Jam Selesai": self.waktu_ke_jam(selesai)
        })

    def run(self):
        for i in range(self.total_ompreng):
            self.env.process(self.proses_ompreng(i+1))
        
        self.env.run()
        
        df = pd.DataFrame(self.data)
        total_waktu = df["Waktu Selesai (menit)"].max()
        jam_selesai = self.waktu_ke_jam(total_waktu)
        
        return df, total_waktu, jam_selesai


# ===============================
# BUTTON SIMULASI
# ===============================
if st.button("🚀 Jalankan Simulasi"):
    
    with st.spinner("Menjalankan simulasi..."):
        
        model = SistemPiketDES()
        df, total_waktu, jam_selesai = model.run()
        
        st.success("✅ Simulasi Selesai!")
        
        # ===============================
        # METRIC
        # ===============================
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Ompreng", 180)
        col2.metric("Total Waktu (menit)", f"{total_waktu:.2f}")
        col3.metric("Selesai Pukul", jam_selesai.strftime("%H:%M:%S"))

        # Tambah kolom meja
        df = df.sort_values("Ompreng")
        df["Meja"] = ((df["Ompreng"] - 1) // 3) + 1
        
        waktu_meja = df.groupby("Meja")["Waktu Selesai (menit)"].max()
        rata_meja = waktu_meja.mean()
        
        st.metric("Rata-rata Layanan per Meja (menit)", f"{rata_meja:.2f}")

        st.markdown("---")

        # ===============================
        # 1️⃣ GRAFIK PROGRES OMPRNG
        # ===============================
        st.subheader("📈 Progres Penyelesaian Ompreng")

        fig1 = px.line(
            df,
            x="Ompreng",
            y="Waktu Selesai (menit)",
            markers=True
        )
        st.plotly_chart(fig1, use_container_width=True)

        # ===============================
        # 2️⃣ DISTRIBUSI WAKTU PER MEJA
        # ===============================
        st.subheader("📊 Waktu Penyelesaian per Meja")

        df_meja = waktu_meja.reset_index()
        df_meja.columns = ["Meja", "Waktu Selesai (menit)"]

        fig2 = px.bar(
            df_meja,
            x="Meja",
            y="Waktu Selesai (menit)"
        )
        st.plotly_chart(fig2, use_container_width=True)

        # ===============================
        # 3️⃣ HISTOGRAM DISTRIBUSI WAKTU
        # ===============================
        st.subheader("📉 Distribusi Waktu Penyelesaian Ompreng")

        fig3 = px.histogram(
            df,
            x="Waktu Selesai (menit)",
            nbins=20
        )
        st.plotly_chart(fig3, use_container_width=True)

        # ===============================
        # 4️⃣ GAUGE TOTAL WAKTU
        # ===============================
        st.subheader("⏱ Gauge Total Waktu Penyelesaian")

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=total_waktu,
            title={'text': "Total Waktu (menit)"},
            gauge={
                'axis': {'range': [0, 30]},
                'steps': [
                    {'range': [0, 15], 'color': "lightgreen"},
                    {'range': [15, 22], 'color': "yellow"},
                    {'range': [22, 30], 'color': "red"},
                ],
            }
        ))

        st.plotly_chart(fig_gauge, use_container_width=True)

        # ===============================
        # TABEL DATA
        # ===============================
        st.subheader("📋 Detail Data")
        st.dataframe(df, use_container_width=True)