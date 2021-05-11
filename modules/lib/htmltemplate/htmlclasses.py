''' File automatically generated with template.html content '''
from htmltemplate.template import Template 

# <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css">
# <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
# <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.16.0/umd/popper.min.js"></script>
# <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.min.js"></script>
begTagStylesheet = b'''<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css"><script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script><script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.16.0/umd/popper.min.js"></script><script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.min.js"></script>'''
def Stylesheet(*args, **params):
	self = Template(*(("Stylesheet",) + args), **params)

	def getBegin(self):
		global begTagStylesheet
		return begTagStylesheet
	self.getBegin     = getBegin

	def getEnd(self):
		return b''
	self.getEnd       = getEnd

	return self

# <link rel="stylesheet" href="stylesheet.css">
begTagStylesheetDefault = b'''<link rel="stylesheet" href="stylesheet.css">'''
def StylesheetDefault(*args, **params):
	self = Template(*(("StylesheetDefault",) + args), **params)

	def getBegin(self):
		global begTagStylesheetDefault
		return begTagStylesheetDefault
	self.getBegin     = getBegin

	def getEnd(self):
		return b''
	self.getEnd       = getEnd

	return self

# <div class="%(class_)s" style="%(style)s" id="%(id)s">%(content)s</div>
begTagDiv = b'''<div class="%s" style="%s" id="%s">'''
endTagDiv = b'''</div>'''
def Div(*args, **params):
	self = Template(*(("Div",) + args), **params)

	def getBegin(self):
		global begTagDiv
		return begTagDiv%(self.class_,self.style,self.id)
	self.getBegin     = getBegin

	def getEnd(self):
		global endTagDiv
		return endTagDiv
	self.getEnd       = getEnd

	self.content      = params.get("content", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.class_       = params.get("class_", b"")
	return self

# <option %(selected)s name="%(text)s" value="%(value)s" %(disabled)s>%(text)s</option>
begTagOption = b'''<option %s name="%s" value="%s" %s>%s</option>'''
def Option(*args, **params):
	self = Template(*(("Option",) + args), **params)

	def getBegin(self):
		global begTagOption
		return begTagOption%( b'selected' if self.selected else b'',self.text,self.value, b'disabled' if self.disabled else b'',self.text)
	self.getBegin     = getBegin

	def getEnd(self):
		return b''
	self.getEnd       = getEnd

	self.text         = params.get("text", b"")
	self.selected     = params.get("selected", b"")
	self.disabled     = params.get("disabled", False)
	self.value        = params.get("value", b"")
	return self

# <label >%(text)s</label>
# <select class="custom-select %(class_)s" style="%(style)s" id="%(id)s" name="%(name)s" %(disabled)s>
# %(content)s
# </select>
# <br>
# <br>
begTagSelect = b'''<label >%s</label><select class="custom-select %s" style="%s" id="%s" name="%s" %s>'''
endTagSelect = b'''</select><br><br>'''
def Select(*args, **params):
	self = Template(*(("Select",) + args), **params)

	def getBegin(self):
		global begTagSelect
		return begTagSelect%(self.text,self.class_,self.style,self.id,self.name, b'disabled' if self.disabled else b'')
	self.getBegin     = getBegin

	def getEnd(self):
		global endTagSelect
		return endTagSelect
	self.getEnd       = getEnd

	self.id           = params.get("id", b"%d"%id(self))
	self.content      = params.get("content", b"")
	self.style        = params.get("style", b"")
	self.name         = params.get("name", b"%d"%id(self))
	self.text         = params.get("text", b"")
	self.class_       = params.get("class_", b"")
	self.disabled     = params.get("disabled", False)
	return self

# <h1 class="%(class_)s" style="%(style)s" id="%(id)s">%(text)s</h1>
begTagTitle1 = b'''<h1 class="%s" style="%s" id="%s">%s</h1>'''
def Title1(*args, **params):
	self = Template(*(("Title1",) + args), **params)

	def getBegin(self):
		global begTagTitle1
		return begTagTitle1%(self.class_,self.style,self.id,self.text)
	self.getBegin     = getBegin

	def getEnd(self):
		return b''
	self.getEnd       = getEnd

	self.text         = params.get("text", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.class_       = params.get("class_", b"")
	return self

# <h2 class="%(class_)s" style="%(style)s" id="%(id)s">%(text)s</h2>
begTagTitle2 = b'''<h2 class="%s" style="%s" id="%s">%s</h2>'''
def Title2(*args, **params):
	self = Template(*(("Title2",) + args), **params)

	def getBegin(self):
		global begTagTitle2
		return begTagTitle2%(self.class_,self.style,self.id,self.text)
	self.getBegin     = getBegin

	def getEnd(self):
		return b''
	self.getEnd       = getEnd

	self.text         = params.get("text", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.class_       = params.get("class_", b"")
	return self

# <h3 class="%(class_)s" style="%(style)s" id="%(id)s">%(text)s</h3>
begTagTitle3 = b'''<h3 class="%s" style="%s" id="%s">%s</h3>'''
def Title3(*args, **params):
	self = Template(*(("Title3",) + args), **params)

	def getBegin(self):
		global begTagTitle3
		return begTagTitle3%(self.class_,self.style,self.id,self.text)
	self.getBegin     = getBegin

	def getEnd(self):
		return b''
	self.getEnd       = getEnd

	self.text         = params.get("text", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.class_       = params.get("class_", b"")
	return self

# <h4 class="%(class_)s" style="%(style)s" id="%(id)s">%(text)s</h4>
begTagTitle4 = b'''<h4 class="%s" style="%s" id="%s">%s</h4>'''
def Title4(*args, **params):
	self = Template(*(("Title4",) + args), **params)

	def getBegin(self):
		global begTagTitle4
		return begTagTitle4%(self.class_,self.style,self.id,self.text)
	self.getBegin     = getBegin

	def getEnd(self):
		return b''
	self.getEnd       = getEnd

	self.text         = params.get("text", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.class_       = params.get("class_", b"")
	return self

# <label class="%(class_)s" style="%(style)s" id="%(id)s">%(text)s</label>
begTagLabel = b'''<label class="%s" style="%s" id="%s">%s</label>'''
def Label(*args, **params):
	self = Template(*(("Label",) + args), **params)

	def getBegin(self):
		global begTagLabel
		return begTagLabel%(self.class_,self.style,self.id,self.text)
	self.getBegin     = getBegin

	def getEnd(self):
		return b''
	self.getEnd       = getEnd

	self.text         = params.get("text", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.class_       = params.get("class_", b"")
	return self

# <div class="form-group">
# <input class="form-control %(class_)s" style="%(style)s" id="%(id)s" pattern="%(pattern)s" placeholder="%(placeholder)s" type="%(type)s" value="%(value)s" name="%(name)s" %(disabled)s>
# </div>
begTagInput = b'''<div class="form-group"><input class="form-control %s" style="%s" id="%s" pattern="%s" placeholder="%s" type="%s" value="%s" name="%s" %s></div>'''
def Input(*args, **params):
	self = Template(*(("Input",) + args), **params)

	def getBegin(self):
		global begTagInput
		return begTagInput%(self.class_,self.style,self.id,self.pattern,self.placeholder,self.type,self.value,self.name, b'disabled' if self.disabled else b'')
	self.getBegin     = getBegin

	def getEnd(self):
		return b''
	self.getEnd       = getEnd

	self.type         = params.get("type", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.class_       = params.get("class_", b"")
	self.name         = params.get("name", b"%d"%id(self))
	self.value        = params.get("value", b"")
	self.pattern      = params.get("pattern", b"*")
	self.placeholder  = params.get("placeholder", b"")
	self.disabled     = params.get("disabled", False)
	return self

# <label for="customRange">%(text)s</label>
# <div style="display: flex;">
# <input type="range" class="custom-range %(class_)s" style="%(style)s" id="slider_%(id)s" name="%(name)s" min="%(min)s" max="%(max)s" step="%(step)s" value="%(value)s" %(disabled)s oninput="onchange_%(id)s()" />
# <span id="value_%(id)s"/>
# </div>
# <script type="text/javascript">
# function onchange_%(id)s() 
# {
# document.getElementById("value_%(id)s").innerHTML = "&nbsp;" + document.getElementById("slider_%(id)s").value;
# }
# onchange_%(id)s();
# </script>
begTagSlider = b'''<label for="customRange">%s</label><div style="display: flex;"><input type="range" class="custom-range %s" style="%s" id="slider_%s" name="%s" min="%s" max="%s" step="%s" value="%s" %s oninput="onchange_%s()" /><span id="value_%s"/></div><script type="text/javascript">function onchange_%s(){document.getElementById("value_%s").innerHTML = "&nbsp;" + document.getElementById("slider_%s").value;}onchange_%s();</script>'''
def Slider(*args, **params):
	self = Template(*(("Slider",) + args), **params)

	def getBegin(self):
		global begTagSlider
		return begTagSlider%(self.text,self.class_,self.style,self.id,self.name,self.min,self.max,self.step,self.value, b'disabled' if self.disabled else b'',self.id,self.id,self.id,self.id,self.id,self.id)
	self.getBegin     = getBegin

	def getEnd(self):
		return b''
	self.getEnd       = getEnd

	self.max          = params.get("max", b"")
	self.min          = params.get("min", b"")
	self.step         = params.get("step", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.name         = params.get("name", b"%d"%id(self))
	self.text         = params.get("text", b"")
	self.class_       = params.get("class_", b"")
	self.value        = params.get("value", b"")
	self.disabled     = params.get("disabled", False)
	return self

# <div class="form-group">
# <label >%(text)s</label>
# <input type="%(type)s" class="form-control %(class_)s" style="%(style)s" id="%(id)s" pattern="%(pattern)s" placeholder="%(placeholder)s" type="%(type)s" value="%(value)s" name="%(name)s" %(disabled)s>
# </div>
begTagEdit = b'''<div class="form-group"><label >%s</label><input type="%s" class="form-control %s" style="%s" id="%s" pattern="%s" placeholder="%s" type="%s" value="%s" name="%s" %s></div>'''
def Edit(*args, **params):
	self = Template(*(("Edit",) + args), **params)

	def getBegin(self):
		global begTagEdit
		return begTagEdit%(self.text,self.type,self.class_,self.style,self.id,self.pattern,self.placeholder,self.type,self.value,self.name, b'disabled' if self.disabled else b'')
	self.getBegin     = getBegin

	def getEnd(self):
		return b''
	self.getEnd       = getEnd

	self.pattern      = params.get("pattern", b"*")
	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.class_       = params.get("class_", b"")
	self.text         = params.get("text", b"")
	self.name         = params.get("name", b"%d"%id(self))
	self.value        = params.get("value", b"")
	self.type         = params.get("type", b"")
	self.placeholder  = params.get("placeholder", b"")
	self.disabled     = params.get("disabled", False)
	return self

# <div class="custom-control custom-switch">
# <input type="checkbox" class="custom-control-input %(class_)s" style="%(style)s" id="%(id)s" value="%(value)s" name="%(name)s" %(checked)s %(disabled)s>
# <label class="custom-control-label" for="%(id)s">%(text)s</label>
# </div>
# <br>
begTagSwitch = b'''<div class="custom-control custom-switch"><input type="checkbox" class="custom-control-input %s" style="%s" id="%s" value="%s" name="%s" %s %s><label class="custom-control-label" for="%s">%s</label></div><br>'''
def Switch(*args, **params):
	self = Template(*(("Switch",) + args), **params)

	def getBegin(self):
		global begTagSwitch
		return begTagSwitch%(self.class_,self.style,self.id,self.value,self.name, b'checked' if self.checked else b'', b'disabled' if self.disabled else b'',self.id,self.text)
	self.getBegin     = getBegin

	def getEnd(self):
		return b''
	self.getEnd       = getEnd

	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.name         = params.get("name", b"%d"%id(self))
	self.class_       = params.get("class_", b"")
	self.text         = params.get("text", b"")
	self.value        = params.get("value", b"")
	self.checked      = params.get("checked", True)
	self.disabled     = params.get("disabled", False)
	return self

# <div class="form-check">
# <label class="form-check-label">
# <input type="checkbox" class="form-check-input %(class_)s" style="%(style)s" id="%(id)s" value="%(value)s" name="%(name)s" %(checked)s %(disabled)s>%(text)s
# </label>
# </div>
begTagCheckbox = b'''<div class="form-check"><label class="form-check-label"><input type="checkbox" class="form-check-input %s" style="%s" id="%s" value="%s" name="%s" %s %s>%s</label></div>'''
def Checkbox(*args, **params):
	self = Template(*(("Checkbox",) + args), **params)

	def getBegin(self):
		global begTagCheckbox
		return begTagCheckbox%(self.class_,self.style,self.id,self.value,self.name, b'checked' if self.checked else b'', b'disabled' if self.disabled else b'',self.text)
	self.getBegin     = getBegin

	def getEnd(self):
		return b''
	self.getEnd       = getEnd

	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.name         = params.get("name", b"%d"%id(self))
	self.class_       = params.get("class_", b"")
	self.text         = params.get("text", b"")
	self.value        = params.get("value", b"")
	self.checked      = params.get("checked", True)
	self.disabled     = params.get("disabled", False)
	return self

# <input class="btn %(class_)s" style="%(style)s" id="%(id)s" type="button" name="%(name)s" %(disabled)s> %(text)s</input>
begTagButton = b'''<input class="btn %s" style="%s" id="%s" type="button" name="%s" %s> %s</input>'''
def Button(*args, **params):
	self = Template(*(("Button",) + args), **params)

	def getBegin(self):
		global begTagButton
		return begTagButton%(self.class_,self.style,self.id,self.name, b'disabled' if self.disabled else b'',self.text)
	self.getBegin     = getBegin

	def getEnd(self):
		return b''
	self.getEnd       = getEnd

	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.name         = params.get("name", b"%d"%id(self))
	self.class_       = params.get("class_", b"")
	self.text         = params.get("text", b"")
	self.disabled     = params.get("disabled", False)
	return self

# <div class="form-check">
# <label class="form-check-label">
# <input type="radio" class="form-check-input %(class_)s" style="%(style)s" id="%(id)s" name="%(name)s" %(checked)s %(disabled)s>%(text)s
# </label>
# </div>
begTagRadio = b'''<div class="form-check"><label class="form-check-label"><input type="radio" class="form-check-input %s" style="%s" id="%s" name="%s" %s %s>%s</label></div>'''
def Radio(*args, **params):
	self = Template(*(("Radio",) + args), **params)

	def getBegin(self):
		global begTagRadio
		return begTagRadio%(self.class_,self.style,self.id,self.name, b'checked' if self.checked else b'', b'disabled' if self.disabled else b'',self.text)
	self.getBegin     = getBegin

	def getEnd(self):
		return b''
	self.getEnd       = getEnd

	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.name         = params.get("name", b"%d"%id(self))
	self.class_       = params.get("class_", b"")
	self.text         = params.get("text", b"")
	self.checked      = params.get("checked", True)
	self.disabled     = params.get("disabled", False)
	return self

# <input type="file"  style="display: none;" 
# id="%(id)s" 
# onchange="document.getElementById('label_%(id)s').value=document.getElementById('%(id)s').value.split(/[\\\/]/).pop();" 
# accept="%(accept)s" name="%(name)s" %(disabled)s />
# <input type="button" id="label_%(id)s" value="%(text)s" onclick="document.getElementById('%(id)s').click()" class="btn btn-outline-primary " %(disabled)s />
begTagChooseFile = b'''<input type="file"  style="display: none;"id="%s"onchange="document.getElementById('label_%s').value=document.getElementById('%s').value.split(/[\\\/]/).pop();"accept="%s" name="%s" %s /><input type="button" id="label_%s" value="%s" onclick="document.getElementById('%s').click()" class="btn btn-outline-primary " %s />'''
def ChooseFile(*args, **params):
	self = Template(*(("ChooseFile",) + args), **params)

	def getBegin(self):
		global begTagChooseFile
		return begTagChooseFile%(self.id,self.id,self.id,self.accept,self.name, b'disabled' if self.disabled else b'',self.id,self.text,self.id, b'disabled' if self.disabled else b'')
	self.getBegin     = getBegin

	def getEnd(self):
		return b''
	self.getEnd       = getEnd

	self.id           = params.get("id", b"%d"%id(self))
	self.name         = params.get("name", b"%d"%id(self))
	self.text         = params.get("text", b"")
	self.accept       = params.get("accept", b"")
	self.disabled     = params.get("disabled", False)
	return self

# <input type="file" style="display:none" id="%(id)s" onchange="importFile_%(id)s()" name="%(name)s" accept="%(accept)s" %(disabled)s />
# <input type="button" id="label_%(id)s" value="%(text)s" onclick="document.getElementById('%(id)s').click()" class="btn btn-outline-primary " %(disabled)s />
# <script>
# function importFile_%(id)s()
# {
# let data = document.getElementById('%(id)s').files[0];
# let entry = document.getElementById('%(id)s').files[0];
# fetch('%(path)s/' + encodeURIComponent(entry.name), {method:'PUT',body:data});
# if ("%(alert)s" != "")
# {
# alert('%(alert)s');
# }
# document.getElementById('%(id)s').value = "";
# location.reload();
# }
# </script>
begTagImportFile = b'''<input type="file" style="display:none" id="%s" onchange="importFile_%s()" name="%s" accept="%s" %s /><input type="button" id="label_%s" value="%s" onclick="document.getElementById('%s').click()" class="btn btn-outline-primary " %s /><script>function importFile_%s(){let data = document.getElementById('%s').files[0];let entry = document.getElementById('%s').files[0];fetch('%s/' + encodeURIComponent(entry.name), {method:'PUT',body:data});if ("%s" != ""){alert('%s');}document.getElementById('%s').value = "";location.reload();}</script>'''
def ImportFile(*args, **params):
	self = Template(*(("ImportFile",) + args), **params)

	def getBegin(self):
		global begTagImportFile
		return begTagImportFile%(self.id,self.id,self.name,self.accept, b'disabled' if self.disabled else b'',self.id,self.text,self.id, b'disabled' if self.disabled else b'',self.id,self.id,self.id,self.path,self.alert,self.alert,self.id)
	self.getBegin     = getBegin

	def getEnd(self):
		return b''
	self.getEnd       = getEnd

	self.id           = params.get("id", b"%d"%id(self))
	self.alert        = params.get("alert", b"")
	self.name         = params.get("name", b"%d"%id(self))
	self.text         = params.get("text", b"")
	self.path         = params.get("path", b"")
	self.accept       = params.get("accept", b"")
	self.disabled     = params.get("disabled", False)
	return self

# <a href="%(path)s" download="%(filename)s" class="btn btn-outline-primary " name="%(name)s" %(disabled)s>%(text)s</a>
begTagExportFile = b'''<a href="%s" download="%s" class="btn btn-outline-primary " name="%s" %s>%s</a>'''
def ExportFile(*args, **params):
	self = Template(*(("ExportFile",) + args), **params)

	def getBegin(self):
		global begTagExportFile
		return begTagExportFile%(self.path,self.filename,self.name, b'disabled' if self.disabled else b'',self.text)
	self.getBegin     = getBegin

	def getEnd(self):
		return b''
	self.getEnd       = getEnd

	self.filename     = params.get("filename", b"")
	self.name         = params.get("name", b"%d"%id(self))
	self.text         = params.get("text", b"")
	self.path         = params.get("path", b"")
	self.disabled     = params.get("disabled", False)
	return self

# <form class="container %(class_)s" style="%(style)s" id="%(id)s" method="%(method)s">
# %(content)s
# </form>
begTagForm = b'''<form class="container %s" style="%s" id="%s" method="%s">'''
endTagForm = b'''</form>'''
def Form(*args, **params):
	self = Template(*(("Form",) + args), **params)

	def getBegin(self):
		global begTagForm
		return begTagForm%(self.class_,self.style,self.id,self.method)
	self.getBegin     = getBegin

	def getEnd(self):
		global endTagForm
		return endTagForm
	self.getEnd       = getEnd

	self.content      = params.get("content", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.class_       = params.get("class_", b"")
	self.method       = params.get("method", b"")
	return self

# <br/>
begTagBr = b'''<br/>'''
def Br(*args, **params):
	self = Template(*(("Br",) + args), **params)

	def getBegin(self):
		global begTagBr
		return begTagBr
	self.getBegin     = getBegin

	def getEnd(self):
		return b''
	self.getEnd       = getEnd

	return self

# <div class="container %(class_)s" style="%(style)s" id="%(id)s">
# %(content)s
# </div>
begTagContainer = b'''<div class="container %s" style="%s" id="%s">'''
endTagContainer = b'''</div>'''
def Container(*args, **params):
	self = Template(*(("Container",) + args), **params)

	def getBegin(self):
		global begTagContainer
		return begTagContainer%(self.class_,self.style,self.id)
	self.getBegin     = getBegin

	def getEnd(self):
		global endTagContainer
		return endTagContainer
	self.getEnd       = getEnd

	self.content      = params.get("content", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.class_       = params.get("class_", b"")
	return self

# <div class="card shadow %(class_)s" style="%(style)s" id="%(id)s">
# %(content)s
# </div>
begTagCard = b'''<div class="card shadow %s" style="%s" id="%s">'''
endTagCard = b'''</div>'''
def Card(*args, **params):
	self = Template(*(("Card",) + args), **params)

	def getBegin(self):
		global begTagCard
		return begTagCard%(self.class_,self.style,self.id)
	self.getBegin     = getBegin

	def getEnd(self):
		global endTagCard
		return endTagCard
	self.getEnd       = getEnd

	self.content      = params.get("content", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.class_       = params.get("class_", b"")
	return self

# <p class="%(class_)s" style="%(style)s" id="%(id)s">%(content)s%(text)s</p>
begTagParagraph = b'''<p class="%s" style="%s" id="%s">'''
endTagParagraph = b'''%s</p>'''
def Paragraph(*args, **params):
	self = Template(*(("Paragraph",) + args), **params)

	def getBegin(self):
		global begTagParagraph
		return begTagParagraph%(self.class_,self.style,self.id)
	self.getBegin     = getBegin

	def getEnd(self):
		global endTagParagraph
		return endTagParagraph%(self.text)
	self.getEnd       = getEnd

	self.content      = params.get("content", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.class_       = params.get("class_", b"")
	self.text         = params.get("text", b"")
	return self

# <li class="list-group-item %(class_)s" style="%(style)s" id="%(id)s">%(content)s%(text)s</li>
begTagListItem = b'''<li class="list-group-item %s" style="%s" id="%s">'''
endTagListItem = b'''%s</li>'''
def ListItem(*args, **params):
	self = Template(*(("ListItem",) + args), **params)

	def getBegin(self):
		global begTagListItem
		return begTagListItem%(self.class_,self.style,self.id)
	self.getBegin     = getBegin

	def getEnd(self):
		global endTagListItem
		return endTagListItem%(self.text)
	self.getEnd       = getEnd

	self.content      = params.get("content", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.class_       = params.get("class_", b"")
	self.text         = params.get("text", b"")
	return self

# <button class="btn %(class_)s" style="%(style)s" id="%(id)s">%(content)s%(text)s</button><br>
begTagButtonItem = b'''<button class="btn %s" style="%s" id="%s">'''
endTagButtonItem = b'''%s</button><br>'''
def ButtonItem(*args, **params):
	self = Template(*(("ButtonItem",) + args), **params)

	def getBegin(self):
		global begTagButtonItem
		return begTagButtonItem%(self.class_,self.style,self.id)
	self.getBegin     = getBegin

	def getEnd(self):
		global endTagButtonItem
		return endTagButtonItem%(self.text)
	self.getEnd       = getEnd

	self.content      = params.get("content", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.class_       = params.get("class_", b"")
	self.text         = params.get("text", b"")
	return self

# <ul class="list-group %(class_)s" style="%(style)s" id="%(id)s">
# %(content)s
# </ul>
begTagList = b'''<ul class="list-group %s" style="%s" id="%s">'''
endTagList = b'''</ul>'''
def List(*args, **params):
	self = Template(*(("List",) + args), **params)

	def getBegin(self):
		global begTagList
		return begTagList%(self.class_,self.style,self.id)
	self.getBegin     = getBegin

	def getEnd(self):
		global endTagList
		return endTagList
	self.getEnd       = getEnd

	self.content      = params.get("content", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.class_       = params.get("class_", b"")
	return self

# <button class="btn btn-outline-primary %(class_)s" style="%(style)s" id="%(id)s" type="submit" value="%(value)s">%(content)s%(text)s</button>
begTagSubmit = b'''<button class="btn btn-outline-primary %s" style="%s" id="%s" type="submit" value="%s">'''
endTagSubmit = b'''%s</button>'''
def Submit(*args, **params):
	self = Template(*(("Submit",) + args), **params)

	def getBegin(self):
		global begTagSubmit
		return begTagSubmit%(self.class_,self.style,self.id,self.value)
	self.getBegin     = getBegin

	def getEnd(self):
		global endTagSubmit
		return endTagSubmit%(self.text)
	self.getEnd       = getEnd

	self.content      = params.get("content", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.class_       = params.get("class_", b"")
	self.text         = params.get("text", b"")
	self.value        = params.get("value", b"")
	return self

# <a class="btn btn-outline-primary %(class_)s" style="%(style)s" id="%(id)s" href="%(href)s">%(content)s%(text)s</a>
begTagCancel = b'''<a class="btn btn-outline-primary %s" style="%s" id="%s" href="%s">'''
endTagCancel = b'''%s</a>'''
def Cancel(*args, **params):
	self = Template(*(("Cancel",) + args), **params)

	def getBegin(self):
		global begTagCancel
		return begTagCancel%(self.class_,self.style,self.id,self.href)
	self.getBegin     = getBegin

	def getEnd(self):
		global endTagCancel
		return endTagCancel%(self.text)
	self.getEnd       = getEnd

	self.content      = params.get("content", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.class_       = params.get("class_", b"")
	self.text         = params.get("text", b"")
	self.href         = params.get("href", b"")
	return self

# <a class="%(class_)s" style="%(style)s" id="%(id)s" href="%(href)s">%(content)s%(text)s</a>
begTagLink = b'''<a class="%s" style="%s" id="%s" href="%s">'''
endTagLink = b'''%s</a>'''
def Link(*args, **params):
	self = Template(*(("Link",) + args), **params)

	def getBegin(self):
		global begTagLink
		return begTagLink%(self.class_,self.style,self.id,self.href)
	self.getBegin     = getBegin

	def getEnd(self):
		global endTagLink
		return endTagLink%(self.text)
	self.getEnd       = getEnd

	self.content      = params.get("content", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.class_       = params.get("class_", b"")
	self.text         = params.get("text", b"")
	self.href         = params.get("href", b"")
	return self

# <li class="nav-item">
# <a class="nav-link btn-outline-primary %(active)s %(class_)s" style="%(style)s" id="%(id)s" href="%(href)s" %(disabled)s>%(content)s%(text)s</a>
# </li>
begTagTabItem = b'''<li class="nav-item"><a class="nav-link btn-outline-primary %s %s" style="%s" id="%s" href="%s" %s>'''
endTagTabItem = b'''%s</a></li>'''
def TabItem(*args, **params):
	self = Template(*(("TabItem",) + args), **params)

	def getBegin(self):
		global begTagTabItem
		return begTagTabItem%( b'active' if self.active else b'',self.class_,self.style,self.id,self.href, b'disabled' if self.disabled else b'')
	self.getBegin     = getBegin

	def getEnd(self):
		global endTagTabItem
		return endTagTabItem%(self.text)
	self.getEnd       = getEnd

	self.active       = params.get("active", False)
	self.id           = params.get("id", b"%d"%id(self))
	self.content      = params.get("content", b"")
	self.style        = params.get("style", b"")
	self.class_       = params.get("class_", b"")
	self.text         = params.get("text", b"")
	self.href         = params.get("href", b"")
	self.disabled     = params.get("disabled", False)
	return self

# <ul class="nav nav-pills nav-stacked flex-column %(class_)s" style="%(style)s" id="%(id)s">
# %(content)s
# </ul>
begTagTab = b'''<ul class="nav nav-pills nav-stacked flex-column %s" style="%s" id="%s">'''
endTagTab = b'''</ul>'''
def Tab(*args, **params):
	self = Template(*(("Tab",) + args), **params)

	def getBegin(self):
		global begTagTab
		return begTagTab%(self.class_,self.style,self.id)
	self.getBegin     = getBegin

	def getEnd(self):
		global endTagTab
		return endTagTab
	self.getEnd       = getEnd

	self.content      = params.get("content", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.class_       = params.get("class_", b"")
	return self

# <a class="dropdown-item %(class_)s" style="%(style)s" id="%(id)s" href="%(href)s">%(text)s</a>
begTagDropdownItem = b'''<a class="dropdown-item %s" style="%s" id="%s" href="%s">%s</a>'''
def DropdownItem(*args, **params):
	self = Template(*(("DropdownItem",) + args), **params)

	def getBegin(self):
		global begTagDropdownItem
		return begTagDropdownItem%(self.class_,self.style,self.id,self.href,self.text)
	self.getBegin     = getBegin

	def getEnd(self):
		return b''
	self.getEnd       = getEnd

	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.class_       = params.get("class_", b"")
	self.text         = params.get("text", b"")
	self.href         = params.get("href", b"")
	return self

# <li class="nav-item dropdown">
# <a class="nav-link dropdown-toggle %(class_)s" style="%(style)s" id="%(id)s" data-toggle="dropdown">
# %(text)s
# </a>
# <div class="dropdown-menu">
# %(content)s
# </div>
# </li>
begTagDropdown = b'''<li class="nav-item dropdown"><a class="nav-link dropdown-toggle %s" style="%s" id="%s" data-toggle="dropdown">%s</a><div class="dropdown-menu">'''
endTagDropdown = b'''</div></li>'''
def Dropdown(*args, **params):
	self = Template(*(("Dropdown",) + args), **params)

	def getBegin(self):
		global begTagDropdown
		return begTagDropdown%(self.class_,self.style,self.id,self.text)
	self.getBegin     = getBegin

	def getEnd(self):
		global endTagDropdown
		return endTagDropdown
	self.getEnd       = getEnd

	self.content      = params.get("content", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.class_       = params.get("class_", b"")
	self.text         = params.get("text", b"")
	return self

# <label >%(text)s</label>
# <input list="%(id)s" class="form-control %(class_)s" style="%(style)s" pattern="%(pattern)s" placeholder="%(placeholder)s" value="%(value)s" name="%(name)s" %(disabled)s>
# <datalist id="%(id)s">
# %(content)s
# </datalist>
# <br>
begTagComboBox = b'''<label >%s</label><input list="%s" class="form-control %s" style="%s" pattern="%s" placeholder="%s" value="%s" name="%s" %s><datalist id="%s">'''
endTagComboBox = b'''</datalist><br>'''
def ComboBox(*args, **params):
	self = Template(*(("ComboBox",) + args), **params)

	def getBegin(self):
		global begTagComboBox
		return begTagComboBox%(self.text,self.id,self.class_,self.style,self.pattern,self.placeholder,self.value,self.name, b'disabled' if self.disabled else b'',self.id)
	self.getBegin     = getBegin

	def getEnd(self):
		global endTagComboBox
		return endTagComboBox
	self.getEnd       = getEnd

	self.id           = params.get("id", b"%d"%id(self))
	self.content      = params.get("content", b"")
	self.style        = params.get("style", b"")
	self.class_       = params.get("class_", b"")
	self.text         = params.get("text", b"")
	self.name         = params.get("name", b"%d"%id(self))
	self.value        = params.get("value", b"")
	self.pattern      = params.get("pattern", b"*")
	self.placeholder  = params.get("placeholder", b"")
	self.disabled     = params.get("disabled", False)
	return self

# <img src="%(src)s" class="%(class_)s" style="%(style)s" id="%(id)s" alt="%(alt)s">
begTagImage = b'''<img src="%s" class="%s" style="%s" id="%s" alt="%s">'''
def Image(*args, **params):
	self = Template(*(("Image",) + args), **params)

	def getBegin(self):
		global begTagImage
		return begTagImage%(self.src,self.class_,self.style,self.id,self.alt)
	self.getBegin     = getBegin

	def getEnd(self):
		return b''
	self.getEnd       = getEnd

	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.src          = params.get("src", b"")
	self.alt          = params.get("alt", b"")
	self.class_       = params.get("class_", b"")
	return self

# <div class="alert alert-success alert-dismissible fade show">
# <button type="button" class="close" data-dismiss="alert">&times;</button>
# %(content)s%(text)s
# </div>
begTagAlertSuccess = b'''<div class="alert alert-success alert-dismissible fade show"><button type="button" class="close" data-dismiss="alert">&times;</button>'''
endTagAlertSuccess = b'''%s</div>'''
def AlertSuccess(*args, **params):
	self = Template(*(("AlertSuccess",) + args), **params)

	def getBegin(self):
		global begTagAlertSuccess
		return begTagAlertSuccess
	self.getBegin     = getBegin

	def getEnd(self):
		global endTagAlertSuccess
		return endTagAlertSuccess%(self.text)
	self.getEnd       = getEnd

	self.text         = params.get("text", b"")
	self.content      = params.get("content", b"")
	return self

# <div class="alert alert-warning alert-dismissible fade show">
# <button type="button" class="close" data-dismiss="alert">&times;</button>
# %(content)s%(text)s
# </div>
begTagAlertWarning = b'''<div class="alert alert-warning alert-dismissible fade show"><button type="button" class="close" data-dismiss="alert">&times;</button>'''
endTagAlertWarning = b'''%s</div>'''
def AlertWarning(*args, **params):
	self = Template(*(("AlertWarning",) + args), **params)

	def getBegin(self):
		global begTagAlertWarning
		return begTagAlertWarning
	self.getBegin     = getBegin

	def getEnd(self):
		global endTagAlertWarning
		return endTagAlertWarning%(self.text)
	self.getEnd       = getEnd

	self.text         = params.get("text", b"")
	self.content      = params.get("content", b"")
	return self

# <div class="alert alert-danger alert-dismissible fade show">
# <button type="button" class="close" data-dismiss="alert">&times;</button>
# %(content)s%(text)s
# </div>
begTagAlertError = b'''<div class="alert alert-danger alert-dismissible fade show"><button type="button" class="close" data-dismiss="alert">&times;</button>'''
endTagAlertError = b'''%s</div>'''
def AlertError(*args, **params):
	self = Template(*(("AlertError",) + args), **params)

	def getBegin(self):
		global begTagAlertError
		return begTagAlertError
	self.getBegin     = getBegin

	def getEnd(self):
		global endTagAlertError
		return endTagAlertError%(self.text)
	self.getEnd       = getEnd

	self.text         = params.get("text", b"")
	self.content      = params.get("content", b"")
	return self

# %(content)s
def Tag(*args, **params):
	self = Template(*(("Tag",) + args), **params)

	def getBegin(self):
		return b''
	self.getBegin     = getBegin

	def getEnd(self):
		return b''
	self.getEnd       = getEnd

	self.content      = params.get("content", b"")
	return self

# <button type="button" class="btn btn-outline-primary %(class_)s" style="%(style)s" id="%(id)s" name="%(name)s" %(disabled)s onclick="oncommand_%(id)s()" >%(text)s</button>
# <script type="text/javascript">
# function oncommand_%(id)s() 
# {
# var confirmMessage = "%(confirm)s";
# var execute = true;
# if (confirmMessage != "")
# {
# execute = confirm(confirmMessage);
# }
# if (execute)
# {
# var xhttp = new XMLHttpRequest();
# xhttp.open("GET","%(path)s?name="+document.getElementById("%(id)s").name,true);
# xhttp.send();
# }
# }
# </script>
begTagButtonCmd = b'''<button type="button" class="btn btn-outline-primary %s" style="%s" id="%s" name="%s" %s onclick="oncommand_%s()" >%s</button><script type="text/javascript">function oncommand_%s(){var confirmMessage = "%s";var execute = true;if (confirmMessage != ""){execute = confirm(confirmMessage);}if (execute){var xhttp = new XMLHttpRequest();xhttp.open("GET","%s?name="+document.getElementById("%s").name,true);xhttp.send();}}</script>'''
def ButtonCmd(*args, **params):
	self = Template(*(("ButtonCmd",) + args), **params)

	def getBegin(self):
		global begTagButtonCmd
		return begTagButtonCmd%(self.class_,self.style,self.id,self.name, b'disabled' if self.disabled else b'',self.id,self.text,self.id,self.confirm,self.path,self.id)
	self.getBegin     = getBegin

	def getEnd(self):
		return b''
	self.getEnd       = getEnd

	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.name         = params.get("name", b"%d"%id(self))
	self.class_       = params.get("class_", b"")
	self.text         = params.get("text", b"")
	self.confirm      = params.get("confirm", b"")
	self.path         = params.get("path", b"")
	self.disabled     = params.get("disabled", False)
	return self

# <label >%(text)s</label>
# <div style="display: flex;">
# <input type="range" class="custom-range %(class_)s" style="%(style)s" id="slider_%(id)s" name="%(name)s" min="%(min)s" max="%(max)s" step="%(step)s" value="%(value)s" %(disabled)s oninput="onchange_%(id)s()" onmouseup="oncommand_%(id)s()" />
# <span id="value_%(id)s"/>
# </div>
# <script type="text/javascript">
# function onchange_%(id)s() 
# {
# document.getElementById("value_%(id)s").innerHTML = "&nbsp;" + document.getElementById("slider_%(id)s").value;
# }
# onchange_%(id)s();
# function oncommand_%(id)s() 
# {
# var xhttp = new XMLHttpRequest();
# xhttp.open("GET","%(path)s?name="+document.getElementById("slider_%(id)s").name+"&value="+document.getElementById("slider_%(id)s").value,true);
# xhttp.send();
# }
# </script>
begTagSliderCmd = b'''<label >%s</label><div style="display: flex;"><input type="range" class="custom-range %s" style="%s" id="slider_%s" name="%s" min="%s" max="%s" step="%s" value="%s" %s oninput="onchange_%s()" onmouseup="oncommand_%s()" /><span id="value_%s"/></div><script type="text/javascript">function onchange_%s(){document.getElementById("value_%s").innerHTML = "&nbsp;" + document.getElementById("slider_%s").value;}onchange_%s();function oncommand_%s(){var xhttp = new XMLHttpRequest();xhttp.open("GET","%s?name="+document.getElementById("slider_%s").name+"&value="+document.getElementById("slider_%s").value,true);xhttp.send();}</script>'''
def SliderCmd(*args, **params):
	self = Template(*(("SliderCmd",) + args), **params)

	def getBegin(self):
		global begTagSliderCmd
		return begTagSliderCmd%(self.text,self.class_,self.style,self.id,self.name,self.min,self.max,self.step,self.value, b'disabled' if self.disabled else b'',self.id,self.id,self.id,self.id,self.id,self.id,self.id,self.id,self.path,self.id,self.id)
	self.getBegin     = getBegin

	def getEnd(self):
		return b''
	self.getEnd       = getEnd

	self.max          = params.get("max", b"")
	self.min          = params.get("min", b"")
	self.step         = params.get("step", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.name         = params.get("name", b"%d"%id(self))
	self.text         = params.get("text", b"")
	self.class_       = params.get("class_", b"")
	self.value        = params.get("value", b"")
	self.path         = params.get("path", b"")
	self.disabled     = params.get("disabled", False)
	return self

# <label >%(text)s</label>
# <select class="btn btn-outline-primary custom-select %(class_)s" style="%(style)s" id="%(id)s" name="%(name)s" %(disabled)s oninput="oncommand_%(id)s()">
# %(content)s
# </select>
# <script type="text/javascript">
# function oncommand_%(id)s() 
# {
# var xhttp = new XMLHttpRequest();
# xhttp.open("GET","%(path)s?name="+document.getElementById("%(id)s").name+"&value="+document.getElementById("%(id)s").value,true);
# xhttp.send();
# }
# </script>
begTagComboCmd = b'''<label >%s</label><select class="btn btn-outline-primary custom-select %s" style="%s" id="%s" name="%s" %s oninput="oncommand_%s()">'''
endTagComboCmd = b'''</select><script type="text/javascript">function oncommand_%s(){var xhttp = new XMLHttpRequest();xhttp.open("GET","%s?name="+document.getElementById("%s").name+"&value="+document.getElementById("%s").value,true);xhttp.send();}</script>'''
def ComboCmd(*args, **params):
	self = Template(*(("ComboCmd",) + args), **params)

	def getBegin(self):
		global begTagComboCmd
		return begTagComboCmd%(self.text,self.class_,self.style,self.id,self.name, b'disabled' if self.disabled else b'',self.id)
	self.getBegin     = getBegin

	def getEnd(self):
		global endTagComboCmd
		return endTagComboCmd%(self.id,self.path,self.id,self.id)
	self.getEnd       = getEnd

	self.id           = params.get("id", b"%d"%id(self))
	self.content      = params.get("content", b"")
	self.style        = params.get("style", b"")
	self.name         = params.get("name", b"%d"%id(self))
	self.text         = params.get("text", b"")
	self.class_       = params.get("class_", b"")
	self.path         = params.get("path", b"")
	self.disabled     = params.get("disabled", False)
	return self

# <div class="custom-control custom-switch">
# <input type="checkbox" class="custom-control-input %(class_)s" style="%(style)s" id="%(id)s" value="%(value)s" name="%(name)s" %(checked)s %(disabled)s oninput="oncommand_%(id)s()">
# <label class="custom-control-label" for="%(id)s">%(text)s</label>
# </div>
# <script type="text/javascript">
# function oncommand_%(id)s() 
# {
# var xhttp = new XMLHttpRequest();
# xhttp.open("GET","%(path)s?name="+document.getElementById("%(id)s").name+"&value="+document.getElementById("%(id)s").checked,true);
# xhttp.send();
# }
# </script>
begTagSwitchCmd = b'''<div class="custom-control custom-switch"><input type="checkbox" class="custom-control-input %s" style="%s" id="%s" value="%s" name="%s" %s %s oninput="oncommand_%s()"><label class="custom-control-label" for="%s">%s</label></div><script type="text/javascript">function oncommand_%s(){var xhttp = new XMLHttpRequest();xhttp.open("GET","%s?name="+document.getElementById("%s").name+"&value="+document.getElementById("%s").checked,true);xhttp.send();}</script>'''
def SwitchCmd(*args, **params):
	self = Template(*(("SwitchCmd",) + args), **params)

	def getBegin(self):
		global begTagSwitchCmd
		return begTagSwitchCmd%(self.class_,self.style,self.id,self.value,self.name, b'checked' if self.checked else b'', b'disabled' if self.disabled else b'',self.id,self.id,self.text,self.id,self.path,self.id,self.id)
	self.getBegin     = getBegin

	def getEnd(self):
		return b''
	self.getEnd       = getEnd

	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.name         = params.get("name", b"%d"%id(self))
	self.class_       = params.get("class_", b"")
	self.text         = params.get("text", b"")
	self.value        = params.get("value", b"")
	self.checked      = params.get("checked", True)
	self.path         = params.get("path", b"")
	self.disabled     = params.get("disabled", False)
	return self

# <html lang="fr" charset="utf-8">
# <head>
# <title>%(title)s</title>
# <meta name="viewport" content="" charset="UTF-8"/>
# <link rel="icon" href="data:,">
# </head>
# <body class="%(class_)s" style="%(style)s"> 
# %(content)s
# </body>
# </html>
begTagPage = b'''<html lang="fr" charset="utf-8"><head><title>%s</title><meta name="viewport" content="" charset="UTF-8"/><link rel="icon" href="data:,"></head><body class="%s" style="%s">'''
endTagPage = b'''</body></html>'''
def Page(*args, **params):
	self = Template(*(("Page",) + args), **params)

	def getBegin(self):
		global begTagPage
		return begTagPage%(self.title,self.class_,self.style)
	self.getBegin     = getBegin

	def getEnd(self):
		global endTagPage
		return endTagPage
	self.getEnd       = getEnd

	self.class_       = params.get("class_", b"")
	self.content      = params.get("content", b"")
	self.style        = params.get("style", b"")
	self.title        = params.get("title", b"")
	return self
