import streamlit as st
from rectpack import newPacker
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Optimizador de Corte", layout="wide")

# Estilo visual para botones
st.markdown("""
    <style>
    .stButton>button {
        background-color: #1f538d;
        color: white;
        height: 3em;
        width: 100%;
        font-weight: bold;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("✂️ Optimizador de Corte: Placas, Marcos y Tramos")

# --- 2. BARRA LATERAL (ENTRADAS) ---
with st.sidebar:
    st.header("Configuración de Trabajo")
    tipo = st.selectbox("Tipo de Trabajo", ["Placa (2D)", "Marco (45°)", "Tramos (1D)"])
    
    kerf = st.number_input("Desgaste Disco (cm):", value=0.5, step=0.1)

    if tipo == "Placa (2D)":
        hw = st.number_input("Ancho Hoja (cm):", value=122.0)
        hh = st.number_input("Alto Hoja (cm):", value=244.0)
        pw = st.number_input("Ancho Pieza (cm):", value=0)
        ph = st.number_input("Alto Pieza (cm):", value=0)
        cant = st.number_input("Cantidad total piezas:", value=0, min_value=1, step=1)
    
    elif tipo == "Marco (45°)":
        bl = st.number_input("Largo de la Barra (cm):", value=0)
        ml = st.number_input("Largo de la Caja (cm):", value=0)
        ma = st.number_input("Ancho de la Caja (cm):", value=0)
        offset = st.number_input("Offset p/ 45° (cm):", value=5.0)
        cant_marcos = st.number_input("Número de Cajas:", value=1, min_value=1, step=1)
        
    else: # Tramos 1D
        bl = st.number_input("Largo de la Barra (cm):", value=0)
        tl = st.number_input("Medida del tramo (cm):", value=0)
        cant_tramos = st.number_input("Cantidad de tramos:", value=1, min_value=1, step=1)

# --- 3. BOTÓN Y LÓGICA ---
if st.button("🚀 Calcular Optimización"):
    
    # --- MODO PLACA (2D) ---
    if tipo == "Placa (2D)":
        try:
            ancho_h = float(hw)
            alto_h = float(hh)
            ancho_p = float(pw) + float(kerf)
            alto_p = float(ph) + float(kerf)
            cantidad_p = int(cant)

            packer = newPacker(rotation=True)
            packer.add_bin(ancho_h, alto_h, count=100)
            
            # SOLUCIÓN COMPATIBLE: Bucle manual para evitar error de 'count'
            for _ in range(cantidad_p):
                packer.add_rect(ancho_p, alto_p)
            
            packer.pack()
            
            hojas_usadas = {}
            for r in packer.rect_list():
                b_id = r[0]
                if b_id not in hojas_usadas: hojas_usadas[b_id] = []
                hojas_usadas[b_id].append(r)
            
            if not hojas_usadas:
                st.error("❌ Las piezas son más grandes que la hoja.")
            else:
                st.success(f"✅ RESUMEN 2D: Hojas usadas: {len(hojas_usadas)} | Piezas logradas: {len(packer.rect_list())}")
                
                for b_id, rects in hojas_usadas.items():
                    st.subheader(f"Hoja #{b_id + 1}")
                    fig, ax = plt.subplots(figsize=(6, 8), facecolor="#008507")
                    ax.set_facecolor('#008507')
                    ax.set_xlim(0, ancho_h); ax.set_ylim(0, alto_h); ax.set_aspect('equal')
                    
                    # Dibujamos la hoja base en gris (sobrante)
                    ax.add_patch(patches.Rectangle((0, 0), ancho_h, alto_h, color="#555555", alpha=1.0))
                    
                    for r in rects:
                        # Piezas en azul
                        ax.add_patch(patches.Rectangle((r[1], r[2]), r[3], r[4], edgecolor="white", facecolor="#3498db"))
                        if r[3] > 10:
                            ax.text(r[1]+r[3]/2, r[2]+r[4]/2, f"{r[3]-kerf:.0f}x{r[4]-kerf:.0f}", 
                                    ha='center', va='center', color='white', fontsize=8, fontweight='bold')
                    
                    ax.tick_params(colors='white')
                    st.pyplot(fig)
        except Exception as e:
            st.error(f"Error en el cálculo 2D: {e}")

    # --- MODO MARCO Y TRAMOS (1D) ---
    else:
        try:
            piezas_1d = []
            longitud_barra = float(bl)
            desgaste = float(kerf)

            if tipo == "Marco (45°)":
                l1 = float(ml) + float(offset)
                l2 = float(ma) + float(offset)
                for _ in range(int(cant_marcos)):
                    piezas_1d.extend([l1, l1, l2, l2])
            else: # Tramos simples
                piezas_1d = [float(tl)] * int(cant_tramos)
            
            piezas_1d.sort(reverse=True)
            barras_finales = []
            
            for p in piezas_1d:
                c_con_k = p + desgaste
                encajado = False
                for b in barras_finales:
                    if sum(b) + c_con_k <= longitud_barra:
                        b.append(c_con_k)
                        encajado = True
                        break
                if not encajado:
                    barras_finales.append([c_con_k])
                    
            st.success(f"✅ RESUMEN 1D: Perfiles usados: {len(barras_finales)} | Piezas totales: {len(piezas_1d)}")
            
            for i, cortes in enumerate(barras_finales):
                fig, ax = plt.subplots(figsize=(10, 1.5), facecolor="#008507")
                ax.set_facecolor("#008507")
                ax.set_xlim(0, longitud_barra); ax.set_ylim(0, 5)
                
                # Barra base gris (sobrante)
                ax.add_patch(patches.Rectangle((0, 0), longitud_barra, 5, color="#555555", alpha=1.0))
                
                x_progreso = 0
                for c in cortes:
                    ax.add_patch(patches.Rectangle((x_progreso, 0), c, 5, facecolor="#3498db", edgecolor="white"))
                    if c > 2:
                        ax.text(x_progreso + c/2, 2.5, f"{c-desgaste:.1f}", 
                                ha='center', va='center', color='white', fontsize=9, fontweight='bold')
                    x_progreso += c
                
                ax.set_title(f"Barra #{i+1}", color="white", loc="left", fontsize=10)
                ax.axis('off')
                st.pyplot(fig)
        except Exception as e:
            st.error(f"Error en el cálculo 1D: {e}")
