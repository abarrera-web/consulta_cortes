import streamlit as st
from rectpack import newPacker
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Configuración estética de la página
st.set_page_config(page_title="Optimizador de Corte", layout="wide")

# Estilo personalizado para emular los colores de tu App de escritorio
st.markdown("""
    <style>
    .stApp {
        background-color: #f0f2f6;
    }
    [data-testid="stSidebar"] {
        background-color: #1f538d;
    }
    .stMarkdown h1, h2, h3 {
        color: #1f538d;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("✂️ Optimizador de Corte: Placas, Marcos y Tramos")

# --- SIDEBAR (Entradas de usuario) ---
with st.sidebar:
    st.header("Configuración")
    tipo = st.selectbox("Tipo de Trabajo", ["Placa (2D)", "Marco (45°)", "Tramos (1D)"])
    
    kerf = st.number_input("Desgaste Disco (cm):", value=0.5, step=0.1)

    if tipo == "Placa (2D)":
        hw = st.number_input("Ancho Hoja (cm):", value=122.0)
        hh = st.number_input("Alto Hoja (cm):", value=244.0)
        pw = st.number_input("Ancho Pieza (cm):", value=0.0)
        ph = st.number_input("Alto Pieza (cm):", value=0.0)
        cant = st.number_input("Cantidad total piezas:", value=1, min_value=1)
    
    elif tipo == "Marco (45°)":
        bl = st.number_input("Largo de la Barra (cm):", value=610.0)
        ml = st.number_input("Largo de la Caja (cm):", value=0.0)
        ma = st.number_input("Ancho de la Caja (cm):", value=0.0)
        offset = st.number_input("Offset p/ 45° (cm):", value=5.0)
        cant = st.number_input("Número de Cajas:", value=1, min_value=1)
        
    else: # Tramos 1D
        bl = st.number_input("Largo de la Barra (cm):", value=610.0)
        tl = st.number_input("Medida del tramo (cm):", value=0.0)
        cant = st.number_input("Cantidad de tramos:", value=1, min_value=1)

# --- LÓGICA DE OPTIMIZACIÓN ---
if st.button("🚀 Calcular Optimización"):
    
    if tipo == "Placa (2D)":
        # Validación mínima
        if pw <= 0 or ph <= 0:
            st.error("Ingresa medidas de pieza válidas.")
        else:
            packer = newPacker(rotation=True)
            packer.add_bin(hw, hh, count=100)
            packer.add_rect(float(pw + kerf), float(ph + kerf), count=int(cant))
            packer.pack()
            
            hojas = {}
            for r in packer.rect_list():
                b = r[0]
                if b not in hojas: hojas[b] = []
                hojas[b].append(r)
            
            st.info(f"**RESUMEN 2D:** Hojas usadas: {len(hojas)} | Piezas logradas: {len(packer.rect_list())}")
            
            for b_id, rects in hojas.items():
                fig, ax = plt.subplots(figsize=(6, 8), facecolor="#008507")
                ax.set_facecolor('#008507')
                ax.set_xlim(0, hw); ax.set_ylim(0, hh); ax.set_aspect('equal')
                
                # Hoja base (gris)
                ax.add_patch(patches.Rectangle((0, 0), hw, hh, color="#555555", alpha=1.0))
                
                for r in rects:
                    ax.add_patch(patches.Rectangle((r[1], r[2]), r[3], r[4], edgecolor="white", facecolor="#3498db"))
                    if r[3] > 10:
                        ax.text(r[1]+r[3]/2, r[2]+r[4]/2, f"{r[3]-kerf:.0f}x{r[4]-kerf:.0f}", 
                                ha='center', va='center', color='white', fontsize=8, fontweight='bold')
                
                ax.set_title(f"Hoja #{b_id+1}", color="white")
                st.pyplot(fig)

    else:
        # Lógica 1D
        piezas_1d = []
        if tipo == "Marco (45°)":
            l1, l2 = ml + offset, ma + offset
            for _ in range(int(cant)): piezas_1d.extend([l1, l1, l2, l2])
        else:
            piezas_1d = [tl] * int(cant)
        
        piezas_1d.sort(reverse=True)
        barras = []
        for p in piezas_1d:
            c = p + kerf
            fit = False
            for b in barras:
                if sum(b) + c <= bl:
                    b.append(c); fit = True; break
            if not fit: barras.append([c])
            
        st.info(f"**RESUMEN 1D:** Perfiles usados: {len(barras)} | Piezas totales: {len(piezas_1d)}")
        
        for i, cortes in enumerate(barras):
            fig, ax = plt.subplots(figsize=(10, 1.5), facecolor="#008507")
            ax.set_facecolor("#008507")
            ax.set_xlim(0, bl); ax.set_ylim(0, 5)
            
            # Barra base (gris)
            ax.add_patch(patches.Rectangle((0, 0), bl, 5, color="#555555", alpha=1.0))
            
            x = 0
            for c in cortes:
                ax.add_patch(patches.Rectangle((x, 0), c, 5, facecolor="#3498db", edgecolor="white"))
                if c > 2:
                    ax.text(x + c/2, 2.5, f"{c-kerf:.1f}", ha='center', va='center', color='white', fontsize=9, fontweight='bold')
                x += c
            
            ax.axis('off')
            st.pyplot(fig)
