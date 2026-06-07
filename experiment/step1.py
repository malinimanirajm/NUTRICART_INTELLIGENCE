import os
import fitz  # PyMuPDF
import json

def run_complete_pipeline(input_folder, output_images_dir):
    os.makedirs(output_images_dir, exist_ok=True)
    
    if not os.path.exists(input_folder):
        print(f" Error: Input folder '{input_folder}' not found.")
        return

    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]
    print(f"Starting Master Pipeline. Found {len(pdf_files)} articles.\n")

    all_system_chunks = []

    for filename in pdf_files:
        pdf_path = os.path.join(input_folder, filename)
        doc = fitz.open(pdf_path)
        
        article_slug = os.path.splitext(filename)[0].replace(" ", "_")
        article_img_dir = os.path.join(output_images_dir, article_slug)
        
        print(f" Extracting structural elements from: {filename}")

        for page_num in range(len(doc)):
            page_idx = page_num + 1
            page = doc[page_num]
            
            # This tracking list will store elements found on this specific page along with their vertical position
            page_elements = []

            # 1. LOCATE TABLES & CAPTURE POSITION
            tables = page.find_tables()
            table_rects = [] # We save table positions so we don't duplicate table text as normal text
            
            for i, table in enumerate(tables):
                markdown_table = table.to_pandas().to_markdown()
                
                # table.rect gives us bounding box coordinates: (x0, y0, x1, y1)
                # y0 is the top edge of the table on the page
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

            # 2.LOCATE TEXT BLOCKS & CAPTURE POSITION
            # 'blocks' splits text into natural paragraphs and returns coordinates for each paragraph box
            text_blocks = page.get_text("blocks")
            
            for block in text_blocks:
                # block layout: (x0, y0, x1, y1, "text content", block_no, block_type)
                x0, y0, x1, y1, block_text, block_no, block_type = block
                
                if block_text.strip():
                    # Optimization: Skip this text block if it falls inside a table we already extracted
                    inside_table = False
                    for t_rect in table_rects:
                        if y0 >= t_rect[1] and y1 <= t_rect[3]:
                            inside_table = True
                            break
                    
                    if inside_table:
                        continue
                        
                    page_elements.append({
                        "y_position": y0, # The top vertical line of the paragraph box
                        "chunk_data": {
                            "source_file": filename,
                            "page_number": page_idx,
                            "chunk_type": "text",
                            "raw_content": block_text.strip(),
                            "summary_or_text": block_text.strip()
                        }
                    })

            # 3.LOCATE IMAGES & CAPTURE POSITION
            # Note: PyMuPDF extracts images via raw data streams. To find WHERE they sit visually, 
            # we look at the page's image locations map.
            image_info_list = page.get_image_info(xrefs=True)
            for img_info in image_info_list:
                # img_info layout provides bounding box: 'bbox': (x0, y0, x1, y1)
                y0 = img_info['bbox'][1]
                xref = img_info['xref']
                
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

            # ========================================================
            #  SORT BY THE VERTICAL 'Y' READING FLOW
            # ========================================================
            # This sorts everything on the page from top (y=0) to bottom
            page_elements.sort(key=lambda element: element["y_position"])

            # Append sorted elements into our main array and stamp the sequence number
            for sequence_idx, element in enumerate(page_elements):
                chunk = element["chunk_data"]
                chunk["sequence_number"] = sequence_idx + 1 # 1 means it is the first item on the page
                all_system_chunks.append(chunk)

    print(f"\n Pipeline Complete! Created a total of {len(all_system_chunks)} sequential chunks.")
    
    with open("final_chunks_preview.json", "w", encoding="utf-8") as f:
        json.dump(all_system_chunks, f, indent=2)
    print(" Saved sequential layout map to 'final_chunks_preview.json'!")

if __name__ == "__main__":
    run_complete_pipeline("data/PDF_Ingestion/article_input", "data/PDF_Ingestion/extracted_images")