import os
from PIL import Image, ImageDraw

def create_pocus_icon(size, is_maskable=False):
    # Crear una imagen con fondo (o transparente si no es maskable)
    # Para maskable, necesitamos un fondo opaco que llene todo el marco (se usará azul oscuro)
    background_color = (30, 58, 138, 255) # #1e3a8a (Primary Medium)
    
    img = Image.new("RGBA", (size, size), background_color)
    draw = ImageDraw.Draw(img)
    
    # Calcular coordenadas relativas
    scale = size / 500.0
    
    # Dibujar la sonda (líneas y formas del logo)
    # Sonda: cuerpo
    probe_poly = [
        (190 * scale, 220 * scale),
        (250 * scale, 160 * scale),
        (310 * scale, 220 * scale),
        (250 * scale, 280 * scale)
    ]
    draw.polygon(probe_poly, outline=(255, 255, 255, 255), fill=(15, 23, 42, 255), width=int(12 * scale))
    
    # Sonda: cabeza/cristal (azul claro)
    draw.chord(
        [180 * scale, 150 * scale, 320 * scale, 230 * scale],
        start=180, end=360,
        fill=(59, 130, 246, 255), outline=(255, 255, 255, 255), width=int(12 * scale)
    )
    
    # Sonda: cable
    draw.line([250 * scale, 280 * scale, 200 * scale, 330 * scale], fill=(255, 255, 255, 255), width=int(14 * scale))
    draw.line([200 * scale, 330 * scale, 120 * scale, 420 * scale], fill=(255, 255, 255, 255), width=int(14 * scale))
    
    # Ondas / Nodos de Ultrasonido (Llama digital)
    nodes = [
        (250 * scale, 140 * scale),
        (280 * scale, 80 * scale),
        (350 * scale, 60 * scale),
        (410 * scale, 100 * scale),
        (430 * scale, 160 * scale),
        (410 * scale, 230 * scale),
        (340 * scale, 250 * scale),
        (280 * scale, 210 * scale),
        (350 * scale, 130 * scale),
        (350 * scale, 180 * scale)
    ]
    
    # Dibujar líneas de conexión
    connections = [
        (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 0),
        (1, 8), (8, 3), (2, 9), (9, 5), (0, 8), (8, 6)
    ]
    for c in connections:
        draw.line([nodes[c[0]], nodes[c[1]]], fill=(59, 130, 246, 200), width=int(4 * scale))
        
    # Dibujar los círculos de los nodos
    for i, node in enumerate(nodes):
        r = int(10 * scale)
        color = (59, 130, 246, 255) if i % 2 == 0 else (255, 255, 255, 255)
        draw.ellipse([node[0] - r, node[1] - r, node[0] + r, node[1] + r], fill=color)
        
    return img

def main():
    os.makedirs("assets/icons", exist_ok=True)
    
    # 1. Icono 192x192
    img_192 = create_pocus_icon(192)
    img_192.save("assets/icons/icon-192.png", "PNG")
    print("Icono 192x192 generado.")
    
    # 2. Icono 512x512
    img_512 = create_pocus_icon(512)
    img_512.save("assets/icons/icon-512.png", "PNG")
    print("Icono 512x512 generado.")
    
    # 3. Icono Maskable 512x512
    img_maskable = create_pocus_icon(512, is_maskable=True)
    img_maskable.save("assets/icons/icon-maskable-512.png", "PNG")
    print("Icono maskable 512x512 generado.")

if __name__ == "__main__":
    main()
