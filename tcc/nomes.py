"""Nomes dos documentos gerados, formados pelo tema do TCC.

O tema é o título do trabalho, sem acentos e com sublinhados, para que os
arquivos possam ser enviados a qualquer sistema.
"""
TEMA = "Modelagem_e_simulacao_de_mecanismos_passivos_de_apoio_ao_braco"
BASE = f"TCC_{TEMA}"

ORIGINAL = "TCC_apenas_exo1.docx"     # DOCX do autor, só leitura
FUNDIDO = f"{BASE}.docx"              # conteúdo, gerado por gerar_tcc_fundido.py
MODELO_FT = f"{BASE}_modelo_FT.docx"  # formato do PDF, gerado por gerar_docx_modelo.py
PDF = f"{BASE}.pdf"                   # latexmk -pdf -jobname=<BASE> tese.tex, em latex/
