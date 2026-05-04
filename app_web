import streamlit as st
from rectpack import newPacker
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="Optimizador de Corte", layout="wide")

st.title("✂️ Optimizador de Corte (Placas y Perfiles)")

# --- BARRA LATERAL (ENTRADA DE DATOS) ---
with st.sidebar:
    st.header("Configuración")
    tipo = st.selectbox("Tipo de Trabajo", ["Placa (2D)", "Marco (45°)", "Tramos (1D)"])
    
    kerf = st.number_input("Desgaste de Disco/Sierra (cm)", value=0.3, step=0.1)
    
    # Agrupamos los inputs para evitar que se mezclen variables
    if tipo == "Placa (2D)":
        h_w = st.number_input("Ancho de la Hoja (cm)", value=122.0)
        h_h = st.number_input("Alto de la Hoja (cm)", value=244.0)
        p_w = st.number_input("Ancho de la Pieza (cm)", value=60.0)
        p_h = st.number_input("Alto de la Pieza (cm)", value=50.0)
        cant = st.number_input("Cantidad de piezas", value=10, step=1, min_value=1)
    
    elif tipo == "Marco (45°)":
        b_l = st.number_input("Largo de la Barra (cm)", value=610.0)
        m_l = st.number_input("Largo de la Caja (cm)", value=100.0)
        m_a = st.number_input("Ancho de la Caja (cm)", value=80.0)
        offset = st.number_input("Offset p/ 45° (cm)", value=5.0)
        cant_marcos = st.number_input("Número de Cajas", value=1, step=1, min_value=1)
        
    else: # Tramos 1D
        b_l = st.number_input("Largo de la Barra (cm)", value=610.0)
        t_l = st.number_input("Medida del tramo (cm)", value=5.0)
        cant_tramos = st.number_input("Cantidad de tramos", value=50, step=1, min_value=1)

# --- BOTÓN DE CÁLCULO ---
if st.button("🚀 Calcular Optimización"):
    
    # --- CASO 1: PLACA (2D) ---
    if tipo == "Placa (2D)":
        packer = newPacker(rotation=True)
        # Añadimos 100 hojas posibles (bins)
        packer.add_bin(h_w, h_h, count=100)
        
        # Añadimos las piezas sumando el desgaste
        for _ in range(int(cant)):
            packer.add_rect(p_w + kerf, p_h + kerf)
        
        packer.pack()
        
        # Agrupar rectángulos por cada hoja usada
        hojas_usadas = {}
        for r in packer.rect_list():
            b_id = r[0] # ID de la hoja
            if b_id not in hojas_usadas:
                hojas_usadas[b_id] = []
            hojas_usadas[b_id].append(r)
            
        if not hojas_usadas:
            st.error("No se pudo acomodar ninguna pieza. Revisa que la pieza no sea más grande que la hoja.")
        else:
            st.success(f"✅ Se necesitan {len(hojas_usadas)} hojas de {h_w}x{h_h} cm.")
            
            for b_id, rects in hojas_usadas.items():
                st.subheader(f"Hoja #{b_id + 1}")
                fig, ax = plt.subplots(figsize=(6, 8))
                ax.set_xlim(0, h_w)
                ax.set_ylim(0, h_h)
                ax.set_aspect('equal')
                
                # Dibujar fondo de la hoja
                ax.add_patch(patches.Rectangle((0, 0), h_w, h_h, color="#f0e4d0", alpha=0.5))
                
                for r in rects:
                    # r = [bin_id, x, y, width, height, rid]
                    ax.add_patch(patches.Rectangle((r[1], r[2]), r[3], r[4], 
                                                 edgecolor="black", facecolor="#3498db", alpha=0.8))
                    # Mostrar medida real (sin kerf)
                    if r[3] > 15: # Solo si cabe el texto
                        ax.text(r[1] + r[3]/2, r[2] + r[4]/2, f"{r[3]-kerf:.0f}x{r[4]-kerf:.0f}", 
                                ha='center', va='center', fontsize=8, color='white', fontweight='bold')
                
                st.pyplot(fig)

    # --- CASO 2: MARCOS Y TRAMOS (1D) ---
    else:
        piezas_1d = []
        if tipo == "Marco (45°)":
            l1, l2 = m_l + offset, m_a + offset
            for _ in range(int(cant_marcos)):
                piezas_1d.extend([l1, l1, l2, l2])
        else: # Tramos simples
            piezas_1d = [t_l] * int(cant_tramos)
        
        piezas_1d.sort(reverse=True)
        barras_resultado = []
        
        for p in piezas_1d:
            c_con_kerf = p + kerf
            acomodado = False
            for b in barras_resultado:
                if sum(b) + c_con_kerf <= b_l:
                    b.append(c_con_kerf)
                    acomodado = True
                    break
            if not acomodado:
                barras_resultado.append([c_con_kerf])
            
        st.success(f"✅ Se necesitan {len(barras_resultado)} barras de {b_l} cm.")
        
        for i, cortes in enumerate(barras_resultado):
            fig, ax = plt.subplots(figsize=(10, 1.5))
            ax.set_xlim(0, b_l)
            ax.set_ylim(0, 5)
            ax.add_patch(patches.Rectangle((0, 0), b_l, 5, color="gray", alpha=0.2))
            
            x_pos = 0
            for c in cortes:
                ax.add_patch(patches.Rectangle((x_pos, 0), c, 5, facecolor="#e67e22", edgecolor="white"))
                ax.text(x_pos + c/2, 2.5, f"{c-kerf:.1f}", ha='center', va='center', color='white', fontweight='bold')
                x_pos += c
            
            ax.axis('off')
            st.pyplot(fig)