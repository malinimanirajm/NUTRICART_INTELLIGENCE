import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Dynamically calculates total pages to render professional 'Page X of Y' footers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (Skipped on Cover Page)
        if self._pageNumber > 1:
            self.drawString(54, 750, "NutriCart Intelligence — System Architecture & Low-Level Design")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
        # Footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 40, footer_text)
        self.drawString(54, 40, "CONFIDENTIAL — INTERNAL DEVELOPMENT USE ONLY")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 52, 558, 52)
        
        self.restoreState()

def build_pdf(filename="NutriCart_Intelligence_LLD.pdf"):
    # Target Document Bounds: 0.75-inch margins (54 points)
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette Definitions
    PRIMARY = colors.HexColor("#1E3A8A")    # Deep Navy
    SECONDARY = colors.HexColor("#0D9488")  # Teal
    NEUTRAL_DARK = colors.HexColor("#1E293B") # Charcoal
    NEUTRAL_LIGHT = colors.HexColor("#F8FAFC") # Off-white background
    ACCENT = colors.HexColor("#EF4444")     # Muted Red for Guardrails
    
    # Typography Modifiers
    styles.add(ParagraphStyle('DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=26, leading=32, textColor=PRIMARY, spaceAfter=8))
    styles.add(ParagraphStyle('DocSub', parent=styles['Normal'], fontName='Helvetica', fontSize=14, leading=18, textColor=SECONDARY, spaceAfter=30))
    styles.add(ParagraphStyle('H1', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=PRIMARY, spaceBefore=18, spaceAfter=12, keepWithNext=True))
    styles.add(ParagraphStyle('H2', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=SECONDARY, spaceBefore=12, spaceAfter=6, keepWithNext=True))
    styles.add(ParagraphStyle('BodyCustom', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, textColor=NEUTRAL_DARK, spaceAfter=8))
    styles.add(ParagraphStyle('CodeBlock', parent=styles['Normal'], fontName='Courier', fontSize=7.5, leading=10, textColor=NEUTRAL_DARK))
    styles.add(ParagraphStyle('TableHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=colors.white, alignment=1))
    styles.add(ParagraphStyle('TableCell', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12, textColor=NEUTRAL_DARK))
    styles.add(ParagraphStyle('TableGuard', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=ACCENT))

    story = []
    
    # -------------------------------------------------------------------------
    # COVER PAGE / HEADER BLOCK
    # -------------------------------------------------------------------------
    story.append(Spacer(1, 40))
    story.append(Paragraph("NutriCart Intelligence", styles['DocTitle']))
    story.append(Paragraph("Low-Level Design & System Component Specification Blueprint", styles['DocSub']))
    story.append(Paragraph("<b>Author:</b> Core Engineering Team<br/><b>Target Environment:</b> Python 3.11 / LangGraph Engine / Weaviate Hybrid Store / SQLite Core<br/><b>Document Version:</b> 1.0.0 (Production Stable)", styles['BodyCustom']))
    story.append(Spacer(1, 20))
    
    # Quick Executive Summary Layout Box
    summary_data = [[
        Paragraph("<b>Executive Specification Overview:</b> This low-level system mapping formalizes the structural processing boundaries, event state transitions, and analytical class entities constituting NutriCart Intelligence. It explicitly details the execution locations of runtime guardrails (Input Verification, System Prompt Isolation, LLM Parametrization, Output Quarantine) designed to safely parse nutritional parameters, run mathematical log summarizations, and securely deliver outbound reports via SMS/WhatsApp gateways.", styles['TableCell'])
    ]]
    summary_table = Table(summary_data, colWidths=[504])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#BFDBFE")),
        ('PADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 15))
    
    # -------------------------------------------------------------------------
    # 1. SEQUENTIAL CODE-TO-DATABASE COMPONENT MAPPING
    # -------------------------------------------------------------------------
    story.append(Paragraph("1. Sequential Code-to-Database Component Mapping", styles['H1']))
    story.append(Paragraph("The system relies on an asynchronous ingestion and batch processing layer to map unstructured nutrition articles and synthetic transactional inputs into query-optimized datastores.", styles['BodyCustom']))
    
    ascii_map_1 = """
  [ Health PDFs / Manuals ]           [ Seed Configurations ]
              │                                  │
              ▼ (PyMuPDF / JSON Maps)            ▼ (Random Seed / CSV Streams)
      ┌───────────────┐                  ┌───────────────┐
      │  document.py  │                  │generate_groce─│
      │  Extraction   │                  │ry_dataset.py  │
      └───────┬───────┘                  └───────┬───────┘
              │                                  │
              ▼ (Layout Ordered Extractions)     ▼ (Relational Transactional Exports)
┌───────────────────────────┐      ┌──────────────────────────────────────────┐
│ Local Directory Storage   │      │ SQLite Relational Database Engine        │
│ ├── extracted_images/     │      │ ├── customers  ├── products              │
│ └── final_chunks_preview  │      │ └── nutrition  └── transactions / items  │
└─────────────┬─────────────┘      └─────────────────────┬────────────────────┘
              │                                          │
              ▼ (Hybrid Sync)                            ▼ (Query Lookup Hook)
      ┌───────────────┐                                  │
      │ Weaviate Vector │                                 │
      │ Schema Index  │                                  │
      └───────┬───────┘                                  │
              │                                          │
              └───────────────┐ ┌────────────────────────┘
                              │ │
                              ▼ ▼
                  ┌───────────────────────┐
                  │     new_graph.py      │
                  │  Multi-Agent Runtime  │
                  └───────────────────────┘
    """
    
    map1_table = Table([[Paragraph(f"<pre>{ascii_map_1.replace(' ', '&nbsp;').replace('│', '|').replace('─', '-').replace('┌', '+').replace('┐', '+').replace('└', '+').replace('┘', '+').replace('┬', '+').replace('▼', 'v').replace('▲', '^')}</pre>", styles['CodeBlock'])]], colWidths=[504])
    map1_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NEUTRAL_LIGHT),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(map1_table)
    story.append(Spacer(1, 10))
    
    # -------------------------------------------------------------------------
    # 2. STATE SPACE LIFECYCLE & AGENT GRAPH PROCESSING NODE FLOW
    # -------------------------------------------------------------------------
    story.append(Paragraph("2. State Space Lifecycle & Agent Graph Processing Node Flow", styles['H1']))
    story.append(Paragraph("Below is the execution flow map showing the tracking paths of the multi-agent orchestration layer. This graph details exactly where defensive guardrail middleware intercepts payloads during execution.", styles['BodyCustom']))
    
    ascii_map_2 = """
                  [ Raw User Request String ]
                              │
                              ▼
           =======================================
           GUARDRAIL 1: INPUT GATEWAY INTERCEPTOR
           =======================================
           ├── [Check] Regex Prompt Injection Scan
           └── [Check] Sensitive PII Stripping / Masking
                              │
                              ▼ (Sanitized Query Text)
                 ┌─────────────────────────┐
                 │    Supervisor Agent     │◀────────────────────────┐
                 └────────────┬────────────┘                         │
                              │                                      │
                 (Routes Dynamic State Target)                       │
                              │                                      │
      ┌───────────────────────┼───────────────────────┐              │
      ▼                       ▼                       ▼              │
┌───────────┐           ┌───────────┐           ┌───────────┐        │
│  Intake   │           │ Inventory │           │ Math Agg  │        │
│   Node    │           │   Node    │           │   Node    │        │
└─────┬─────┘           └─────┬─────┘           └─────┬─────┘        │
      │                       │                       │              │
 [Database Check]        [Vector Search]         [Computation]       │
 ├── SQLite Fetch:       ├── Hybrid Match:       └── Deterministic   │
 │   User Prefs /        │   Sugar < 5g              Summation Loop: │
 │   Dislikes            │   Protein > 10g           Protein, Sugar, │
 └── Mode Evaluation     └── Exclude Blacklist       and Calories    │
      │                       │                       │              │
      ▼                       ▼                       ▼              │
(Append AI State)       (Append Results)        (Append Report)      │
      │                       │                       │              │
      └───────────────────────┼───────────────────────┘              │
                              │                                      │
                    (Returns Updated State)                          │
                              │                                      │
                              └──────────────────────────────────────┘
                              │
                    (If next == "FINISH")
                              │
                              ▼
           =======================================
            GUARDRAIL 2 & 3: SYSTEM PROMPT / MODEL
           =======================================
           ├── [System] Enforce Strict JSON Formatting Contexts
           └── [LLM] Set Temperature = 0.0 for Consistent Behavior
                              │
                              ▼ (Drafted Message String)
           =======================================
           GUARDRAIL 4: OUTPUT INTEGRITY VERIFIER
           =======================================
           ├── [Check] Missing Bracket Template Leakage Check
           ├── [Check] Total Character Length Cap Limit Check (< 4000)
           └── [Check] Data Coherency / Hallucination Verification Scan
                              │
                    ┌*********┴*********┐
                    │ Is Payload Valid? │
                    └****┬*********┬****┘
                         │         │
                   (Yes) │         │ (No)
                         ▼         ▼
          ┌───────────────────┐   ┌───────────────────┐
          │ WhatsApp Dispatch │   │  Fallback Safe    │
          │ (Twilio Gateway)  │   │  Text Redirection │
          └───────────────────┘   └───────────────────┘
    """
    
    map2_table = Table([[Paragraph(f"<pre>{ascii_map_2.replace(' ', '&nbsp;').replace('│', '|').replace('─', '-').replace('┌', '+').replace('┐', '+').replace('└', '+').replace('┘', '+').replace('┬', '+').replace('▼', 'v').replace('▲', '^').replace('┼', '+')}</pre>", styles['CodeBlock'])]], colWidths=[504])
    map2_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NEUTRAL_LIGHT),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    
    # Force the complex diagram and its header to sit together cleanly on page 2
    story.append(KeepTogether([map2_table]))
    story.append(Spacer(1, 10))
    
    # Guardrail Placement Clarification Grid
    story.append(Paragraph("System Guardrail Placement & Execution Specifications", styles['H2']))
    guard_data = [
        [Paragraph("Guardrail ID & Layer", styles['TableHeader']), Paragraph("Code Hook Location", styles['TableHeader']), Paragraph("Functional Verification Objective", styles['TableHeader'])],
        [Paragraph("<b>GD-01: Input Gateway</b>", styles['TableCell']), Paragraph("<code>intake_agent</code> entry", styles['TableCell']), Paragraph("Strips malicious injections and isolates tracking variables like customer IDs.", styles['TableCell'])],
        [Paragraph("<b>GD-02: System Prompt</b>", styles['TableCell']), Paragraph("<code>supervisor_agent</code> initialization", styles['TableCell']), Paragraph("Binds agent reasoning paths to safe domains and enforces JSON format configurations.", styles['TableCell'])],
        [Paragraph("<b>GD-03: Model Runtime</b>", styles['TableCell']), Paragraph("<code>ChatOllama</code> wrapper instantiation", styles['TableCell']), Paragraph("Pins temperature variables to absolute zero (0.0) to eliminate non-deterministic hallucinations.", styles['TableCell'])],
        [Paragraph("<b>GD-04: Output Integrity</b>", styles['TableCell']), Paragraph("<code>whatsapp_node</code> outbound delivery", styles['TableGuard']), Paragraph("Quarantines drafts checking for template bracket leakage or truncated text blocks before network dispatch.", styles['TableCell'])],
    ]
    guard_table = Table(guard_data, colWidths=[120, 144, 240])
    guard_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, NEUTRAL_LIGHT]),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(KeepTogether([guard_table]))
    story.append(Spacer(1, 15))

    # -------------------------------------------------------------------------
    # 3. COMPREHENSIVE DATA-OBJECT CLASS RELATIONSHIPS
    # -------------------------------------------------------------------------
    story.append(Paragraph("3. Comprehensive Data-Object Class Relationships", styles['H1']))
    story.append(Paragraph("The system state acts as a single centralized thread across active worker components, pulling structural properties from relational models and vector entity maps.", styles['BodyCustom']))
    
    ascii_map_3 = """
+─────────────────────────────────────────────────────────────────────────────+
|                             MultiAgentState (dict)                          |
+─────────────────────────────────────────────────────────────────────────────+
|  - messages : Sequence[BaseMessage] (Chronological conversational trace)     |
|  - next     : str ("Intake" | "Inventory" | "Aggregate" | "FINISH")          |
|  - filters  : dict {"max_sugar": 5.0, "min_protein": 10.0, "dislikes": []}  |
|  - results  : List[dict] (Extracted row vectors from databases)            |
|  - answer   : str (Compiled report text for output delivery)                |
|  - customer_id : str (Padded, unique client mapping tag)                    |
+───────────────────────────────────────────────────┬─────────────────────────+
                                                    │
                                      (Hydrates Content Matrices)
                                                    │
                                                    ▼
+─────────────────────────────────────────────────────────────────────────────+
|                         Target Storage Target Entities                      |
+─────────────────────────────────────────────────────────────────────────────+
|  ┌───────────────────────────────┐     ┌─────────────────────────────────┐  |
|  │      Weaviate Product Class   │     │    Relational DB Operations     │  |
|  ├───────────────────────────────┤     ├─────────────────────────────────┤  |
|  │ - product_name    : text      │     │ [Table: transactions]           │  |
|  │ - category_name   : text      │     │  - transaction_id   : PK_Str    │  |
|  │ - added_sugar     : number    │     │  - customer_id      : FK_Str    │  |
|  │ - protein         : number    │     │  - transaction_date : Date      │  |
|  │ - calories        : number    │     │ [Table: transaction_items]      │  |
|  └───────────────────────────────┘     │  - product_id       : FK_Str    │  |
|                                        │  - quantity         : Int       │  |
|                                        └─────────────────────────────────┘  |
+─────────────────────────────────────────────────────────────────────────────+
    """
    
    map3_table = Table([[Paragraph(f"<pre>{ascii_map_3.replace(' ', '&nbsp;').replace('│', '|').replace('─', '-').replace('┌', '+').replace('┐', '+').replace('└', '+').replace('┘', '+').replace('┬', '+').replace('▼', 'v').replace('▲', '^').replace('├', '+').replace('┤', '+')}</pre>", styles['CodeBlock'])]], colWidths=[504])
    map3_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NEUTRAL_LIGHT),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(KeepTogether([map3_table]))
    
    # Render PDF Elements using our Numbered Canvas
    doc.build(story, canvasmaker=NumberedCanvas)

if __name__ == "__main__":
    build_pdf()