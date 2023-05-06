# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Function define the web page to view recent motion detection """
# pylint:disable=anomalous-unicode-escape-in-string
import io
import os
import server.httpserver
import server.httprequest
from htmltemplate          import *
import webpage.mainpage
import webpage.streamingpage

FOLDER_ICON   = b"\xF0\x9F\x93\x81"
TEXT_ICON     = b"\xf0\x9f\x93\x84"
IMAGE_ICON    = b"\xF0\x9F\x96\xBC"
TRASH_ICON    = b"\xF0\x9F\x97\x91"
BIN_ICON      = b"\xF0\x9F\x93\xA6"
DOWNLOAD_ICON = b"\xF0\x9F\x93\xA4"
UPLOAD_ICON   = b"\xF0\x9F\x93\xA5"
FILE_EXPLORER = b"/file_explorer"

def create_file_item(path="", filepath="", directory=False):
	""" Create file line with icon, name, size and date """
	if directory:
		icon = FOLDER_ICON
		url  = b"%s?path=%s"%(FILE_EXPLORER,tools.strings.tobytes(filepath))
	else:
		ext = tools.strings.tobytes(tools.filesystem.splitext(filepath)[1]).lower()
		mime = server.httprequest.MIMES.get(ext, b"binary")

		if b"image/" in mime:
			icon = IMAGE_ICON
			url  = b"%s/image_file?path=%s"%(FILE_EXPLORER,tools.strings.tobytes(filepath))
		elif b"text/" in mime or mime in [b"application/javascript", b"application/xml", b"application/xhtml+xml", b"application/json", b"application/typescript",]:
			icon = TEXT_ICON
			url  = b"%s/text_file?path=%s"%(FILE_EXPLORER,tools.strings.tobytes(filepath))
		else:
			icon = BIN_ICON
			url  = b"%s/bin_file?path=%s"%(FILE_EXPLORER,tools.strings.tobytes(filepath))

	if filepath=="..":
		icon = FOLDER_ICON
		url  = b"%s?path=%s"%(FILE_EXPLORER,tools.strings.tobytes(tools.filesystem.split(path)[0]))


	url   = b"location.href='%s'"%url
	style = b"font-family: monospace;cursor:pointer;white-space:nowrap;"
	name  = tools.strings.tobytes(tools.filesystem.split(filepath)[1])

	if directory:
		size = b""
		date = b""
		download = b""
	else:
		size = tools.strings.size_to_bytes(tools.filesystem.filesize(filepath))
		size = size.replace(b" ",b"&nbsp;")
		date = tools.date.date_to_bytes(tools.filesystem.filetime(filepath))
		download = Download(text=DOWNLOAD_ICON, path=FILE_EXPLORER+b"/download?path=%s"%tools.strings.tobytes(filepath), filename=tools.strings.tobytes(name))

	return Tr([
			Td(text=icon, onclick=url, style=style, width=b"1"),
			Td(text=name, onclick=url, style=style,           ),
			Td(text=size, onclick=url, style=style, width=b"1"),
			Td(text=date, onclick=url, style=style, width=b"1"),
			Td(download, width=b"1"),
			])

def get_root_link(filepath):
	""" Get """
	directories = []
	p = filepath
	not_link = False

	while True:
		p, directory = tools.filesystem.split(filepath)
		if directory == "":
			break
		else:
			if not_link is False:
				directories.insert(0, Span(text=tools.strings.tobytes(directory)))
				not_link = True
			else:
				directories.insert(0, Link(text=tools.strings.tobytes(directory), href=FILE_EXPLORER+b"?path=%s"%(tools.strings.tobytes(filepath))
				, class_=b"border", style=b"padding: 0.25rem;"))
			directories.insert(0,Span(text=b"/"))
		filepath = p

	directories = directories[1:]
	directories.insert(0, Link(text=b"/", href=FILE_EXPLORER+b"?path=/", class_=b"border", style=b"padding: 0.25rem;"))
	return directories

def list_files(path):
	""" List files """
	directories, filenames = tools.filesystem.scandir(path, "*", False)
	content = []
	directories.sort()

	if path != "/":
		directories.insert(0, "..")

	for directory in directories:
		content.append(create_file_item(path, directory, True))

	filenames.sort()
	for filename in filenames:
		content.append(create_file_item(path, filename, False))
	return Table(content)

def get_text_file(filename):
	""" Get text file """
	try:
		result = b'<code class="text-secondary">'
		# pylint:disable=unspecified-encoding
		with open(filename, "rb") as file:
			while True:
				line = file.readline()
				if len(line) == 0:
					break
				line = line.replace(b" ",b"&nbsp;")
				line = line.replace(b"\t",b"&nbsp;&nbsp;&nbsp;&nbsp;")
				line = line.replace(b">",b"&gt;")
				line = line.replace(b"<",b"&lt;")
				result += line.rstrip() + b"<br>"
		return result + b"</code>"
	except:
		return Span(text=tools.lang.failed_to_load)

def get_bin_file(filename):
	""" Dump binary file """
	try:
		out = io.BytesIO()
		out.write(b'<code class="text-secondary">')
		with open(filename, "rb") as file:
			width = 16
			offset = 0
			while True:
				data = file.read(width)
				if len(data) == 0:
					break
				out.write(b'%08X&nbsp;&nbsp;' % offset)
				tools.strings.dump_line(data, out, width, b"&nbsp;")
				offset += width
				out.write(b"<br>")
		out.write(b"</code>")
		return out.getvalue()
	except:
		return Span(text=tools.lang.failed_to_load)

@server.httpserver.HttpServer.add_route(FILE_EXPLORER+b'/download')
async def download_file_browser(request, response, args):
	""" Download file """
	path = tools.strings.tostrings(request.params.get(b"path", b""))
	tools.tasking.Tasks.slow_down()
	await response.send_file(path, headers=request.headers)

@server.httpserver.HttpServer.add_route(FILE_EXPLORER+b'/text_file')
async def text_file_page(request, response, args):
	""" Display text file page """
	path = tools.strings.tostrings(request.params.get(b"path", b""))
	filename = tools.filesystem.split(path)[1]
	page = webpage.mainpage.main_frame(request, response, args, tools.lang.item_explorer,
	[
		get_root_link(path), Span(b"&nbsp;"), Download(text=DOWNLOAD_ICON, path=FILE_EXPLORER+b"/download?path=%s"%tools.strings.tobytes(path), filename=tools.strings.tobytes(filename)),
		Br(), Br(),
		get_text_file(path)
	])
	await response.send_page(page)

@server.httpserver.HttpServer.add_route(FILE_EXPLORER+b'/bin_file')
async def bin_file_page(request, response, args):
	""" Display binary file page """
	path = tools.strings.tostrings(request.params.get(b"path", b""))
	filename = tools.filesystem.split(path)[1]
	page = webpage.mainpage.main_frame(request, response, args, tools.lang.item_explorer,
	[
		get_root_link(path), Span(b"&nbsp;"), Download(text=DOWNLOAD_ICON, path=FILE_EXPLORER+b"/download?path=%s"%tools.strings.tobytes(path), filename=tools.strings.tobytes(filename)),
		Br(), Br(),
		get_bin_file(path)
	])
	await response.send_page(page)

@server.httpserver.HttpServer.add_route(FILE_EXPLORER+b'/image_file')
async def image_file_page(request, response, args):
	""" Display image file page """
	path = tools.strings.tostrings(request.params.get(b"path", b""))
	filename = tools.filesystem.split(path)[1]
	page = webpage.mainpage.main_frame(request, response, args, tools.lang.item_explorer,
	[
		get_root_link(path), Span(b"&nbsp;"), Download(text=DOWNLOAD_ICON, path=FILE_EXPLORER+b"/download?path=%s"%tools.strings.tobytes(path), filename=tools.strings.tobytes(filename)),
		Br(), Br(),
		Image(src=FILE_EXPLORER+b'/download?path=%s'%tools.strings.tobytes(path), class_=b"w-100")
	])
	await response.send_page(page)

@server.httpserver.HttpServer.add_route(FILE_EXPLORER+b'', menu=tools.lang.menu_system, item=tools.lang.item_explorer)
async def file_explorer_page(request, response, args):
	""" Display file explorer page """
	if tools.filesystem.ismicropython():
		root = b"/"
	else:
		root = tools.strings.tobytes(os.getcwd())
	path = tools.strings.tostrings(request.params.get(b"path", root))
	page = webpage.mainpage.main_frame(request, response, args, tools.lang.item_explorer,
	[
		get_root_link(path),Br(), Br(),
		list_files(path)
	])
	await response.send_page(page)
