import os
from PIL import Image, ImageOps

def get_robust_background_color(source_img):
    """
    Calcula un color de fondo robusto a partir de las esquinas de la imagen.
    Si las esquinas son transparentes, utiliza el color institucional por defecto (#1e3a8a).
    """
    w, h = source_img.size
    # Obtener los píxeles de las 4 esquinas
    corners = [
        source_img.getpixel((0, 0)),
        source_img.getpixel((w - 1, 0)),
        source_img.getpixel((0, h - 1)),
        source_img.getpixel((w - 1, h - 1))
    ]
    
    valid_rgbs = []
    for pixel in corners:
        # Si tiene canal alfa y es opaco o semiopaco (alfa > 50)
        if len(pixel) == 4:
            r, g, b, a = pixel
            if a > 50:
                valid_rgbs.append((r, g, b))
        else:
            valid_rgbs.append(pixel[:3])
            
    if valid_rgbs:
        r_avg = int(sum(c[0] for c in valid_rgbs) / len(valid_rgbs))
        g_avg = int(sum(c[1] for c in valid_rgbs) / len(valid_rgbs))
        b_avg = int(sum(c[2] for c in valid_rgbs) / len(valid_rgbs))
        return (r_avg, g_avg, b_avg, 255)
    else:
        # Color por defecto (#1e3a8a)
        return (30, 58, 138, 255)

def create_contained_image(source, canvas_size, max_content_size, background):
    """
    Escala la imagen origen proporcionalmente usando ImageOps.contain para que quepa
    dentro de max_content_size y la centra en un lienzo de tamaño canvas_size
    relleno con el color background.
    """
    # Escalar proporcionalmente para que se ajuste dentro de max_content_size
    resized_img = ImageOps.contain(source, max_content_size)
    
    # Crear el lienzo del tamaño final
    canvas = Image.new("RGBA", canvas_size, background)
    
    # Calcular la posición para centrar la imagen redimensionada
    offset_x = (canvas_size[0] - resized_img.size[0]) // 2
    offset_y = (canvas_size[1] - resized_img.size[1]) // 2
    
    # Pegar usando la misma imagen como máscara para su canal alfa
    canvas.paste(resized_img, (offset_x, offset_y), resized_img)
    return canvas

def main():
    source_path = "assets/images/pocus_fusion_branding.png"
    icons_dir = "assets/icons"
    images_dir = "assets/images"
    
    os.makedirs(icons_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    
    print(f"Cargando y convirtiendo imagen fuente a RGBA: {source_path}")
    source_img = Image.open(source_path).convert("RGBA")
    
    # Obtener un color de fondo coherente
    bg_color = get_robust_background_color(source_img)
    print(f"Color de fondo determinado: {bg_color}")
    
    # 1. apple-touch-icon-180.png (180x180)
    print("Generando apple-touch-icon-180.png...")
    img_180 = create_contained_image(source_img, (180, 180), (180, 180), bg_color)
    img_180.save(os.path.join(icons_dir, "apple-touch-icon-180.png"), "PNG")
    
    # 2. icon-192.png (192x192)
    print("Generando icon-192.png...")
    img_192 = create_contained_image(source_img, (192, 192), (192, 192), bg_color)
    img_192.save(os.path.join(icons_dir, "icon-192.png"), "PNG")
    
    # 3. icon-512.png (512x512)
    print("Generando icon-512.png...")
    img_512 = create_contained_image(source_img, (512, 512), (512, 512), bg_color)
    img_512.save(os.path.join(icons_dir, "icon-512.png"), "PNG")
    
    # 4. icon-maskable-512.png (512x512, contenido de 384x384 máx)
    print("Generando icon-maskable-512.png...")
    img_maskable = create_contained_image(source_img, (512, 512), (384, 384), bg_color)
    img_maskable.save(os.path.join(icons_dir, "icon-maskable-512.png"), "PNG")
    
    # 5. social-preview-1200x630.png (1200x630, contenido de 1200x630 máx)
    print("Generando social-preview-1200x630.png...")
    img_preview = create_contained_image(source_img, (1200, 630), (1200, 630), bg_color)
    img_preview.save(os.path.join(images_dir, "social-preview-1200x630.png"), "PNG")
    
    print("Procesamiento completado con éxito.")

if __name__ == "__main__":
    main()
