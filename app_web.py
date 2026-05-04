# --- MODO PLACA (2D) ---
    if tipo == "Placa (2D)":
        try:
            # Limpieza y forzado de tipos
            ancho_h = float(hw)
            alto_h = float(hh)
            ancho_p = float(pw) + float(kerf)
            alto_p = float(ph) + float(kerf)
            cantidad_p = int(cant)

            packer = newPacker(rotation=True)
            packer.add_bin(ancho_h, alto_h, count=100)
            
            # CAMBIO AQUÍ: En lugar de usar 'count' dentro de add_rect,
            # usamos un bucle for para añadir las piezas una por una.
            # Esto es compatible con todas las versiones de rectpack.
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
                    
                    ax.add_patch(patches.Rectangle((0, 0), ancho_h, alto_h, color="#555555", alpha=1.0))
                    
                    for r in rects:
                        ax.add_patch(patches.Rectangle((r[1], r[2]), r[3], r[4], edgecolor="white", facecolor="#3498db"))
                        if r[3] > 10:
                            ax.text(r[1]+r[3]/2, r[2]+r[4]/2, f"{r[3]-kerf:.0f}x{r[4]-kerf:.0f}", 
                                    ha='center', va='center', color='white', fontsize=8, fontweight='bold')
                    
                    ax.tick_params(colors='white')
                    st.pyplot(fig)
        except Exception as e:
            st.error(f"Error en el cálculo 2D: {e}")
