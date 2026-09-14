"""
Gerador de documentos DOCX e PDF profissionais
Arquivo: backend/app/services/document_generator.py
"""

from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from typing import Dict, Any
import io
from datetime import datetime


class DocumentGenerator:
    """
    Gera memoriais descritivos em formato DOCX/PDF
    """

    def __init__(self):
        self.document = None

    def generate_docx(
        self, content: Dict[str, Any], metadata: Dict[str, Any]
    ) -> io.BytesIO:
        """
        Gera documento DOCX formatado profissionalmente

        Args:
            content: Conteúdo renderizado do template
            metadata: Informações do projeto (título, autor, etc)

        Returns:
            BytesIO com documento DOCX
        """
        self.document = Document()
        self._setup_styles()
        self._add_cover_page(metadata)

        for section in content.get("sections", []):
            self._add_section(section)

        if content.get("calculations"):
            self._add_calculations(content["calculations"])

        if content.get("normas"):
            self._add_norms(content["normas"])

        self._add_project_data_block(metadata)

        file_stream = io.BytesIO()
        self.document.save(file_stream)
        file_stream.seek(0)
        return file_stream

    def _setup_styles(self):
        """Configura estilos do documento"""
        return None

    def _add_cover_page(self, metadata: Dict[str, Any]):
        """Capa enxuta: titulo + nome da obra (demais dados no final)."""
        def display(value: Any, fallback: str = "N/A") -> str:
            return str(value) if value not in (None, "") else fallback

        title = self.document.add_heading(
            metadata.get("title", "MEMORIAL DESCRITIVO"), 0
        )
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        subtitle = self.document.add_paragraph(metadata.get("subtitle", ""))
        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if subtitle.runs:
            subtitle_format = subtitle.runs[0].font
            subtitle_format.size = Pt(14)
            subtitle_format.color.rgb = RGBColor(89, 89, 89)

        self.document.add_paragraph("\n" * 3)
        obra = self.document.add_paragraph()
        obra.alignment = WD_ALIGN_PARAGRAPH.CENTER
        obra.add_run("Obra: ").bold = True
        obra.add_run(display(metadata.get("obra")))
        self.document.add_page_break()

    def _add_project_data_block(self, metadata: Dict[str, Any]):
        """Bloco de identificacao do projeto e responsabilidade no final."""
        def display(value: Any, fallback: str = "N/A") -> str:
            return str(value) if value not in (None, "") else fallback

        professional = metadata.get("professional", {}) or {}
        shared = metadata.get("shared_data", {}) or {}

        self.document.add_page_break()
        self.document.add_heading("DADOS DO PROJETO", level=1)

        info_table = self.document.add_table(rows=10, cols=2)
        info_table.style = "Light Grid Accent 1"
        info_data = [
            ("Obra:", display(metadata.get("obra"))),
            ("Local:", display(metadata.get("local") or shared.get("localizacao"))),
            ("Município:", display(shared.get("municipio"))),
            ("UF:", display(shared.get("uf"))),
            ("Área construída:", display(shared.get("area_construida"))),
            ("Pavimentos:", display(shared.get("numero_pavimentos"))),
            ("Responsável Técnico:", display(metadata.get("responsavel") or professional.get("full_name"))),
            ("CREA:", display(metadata.get("crea"))),
            ("Empresa:", display(professional.get("company_name"))),
            ("ART/RRT:", display(professional.get("art_number") or professional.get("rrt_number"))),
        ]
        for i, (label, value) in enumerate(info_data):
            info_table.rows[i].cells[0].text = label
            info_table.rows[i].cells[1].text = value

        self.document.add_heading("RESPONSABILIDADE TÉCNICA", level=1)
        signature = self.document.add_paragraph()
        signature.add_run("Profissional: ").bold = True
        signature.add_run(display(professional.get("full_name") or metadata.get("responsavel"), "A definir"))
        signature.add_run("\nTítulo: ").bold = True
        signature.add_run(display(professional.get("professional_title"), "Engenheiro(a)"))
        signature.add_run("\nRegistro: ").bold = True
        signature.add_run(display(metadata.get("crea"), "A definir"))
        signature.add_run("\nData: ").bold = True
        signature.add_run(datetime.now().strftime("%d/%m/%Y"))
        signature.add_run("\nAssinatura: ").bold = True
        signature.add_run("Pendente de assinatura eletrônica certificada")

    def _add_section(self, section: Dict[str, Any]):
        """Adiciona seção ao documento"""
        self.document.add_heading(section["title"], level=1)
        self.document.add_paragraph(section["content"])
        for subsection in section.get("subsections", []):
            self.document.add_heading(subsection["title"], level=2)
            self.document.add_paragraph(subsection["content"])

    def _add_calculations(self, calculations: Dict[str, Any]):
        """Adiciona seção de cálculos"""
        self.document.add_page_break()
        self.document.add_heading("CÁLCULOS E DIMENSIONAMENTOS", level=1)

        for calc_name, calc_data in calculations.items():
            if "error" not in calc_data:
                p = self.document.add_paragraph()
                p.add_run(f"{calc_name}: ").bold = True
                p.add_run(f"{calc_data['value']:.2f} {calc_data['unit']}")
                p.add_run(f"\nFórmula: {calc_data['formula']}").italic = True

    def _add_norms(self, normas: list):
        """Adiciona referências normativas"""
        self.document.add_page_break()
        self.document.add_heading("NORMAS TÉCNICAS APLICÁVEIS", level=1)
        for norma in normas:
            self.document.add_paragraph(norma, style="List Bullet")

    def generate_pdf(
        self, content: Dict[str, Any], metadata: Dict[str, Any]
    ) -> io.BytesIO:
        """Gera PDF com ReportLab a partir do conteúdo já renderizado."""
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            ListFlowable,
            ListItem,
        )

        def display(value: Any, fallback: str = "N/A") -> str:
            return str(value) if value not in (None, "") else fallback

        buffer = io.BytesIO()
        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
            title=display(metadata.get("title"), "Memorial Descritivo"),
        )
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontSize=18, spaceAfter=12))
        styles.add(ParagraphStyle(name="BodyTextPt", parent=styles["BodyText"], fontSize=11, leading=14, spaceAfter=8))
        styles.add(ParagraphStyle(name="MetaLine", parent=styles["Normal"], fontSize=10, leading=13, spaceAfter=4))

        story = []
        professional = metadata.get("professional", {}) or {}
        shared = metadata.get("shared_data", {}) or {}
        story.append(Paragraph(display(metadata.get("title"), "MEMORIAL DESCRITIVO"), styles["CoverTitle"]))
        if metadata.get("subtitle"):
            story.append(Paragraph(display(metadata.get("subtitle")), styles["BodyTextPt"]))
        story.append(Spacer(1, 0.4 * cm))
        story.append(Paragraph(f"<b>Obra:</b> {display(metadata.get('obra'))}", styles["MetaLine"]))
        story.append(Spacer(1, 0.6 * cm))

        for section in content.get("sections", []):
            story.append(Paragraph(display(section.get("title"), "Seção"), styles["Heading1"]))
            story.append(Paragraph(display(section.get("content"), "").replace("\n", "<br/>"), styles["BodyTextPt"]))
            for subsection in section.get("subsections", []):
                story.append(Paragraph(display(subsection.get("title"), "Subseção"), styles["Heading2"]))
                story.append(
                    Paragraph(
                        display(subsection.get("content"), "").replace("\n", "<br/>"),
                        styles["BodyTextPt"],
                    )
                )

        calculations = content.get("calculations") or {}
        if calculations:
            story.append(Paragraph("Cálculos e dimensionamentos", styles["Heading1"]))
            for calc_name, calc_data in calculations.items():
                if "error" in calc_data:
                    continue
                story.append(
                    Paragraph(
                        f"<b>{calc_name}:</b> {calc_data.get('value', '')} {calc_data.get('unit', '')}<br/>"
                        f"<i>Fórmula: {calc_data.get('formula', '')}</i>",
                        styles["BodyTextPt"],
                    )
                )

        normas = content.get("normas") or []
        if normas:
            story.append(Paragraph("Normas técnicas aplicáveis", styles["Heading1"]))
            items = [ListItem(Paragraph(str(norma), styles["BodyTextPt"])) for norma in normas]
            story.append(ListFlowable(items, bulletType="bullet"))

        story.append(Paragraph("Dados do projeto", styles["Heading1"]))
        story.append(Paragraph(f"<b>Local:</b> {display(metadata.get('local') or shared.get('localizacao'))}", styles["MetaLine"]))
        story.append(Paragraph(f"<b>Município:</b> {display(shared.get('municipio'))}", styles["MetaLine"]))
        story.append(Paragraph(f"<b>UF:</b> {display(shared.get('uf'))}", styles["MetaLine"]))
        story.append(
            Paragraph(
                f"<b>Responsável técnico:</b> {display(professional.get('full_name') or metadata.get('responsavel'))}",
                styles["MetaLine"],
            )
        )
        story.append(Paragraph(f"<b>CREA:</b> {display(metadata.get('crea'))}", styles["MetaLine"]))
        story.append(Paragraph(f"<b>Data:</b> {datetime.now().strftime('%d/%m/%Y')}", styles["MetaLine"]))

        document.build(story)
        buffer.seek(0)
        return buffer
