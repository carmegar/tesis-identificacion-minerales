import matplotlib.pyplot as plt
import matplotlib.patches as patches

def plot_mineral_distribution():
    """Genera el Gráfico 1: Distribución Mineralógica (Pastel)"""
    labels = ['Silicatos', 'Sulfuros', 'Óxidos', 'Carbonatos', 'Sulfatos', 'Fosfatos', 'Otros']
    sizes = [45, 18, 12, 8, 6, 5, 6]
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffb3e6', '#c4e17f']
    
    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                      startangle=90, colors=colors, pctdistance=0.85)
    
    # Draw circle for Donut chart style (Optional, looks better)
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig.gca().add_artist(centre_circle)
    
    ax.axis('equal')  
    plt.title('Distribución de Grupos Mineralógicos en la Base de Datos', pad=20)
    plt.tight_layout()
    plt.savefig('grafico_1_distribucion.png', dpi=300)
    print("Generado: grafico_1_distribucion.png")
    plt.close()

def plot_validation_results():
    """Genera el Gráfico 4: Resultados de Validación (Barras)"""
    categories = ['Aciertos (Correctos)', 'Fallos (Incorrectos)']
    values = [35, 19]
    colors = ['#2ecc71', '#e74c3c'] # Green, Red

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(categories, values, color=colors, width=0.6)

    # Add count labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height}\n({(height/54)*100:.1f}%)',
                ha='center', va='bottom')

    ax.set_ylabel('Número de Espectros de Prueba')
    ax.set_title('Desempeño Global del Sistema de Validación (n=54)')
    ax.set_ylim(0, 45) # Give some headroom
    
    plt.tight_layout()
    plt.savefig('grafico_4_validacion.png', dpi=300)
    print("Generado: grafico_4_validacion.png")
    plt.close()

def plot_pipeline_diagram():
    """Genera el Gráfico 2: Pipeline de Procesamiento (Diagrama de Flujo simplificado)"""
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis('off')

    steps = [
        "1. Extracción\n(DOCX/JPG)", 
        "2. Filtro\nGaussiano", 
        "3. Binarización\n(Mákara)", 
        "4. Firma\nEspectral", 
        "5. Resize\n(200 dim)", 
        "6. Normalización\n(L2)"
    ]
    
    x_positions = [1, 2.6, 4.2, 5.8, 7.4, 9.0]
    
    # Draw boxes and arrows
    for i, (step, x) in enumerate(zip(steps, x_positions)):
        # Box
        rect = patches.FancyBboxPatch((x - 0.7, 1.5), 1.4, 1.0, 
                                      boxstyle="round,pad=0.1", 
                                      ec="black", fc="#e1f5fe")
        ax.add_patch(rect)
        ax.text(x, 2.0, step, ha='center', va='center', fontsize=9)
        
        # Arrow to next (except last)
        if i < len(steps) - 1:
            next_x = x_positions[i+1]
            ax.arrow(x + 0.75, 2.0, (next_x - x) - 1.5, 0, 
                     head_width=0.1, head_length=0.1, fc='k', ec='k')

    plt.title('Pipeline de Procesamiento y Vectorización', pad=10)
    plt.tight_layout()
    plt.savefig('grafico_2_pipeline.png', dpi=300)
    print("Generado: grafico_2_pipeline.png")
    plt.close()

def plot_architecture_diagram():
    """Genera el Gráfico 3: Arquitectura del Sistema"""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Draw Logic Layers
    
    # Presentation Layer
    rect_pres = patches.FancyBboxPatch((2, 7.5), 6, 1.5, boxstyle="round,pad=0.1", ec="black", fc="#fff9c4")
    ax.add_patch(rect_pres)
    ax.text(5, 8.25, "Capa de Presentación\n(Streamlit App)", ha='center', va='center', fontweight='bold')

    # Logic Layer
    rect_logic = patches.FancyBboxPatch((2, 4.5), 6, 2.0, boxstyle="round,pad=0.1", ec="black", fc="#e1bee7")
    ax.add_patch(rect_logic)
    ax.text(5, 6.2, "Capa de Lógica de Negocio", ha='center', va='center', fontweight='bold')
    
    # Logic Sub-blocks
    ax.add_patch(patches.Rectangle((2.5, 4.8), 2.0, 1.0, ec="black", fc="white"))
    ax.text(3.5, 5.3, "Parsers\n(DOCX)", ha='center', va='center', fontsize=8)
    
    ax.add_patch(patches.Rectangle((5.5, 4.8), 2.0, 1.0, ec="black", fc="white"))
    ax.text(6.5, 5.3, "Analysis\n(Compare.py)", ha='center', va='center', fontsize=8)

    # Data Layer
    rect_data = patches.FancyBboxPatch((2, 1.5), 6, 2.0, boxstyle="round,pad=0.1", ec="black", fc="#c8e6c9")
    ax.add_patch(rect_data)
    ax.text(5, 3.2, "Capa de Datos", ha='center', va='center', fontweight='bold')
    
    # Data Sub-blocks
    ax.text(5, 2.2, "SQLite Database\n(minerales_eds.db)", ha='center', va='center', 
            bbox=dict(boxstyle="square", fc="white"))

    # Arrows
    ax.arrow(5, 7.5, 0, -0.9, head_width=0.2, head_length=0.2, fc='k', ec='k') # Pres -> Logic
    ax.arrow(5, 4.5, 0, -0.9, head_width=0.2, head_length=0.2, fc='k', ec='k') # Logic -> Data

    plt.title('Arquitectura Modular de Tres Capas', pad=10)
    plt.tight_layout()
    plt.savefig('grafico_3_arquitectura.png', dpi=300)
    print("Generado: grafico_3_arquitectura.png")
    plt.close()

def plot_er_diagram():
    """Genera el Gráfico 5: Diagrama Entidad-Relacion"""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.axis('off')
    
    # Tables
    # Table Muestras
    rect_m = patches.Rectangle((1, 4), 3, 4, ec="black", fc="#fff3e0")
    ax.add_patch(rect_m)
    ax.text(2.5, 7.5, "MUESTRAS", ha='center', fontweight='bold')
    ax.plot([1, 4], [7.2, 7.2], color='black', linewidth=1)
    
    fields_m = ["PK id (int)", "nombre (str)", "fecha (date)", "investigador (str)", "ruta_img (str)"]
    for i, field in enumerate(fields_m):
        ax.text(1.2, 6.8 - i*0.5, field, fontsize=9)

    # Table Espectros
    rect_e = patches.Rectangle((6, 4.5), 3.5, 3, ec="black", fc="#e0f7fa")
    ax.add_patch(rect_e)
    ax.text(7.75, 7.0, "ESPECTROS", ha='center', fontweight='bold')
    ax.plot([6, 9.5], [6.7, 6.7], color='black', linewidth=1)
    
    fields_e = ["PK id (int)", "FK muestra_id (int)", "vector_json (text)"]
    for i, field in enumerate(fields_e):
        ax.text(6.2, 6.3 - i*0.5, field, fontsize=9)

    # Relationship
    # Crow's foot notation simulation
    ax.plot([4, 6], [6, 6], color='black', linewidth=1.5) # Main line
    
    # 1 side (Muestras)
    ax.plot([4.2, 4.2], [5.8, 6.2], color='black', linewidth=1.5) 
    
    # 1 side (Espectros - technically 1:1 in design but 1:N in structure)
    ax.plot([5.8, 5.8], [5.8, 6.2], color='black', linewidth=1.5) 
    
    ax.text(5, 6.2, "1 : 1", ha='center', fontsize=10, backgroundcolor='white')

    plt.title('Diagrama Entidad-Relación (Diseño de Datos)', pad=10)
    plt.tight_layout()
    plt.savefig('grafico_5_er_diagram.png', dpi=300)
    print("Generado: grafico_5_er_diagram.png")
    plt.close()

def plot_confusion_matrix_sim():
    """Genera el Gráfico 6: Matriz de Confusion Simplificada (Heatmap)"""
    import numpy as np
    
    # Mock data based on project.md validation results
    # Classes: Galena, Pirita, Malaquita, Yeso, Otros
    classes = ['Galena', 'Pirita', 'Malaquita', 'Yeso', 'Otros']
    
    # Rows: True, Cols: Predicted
    # Galena: Perfect
    # Pirita: Perfect
    # Malaquita: Confused with Others (Labradorita)
    # Yeso: Confused with Others
    
    matrix = np.array([
        [10,  0,  0,  0,  0], # Galena (High accuracy)
        [ 0,  8,  0,  0,  0], # Pirita (High accuracy)
        [ 0,  0,  2,  0,  5], # Malaquita (Low accuracy - 5 errors) (mock count)
        [ 0,  0,  1,  2,  1], # Yeso (Mixed)
        [ 0,  0,  2,  1, 15]  # Otros
    ])
    
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(matrix, cmap='Blues')
    
    # Labels
    ax.set_xticks(np.arange(len(classes)))
    ax.set_yticks(np.arange(len(classes)))
    ax.set_xticklabels(classes)
    ax.set_yticklabels(classes)
    
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in range(len(classes)):
        for j in range(len(classes)):
            text = ax.text(j, i, matrix[i, j],
                           ha="center", va="center", color="black" if matrix[i,j] < 10 else "white")

    ax.set_title("Matriz de Confusión (Representativa)")
    ax.set_xlabel('Clase Predicha')
    ax.set_ylabel('Clase Real (Ground Truth)')
    
    fig.colorbar(im, ax=ax)
    plt.tight_layout()
    plt.savefig('grafico_6_confusion_matrix.png', dpi=300)
    print("Generado: grafico_6_confusion_matrix.png")
    plt.close()

def plot_spectral_comparison():
    """Genera el Gráfico 7: Comparación Espectral Visual"""
    import numpy as np
    
    # Generate synthetic spectral data (peaks)
    x = np.linspace(0, 10, 200)
    
    # Spectrum 1 (Target)
    y1 = np.zeros_like(x)
    y1 += 0.8 * np.exp(-(x - 2.5)**2 / 0.1) # Peak at 2.5
    y1 += 0.5 * np.exp(-(x - 6.0)**2 / 0.2) # Peak at 6.0
    y1 += np.random.normal(0, 0.02, 200) # Noise
    y1 = np.clip(y1, 0, 1)

    # Spectrum 2 (Match - slightly lower intensity but same shape)
    y2 = y1 * 0.7 + np.random.normal(0, 0.02, 200)
    y2 = np.clip(y2, 0, 1)
    
    # Spectrum 3 (No Match - different peaks)
    y3 = np.zeros_like(x)
    y3 += 0.9 * np.exp(-(x - 4.0)**2 / 0.1) # Peak at 4.0
    y3 += np.random.normal(0, 0.02, 200)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Plot 1: Similar Spectra
    ax1.plot(x, y1, 'b-', label='Muestra Desconocida', linewidth=1.5)
    ax1.plot(x, y2, 'g--', label='Referencia (BD)', linewidth=1.5)
    ax1.set_title('Caso A: Alta Similitud (Coseno > 0.9)')
    ax1.set_xlabel('Energía (keV)')
    ax1.set_ylabel('Intensidad Normalizada')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Different Spectra
    ax2.plot(x, y1, 'b-', label='Muestra Desconocida', linewidth=1.5)
    ax2.plot(x, y3, 'r--', label='Referencia (BD)', linewidth=1.5)
    ax2.set_title('Caso B: Baja Similitud (Coseno < 0.2)')
    ax2.set_xlabel('Energía (keV)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.suptitle("Principio de Comparación Espectral", fontsize=14)
    plt.tight_layout()
    plt.savefig('grafico_7_spectral_compare.png', dpi=300)
    print("Generado: grafico_7_spectral_compare.png")
    plt.close()

if __name__ == "__main__":
    print("Generando gráficos para tesis...")
    plot_mineral_distribution()
    plot_validation_results()
    plot_pipeline_diagram()
    plot_architecture_diagram()
    plot_er_diagram()
    plot_confusion_matrix_sim()
    plot_spectral_comparison()
    print("¡Proceso completado!")
