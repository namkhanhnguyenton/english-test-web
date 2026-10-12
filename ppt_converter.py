import os
import re
import glob
import shutil
import logging
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

def convert_ppt_to_slides(ppt_file_path, output_dir):
    """
    Converts a PPT/PPTX presentation into a collection of slide images (slide_1.jpg, slide_2.jpg, ...).
    Returns (slide_files_list, total_slides) where slide_files_list is sorted relative image filenames.
    """
    abs_ppt = os.path.abspath(ppt_file_path)
    abs_out_dir = os.path.abspath(output_dir)
    os.makedirs(abs_out_dir, exist_ok=True)

    success = False
    error_msg = ""

    # Method 1: PowerPoint COM (High fidelity conversion)
    try:
        import win32com.client
        import pythoncom
        pythoncom.CoInitialize()

        ppt_app = win32com.client.Dispatch("PowerPoint.Application")
        # WithWindow=False keeps PowerPoint hidden
        presentation = ppt_app.Presentations.Open(abs_ppt, WithWindow=False)
        try:
            # Format 17 is ppSaveAsJPG (or 18 is ppSaveAsPNG)
            presentation.SaveAs(abs_out_dir, 17)
            total_slides_count = presentation.Slides.Count
            presentation.Close()
            success = True
        finally:
            try:
                ppt_app.Quit()
            except Exception:
                pass
            pythoncom.CoUninitialize()
            
    except Exception as e:
        error_msg = str(e)
        logger.warning(f"PowerPoint COM export failed, falling back to PIL/pptx generator. Error: {e}")

    # Standardize filenames to slide_1.jpg, slide_2.jpg ...
    if success:
        normalized_slides = _standardize_slide_files(abs_out_dir)
        if len(normalized_slides) > 0:
            return normalized_slides, len(normalized_slides)

    # Method 2: Fallback using python-pptx and Pillow
    logger.info("Using python-pptx & Pillow fallback to render slides...")
    return _render_slides_fallback(abs_ppt, abs_out_dir)


def _standardize_slide_files(directory):
    """
    Finds PowerPoint exported slide images (Slide1.jpg, Slide2.jpg or slide1.png, etc.)
    and renames them cleanly to slide_1.jpg, slide_2.jpg, ...
    """
    all_files = os.listdir(directory)
    # Match patterns like Slide1.jpg, Slide10.png, slide_1.jpg, etc.
    slide_pattern = re.compile(r'slide[_\s-]?(\d+)\.(jpe?g|png)', re.IGNORECASE)
    
    extracted = []
    for f in all_files:
        match = slide_pattern.match(f)
        if match:
            idx = int(match.group(1))
            extracted.append((idx, f))

    if not extracted:
        # Check any image files
        img_pattern = re.compile(r'.*\.(jpe?g|png)', re.IGNORECASE)
        img_files = sorted([f for f in all_files if img_pattern.match(f)])
        for idx, f in enumerate(img_files, start=1):
            extracted.append((idx, f))

    # Sort numerically by slide number
    extracted.sort(key=lambda x: x[0])

    renamed_slides = []
    # Rename sequentially
    temp_dir = os.path.join(directory, "_temp_rename")
    os.makedirs(temp_dir, exist_ok=True)

    # Move to temp first to avoid overwriting conflicts
    for new_idx, (old_idx, old_name) in enumerate(extracted, start=1):
        old_path = os.path.join(directory, old_name)
        temp_path = os.path.join(temp_dir, f"slide_{new_idx}.jpg")
        
        # Convert to standard JPG with Pillow if needed
        try:
            with Image.open(old_path) as img:
                rgb_img = img.convert('RGB')
                rgb_img.save(temp_path, 'JPEG', quality=90)
        except Exception:
            shutil.copy2(old_path, temp_path)
        
        try:
            os.remove(old_path)
        except Exception:
            pass

    # Move back
    for f in sorted(os.listdir(temp_dir)):
        src = os.path.join(temp_dir, f)
        dst = os.path.join(directory, f)
        shutil.move(src, dst)
        renamed_slides.append(f)

    try:
        os.rmdir(temp_dir)
    except Exception:
        pass

    # Return natural sorted list
    renamed_slides.sort(key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0)
    return renamed_slides


def _render_slides_fallback(ppt_file_path, output_dir):
    """
    Fallback parser using python-pptx to extract text & shapes,
    generating clear, attractive slide images using Pillow.
    """
    slides_list = []
    try:
        from pptx import Presentation
        prs = Presentation(ppt_file_path)
        
        for slide_idx, slide in enumerate(prs.slides, start=1):
            slide_text_lines = []
            title_text = f"Slide {slide_idx}"
            
            # Check shapes
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        txt = paragraph.text.strip()
                        if txt:
                            if not slide_text_lines and (shape == slide.shapes.title or "Slide" in title_text):
                                title_text = txt
                            else:
                                slide_text_lines.append(txt)

            # Generate slide canvas
            width, height = 1600, 900
            img = Image.new('RGB', (width, height), color=(248, 250, 252)) # Slate 50
            draw = ImageDraw.Draw(img)

            # Draw stylish header banner
            draw.rectangle([(0, 0), (width, 140)], fill=(30, 58, 138)) # Indigo 900
            
            # Header text
            try:
                header_font = ImageFont.truetype("arial.ttf", 46)
                badge_font = ImageFont.truetype("arial.ttf", 26)
                body_font = ImageFont.truetype("arial.ttf", 36)
            except Exception:
                header_font = ImageFont.load_default()
                badge_font = ImageFont.load_default()
                body_font = ImageFont.load_default()

            draw.text((60, 45), title_text[:70], fill=(255, 255, 255), font=header_font)
            
            # Slide badge
            draw.rounded_rectangle([(width - 220, 45), (width - 60, 95)], radius=10, fill=(59, 130, 246))
            draw.text((width - 200, 55), f"Slide {slide_idx}/{len(prs.slides)}", fill=(255, 255, 255), font=badge_font)

            # Draw card body
            card_rect = [(60, 180), (width - 60, height - 60)]
            draw.rounded_rectangle(card_rect, radius=20, fill=(255, 255, 255), outline=(226, 232, 240), width=3)

            # Draw lines of text
            y_offset = 240
            if not slide_text_lines:
                draw.text((120, y_offset), "Nội dung câu hỏi / Slide trình chiếu PowerPoint", fill=(100, 116, 139), font=body_font)
            else:
                for line in slide_text_lines[:14]: # Up to 14 lines
                    draw.text((120, y_offset), line[:95], fill=(30, 41, 59), font=body_font)
                    y_offset += 45

            # Save image
            filename = f"slide_{slide_idx}.jpg"
            save_path = os.path.join(output_dir, filename)
            img.save(save_path, 'JPEG', quality=95)
            slides_list.append(filename)

        return slides_list, len(slides_list)

    except Exception as e:
        logger.error(f"Fallback generation also failed: {e}")
        # Generate at least 1 emergency slide
        width, height = 1600, 900
        img = Image.new('RGB', (width, height), color=(241, 245, 249))
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except Exception:
            font = ImageFont.load_default()
        draw.text((100, 400), "Đề thi Tiếng Anh - Vui lòng xem câu hỏi và chọn đáp án", fill=(15, 23, 42), font=font)
        filename = "slide_1.jpg"
        save_path = os.path.join(output_dir, filename)
        img.save(save_path, 'JPEG', quality=90)
        return [filename], 1

