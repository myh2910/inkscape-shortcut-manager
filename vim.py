import os
import tempfile
import subprocess
from constants import TARGET
from clipboard import copy
from config import config
from Xlib import X

def open_vim(self, compile_latex):
	f = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.tex')
	if compile_latex:
		template = config['latex_document']()
	else:
		template = ''
	f.write(template)
	f.close()

	config['open_editor'](f.name)
	created_time = os.path.getmtime(f.name)
	while True:
		if os.path.getmtime(f.name) != created_time:
			latex = open(f.name, 'r').read()
			break

	os.remove(f.name)
	if latex.strip() == '':
		print('Empty file')
		return False

	if latex.strip() != template.strip():
		if not compile_latex:
			svg = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
	<svg>
		<text
			style="font-size:{config['font_size']}px; font-family:'{config['font']}';-inkscape-font-specification:'{config['font']},Normal';fill:#000000;fill-opacity:1;stroke:none;"
			xml:space="preserve"><tspan sodipodi:role="line">{latex}</tspan></text>
	</svg>
"""
			copy(svg, target=TARGET)
		else:
			m = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.tex')
			m.write(latex)
			m.close()

			working_directory = tempfile.gettempdir()
			subprocess.run(
				['pdflatex', m.name],
				cwd=working_directory,
				stdout=subprocess.DEVNULL,
				stderr=subprocess.DEVNULL
			)

			base_name = os.path.splitext(m.name)[0]
			subprocess.run(
				['pdf2svg', f'{base_name}.pdf', f'{base_name}.svg'],
				cwd=working_directory
			)

			with open(f'{base_name}.svg') as svg:
				subprocess.run(
					['xclip', '-selection', 'c', '-target', TARGET],
					stdin=svg
				)
			for ext in ['pdf', 'svg', 'aux', 'pre', 'log', 'tex']:
				file_name = f'{base_name}.{ext}'
				if os.path.exists(file_name):
					os.remove(file_name)

		print('Done!')
	self.press('Escape')
