import os
import fitz  # PyMuPDF
import json

def run_complete_pipeline(input_folder, output_images_dir):
    os.makedirs(output_images_dir, exist_ok=True)
    
    if not os.path.exists(input_folder):
        print(f" Error: Input folder '{input_folder}' not found.")
        return

    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]
    print(f" Starting Master Pipeline. Found {len(pdf_files)} articles.\n")

    all_system_chunks = []
    corrupted_files = []

    for filename in pdf_files:
        pdf_path = os.path.join(input_folder, filename)
        
        # ========================================================
        # CORRECTION: SAFE OPENING & AUTO-REPAIR LAYER
        # ========================================================
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            if "bad xref" in str(e).lower() or "xref" in str(e).lower():
                print(f"Warning: '{filename}' has a broken XREF map index. Attempting memory auto-repair...")
                try:
                    # Force byte-stream repair reconstruction in RAM
                    doc = fitz.open(pdf_path, filetype="pdf")
                    doc.init_doc()  # Validates internal tree pointers
                    print(f"Reconstructive fix applied successfully for '{filename}'!")
                except Exception as repair_error:
                    print(f"Critical Error: '{filename}' is unrepairable. Skipping file. Details: {repair_error}")
                    corrupted_files.append((filename, str(repair_error)))
                    continue
            else:
                print(f"Unknown failure opening '{filename}'. Skipping. Details: {e}")
                corrupted_files.append((filename, str(e)))
                continue
        
        article_slug = os.path.splitext(filename)[0].replace(" ", "_")
        article_img_dir = os.path.join(output_images_dir, article_slug)
        
        print(f"Extracting structural elements from: {filename}")

        for page_num in range(len(doc)):
            page_idx = page_num + 1
            page = doc[page_num]
            
            page_elements = []
            table_rects = [] 

            # 1.LOCATE TABLES & CAPTURE POSITION
            try:
                tables = page.find_tables()
                for i, table in enumerate(tables):
                    markdown_table = table.to_pandas().to_markdown()
                    top_edge_y = table.rect[1] 
                    table_rects.append(table.rect)
                    
                    page_elements.append({
                        "y_position": top_edge_y,
                        "chunk_data": {
                            "source_file": filename,
                            "page_number": page_idx,
                            "chunk_type": "table",
                            "raw_content": markdown_table,
                            "summary_or_text": f"TABLE_MARKER: Structured data layout matrix on page {page_idx}."
                        }
                    })
            except Exception as table_err:
                print(f"Skipping table parsing on page {page_idx} due to structural layout noise.")
                table_rects = []

            # 2. LOCATE TEXT BLOCKS & CAPTURE POSITION
            try:
                text_blocks = page.get_text("blocks")
                for block in text_blocks:
                    x0, y0, x1, y1, block_text, block_no, block_type = block
                    
                    if block_text.strip():
                        inside_table = False
                        for t_rect in table_rects:
                            if y0 >= t_rect[1] and y1 <= t_rect[3]:
                                inside_table = True
                                break
                        
                        if inside_table:
                            continue
                            
                        page_elements.append({
                            "y_position": y0, 
                            "chunk_data": {
                                "source_file": filename,
                                "page_number": page_idx,
                                "chunk_type": "text",
                                "raw_content": block_text.strip(),
                                "summary_or_text": block_text.strip()
                            }
                        })
            except Exception as text_err:
                print(f" Skipping text parsing on page {page_idx} due to block extraction encoding issues.")

            # 3.LOCATE IMAGES & CAPTURE POSITION
            try:
                image_info_list = page.get_image_info(xrefs=True)
                for img_info in image_info_list:
                    y0 = img_info['bbox'][1]
                    xref = img_info['xref']
                    
                    # Skip images without a valid cross-reference ID
                    if xref == 0:
                        continue
                        
                    os.makedirs(article_img_dir, exist_ok=True)
                    base_image = doc.extract_image(xref)
                    
                    img_name = f"page_{page_idx}_img_{xref}.{base_image['ext']}"
                    img_save_path = os.path.join(article_img_dir, img_name)
                    
                    with open(img_save_path, "wb") as f:
                        f.write(base_image["image"])

                    page_elements.append({
                        "y_position": y0,
                        "chunk_data": {
                            "source_file": filename,
                            "page_number": page_idx,
                            "chunk_type": "image",
                            "raw_content": img_save_path,
                            "summary_or_text": f"IMAGE_MARKER: Visual graphic file located at {img_save_path}."
                        }
                    })
            except Exception as img_err:
                print(f"Skipping image extraction on page {page_idx} due to image object metadata corruption.")

            # ========================================================
            # SORT BY THE VERTICAL 'Y' READING FLOW
            # ========================================================
            page_elements.sort(key=lambda element: element["y_position"])

            # Append sorted elements into our main array and stamp the sequence number
            for sequence_idx, element in enumerate(page_elements):
                chunk = element["chunk_data"]
                chunk["sequence_number"] = sequence_idx + 1 
                all_system_chunks.append(chunk)

        doc.close()

    print(f"\nPipeline Complete! Created a total of {len(all_system_chunks)} sequential chunks.")
    if corrupted_files:
        print(f"Skipped {len(corrupted_files)} unrepairable file(s):")
        for bad_f, err in corrupted_files:
            print(f"   - {bad_f} -> {err}")
    
    with open("final_chunks_preview.json", "w", encoding="utf-8") as f:
        json.dump(all_system_chunks, f, indent=2)
    print("Saved sequential layout map to 'final_chunks_preview.json'!")

if __name__ == "__main__":
    run_complete_pipeline("data/PDF_Ingestion/article_input", "data/PDF_Ingestion/extracted_images")