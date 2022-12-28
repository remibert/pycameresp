''' File automatically generated with template.html content '''
# pylint:disable=missing-function-docstring
# pylint:disable=global-variable-not-assigned
# pylint:disable=trailing-whitespace
# pylint:disable=too-many-lines
from htmltemplate.template import Template 

# <link  href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
# <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
beg_tagStylesheet = b'''<link  href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet"><script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>'''
def Stylesheet(*args, **params):
	self = Template(*(("Stylesheet",) + args), **params)

	def get_begin(self):
		global beg_tagStylesheet
		return beg_tagStylesheet
	self.get_begin     = get_begin

	def get_end(self):
		return b''
	self.get_end       = get_end

	self.end_init(**params)
	return self

# <link href="/bootstrap.min.css" rel="stylesheet"/>
# <script src="/bootstrap.bundle.min.js"></script>
beg_tagStylesheetDefault = b'''<link href="/bootstrap.min.css" rel="stylesheet"/><script src="/bootstrap.bundle.min.js"></script>'''
def StylesheetDefault(*args, **params):
	self = Template(*(("StylesheetDefault",) + args), **params)

	def get_begin(self):
		global beg_tagStylesheetDefault
		return beg_tagStylesheetDefault
	self.get_begin     = get_begin

	def get_end(self):
		return b''
	self.get_end       = get_end

	self.end_init(**params)
	return self

# <div class="%(class_)s" style="%(style)s" id="%(id)s">
# %(content)s
# </div>
beg_tagDiv = b'''<div class="%s" style="%s" id="%s">'''
end_tagDiv = b'''</div>'''
def Div(*args, **params):
	self = Template(*(("Div",) + args), **params)

	def get_begin(self):
		global beg_tagDiv
		return beg_tagDiv%(self.class_,self.style,self.id)
	self.get_begin     = get_begin

	def get_end(self):
		global end_tagDiv
		return end_tagDiv
	self.get_end       = get_end

	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.content      = params.get("content", b"")
	self.end_init(**params)
	return self

# <h1 class="%(class_)s" style="%(style)s" id="%(id)s">%(text)s</h1>
beg_tagTitle1 = b'''<h1 class="%s" style="%s" id="%s">%s</h1>'''
def Title1(*args, **params):
	self = Template(*(("Title1",) + args), **params)

	def get_begin(self):
		global beg_tagTitle1
		return beg_tagTitle1%(self.class_,self.style,self.id,self.text)
	self.get_begin     = get_begin

	def get_end(self):
		return b''
	self.get_end       = get_end

	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <h2 class="%(class_)s" style="%(style)s" id="%(id)s">%(text)s</h2>
beg_tagTitle2 = b'''<h2 class="%s" style="%s" id="%s">%s</h2>'''
def Title2(*args, **params):
	self = Template(*(("Title2",) + args), **params)

	def get_begin(self):
		global beg_tagTitle2
		return beg_tagTitle2%(self.class_,self.style,self.id,self.text)
	self.get_begin     = get_begin

	def get_end(self):
		return b''
	self.get_end       = get_end

	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <h3 class="%(class_)s" style="%(style)s" id="%(id)s">%(text)s</h3>
beg_tagTitle3 = b'''<h3 class="%s" style="%s" id="%s">%s</h3>'''
def Title3(*args, **params):
	self = Template(*(("Title3",) + args), **params)

	def get_begin(self):
		global beg_tagTitle3
		return beg_tagTitle3%(self.class_,self.style,self.id,self.text)
	self.get_begin     = get_begin

	def get_end(self):
		return b''
	self.get_end       = get_end

	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <h4 class="%(class_)s" style="%(style)s" id="%(id)s">%(text)s</h4>
beg_tagTitle4 = b'''<h4 class="%s" style="%s" id="%s">%s</h4>'''
def Title4(*args, **params):
	self = Template(*(("Title4",) + args), **params)

	def get_begin(self):
		global beg_tagTitle4
		return beg_tagTitle4%(self.class_,self.style,self.id,self.text)
	self.get_begin     = get_begin

	def get_end(self):
		return b''
	self.get_end       = get_end

	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <label class="%(class_)s" style="%(style)s" id="%(id)s">%(text)s</label>
beg_tagLabel = b'''<label class="%s" style="%s" id="%s">%s</label>'''
def Label(*args, **params):
	self = Template(*(("Label",) + args), **params)

	def get_begin(self):
		global beg_tagLabel
		return beg_tagLabel%(self.class_,self.style,self.id,self.text)
	self.get_begin     = get_begin

	def get_end(self):
		return b''
	self.get_end       = get_end

	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <input class="%(class_)s" style="%(style)s" id="%(id)s" pattern="%(pattern)s" placeholder="%(placeholder)s" type="%(type)s" value="%(value)s" name="%(name)s" %(disabled)s %(event)s min="%(min)s" max="%(max)s" %(required)s/>
beg_tagInput = b'''<input class="%s" style="%s" id="%s" pattern="%s" placeholder="%s" type="%s" value="%s" name="%s" %s %s min="%s" max="%s" %s/>'''
def Input(*args, **params):
	self = Template(*(("Input",) + args), **params)

	def get_begin(self):
		global beg_tagInput
		return beg_tagInput%(self.class_,self.style,self.id,self.pattern,self.placeholder,self.type,self.value,self.name, b'disabled' if self.disabled else b'',self.event,self.min,self.max, b'required' if self.required else b'')
	self.get_begin     = get_begin

	def get_end(self):
		return b''
	self.get_end       = get_end

	self.placeholder  = params.get("placeholder", b"")
	self.max          = params.get("max", b"")
	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.name         = params.get("name", b"%d"%id(self))
	self.pattern      = params.get("pattern", b"*")
	self.min          = params.get("min", b"")
	self.type         = params.get("type", b"")
	self.event        = params.get("event", b"")
	self.disabled     = params.get("disabled", False)
	self.required     = params.get("required", False)
	self.value        = params.get("value", b"")
	self.end_init(**params)
	return self

# <div class="form-group %(spacer)s">
# <label for="customRange">%(text)s</label>
# <div style="display: flex;">
# <input type="range" class="form-range %(class_)s" style="%(style)s" id="slider_%(id)s" name="%(name)s" min="%(min)s" max="%(max)s" step="%(step)s" value="%(value)s" %(disabled)s oninput="onchange_%(id)s()" />
# <span id="value_%(id)s"/>
# </div>
# <script type="text/javascript">
# function onchange_%(id)s() 
# {
# document.getElementById("value_%(id)s").innerHTML = "&nbsp;" + document.getElementById("slider_%(id)s").value;
# }
# onchange_%(id)s();
# </script>
# </div>
beg_tagSlider = b'''<div class="form-group %s"><label for="customRange">%s</label><div style="display: flex;"><input type="range" class="form-range %s" style="%s" id="slider_%s" name="%s" min="%s" max="%s" step="%s" value="%s" %s oninput="onchange_%s()" /><span id="value_%s"/></div><script type="text/javascript">function onchange_%s(){document.getElementById("value_%s").innerHTML = "&nbsp;" + document.getElementById("slider_%s").value;}onchange_%s();</script></div>'''
def Slider(*args, **params):
	self = Template(*(("Slider",) + args), **params)

	def get_begin(self):
		global beg_tagSlider
		return beg_tagSlider%(self.spacer,self.text,self.class_,self.style,self.id,self.name,self.min,self.max,self.step,self.value, b'disabled' if self.disabled else b'',self.id,self.id,self.id,self.id,self.id,self.id)
	self.get_begin     = get_begin

	def get_end(self):
		return b''
	self.get_end       = get_end

	self.max          = params.get("max", b"")
	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.name         = params.get("name", b"%d"%id(self))
	self.min          = params.get("min", b"")
	self.disabled     = params.get("disabled", False)
	self.spacer       = params.get("spacer", b"")
	self.step         = params.get("step", b"")
	self.value        = params.get("value", b"")
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <option %(selected)s name="%(name)s" value="%(value)s" %(disabled)s>%(text)s</option>
beg_tagOption = b'''<option %s name="%s" value="%s" %s>%s</option>'''
def Option(*args, **params):
	self = Template(*(("Option",) + args), **params)

	def get_begin(self):
		global beg_tagOption
		return beg_tagOption%( b'selected' if self.selected else b'',self.name,self.value, b'disabled' if self.disabled else b'',self.text)
	self.get_begin     = get_begin

	def get_end(self):
		return b''
	self.get_end       = get_end

	self.name         = params.get("name", b"%d"%id(self))
	self.disabled     = params.get("disabled", False)
	self.selected     = params.get("selected", b"")
	self.value        = params.get("value", b"")
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <div class="form-group %(spacer)s" >
# <select class="form-select %(class_)s" style="%(style)s" id="%(id)s" name="%(name)s" %(disabled)s %(event)s>
# %(content)s
# </select>
# </div>
beg_tagSelect = b'''<div class="form-group %s" ><select class="form-select %s" style="%s" id="%s" name="%s" %s %s>'''
end_tagSelect = b'''</select></div>'''
def Select(*args, **params):
	self = Template(*(("Select",) + args), **params)

	def get_begin(self):
		global beg_tagSelect
		return beg_tagSelect%(self.spacer,self.class_,self.style,self.id,self.name, b'disabled' if self.disabled else b'',self.event)
	self.get_begin     = get_begin

	def get_end(self):
		global end_tagSelect
		return end_tagSelect
	self.get_end       = get_end

	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.name         = params.get("name", b"%d"%id(self))
	self.event        = params.get("event", b"")
	self.disabled     = params.get("disabled", False)
	self.spacer       = params.get("spacer", b"")
	self.content      = params.get("content", b"")
	self.end_init(**params)
	return self

# <div class="form-group %(spacer)s">
# %(content)s
# </div>
beg_tagFormGroup = b'''<div class="form-group %s">'''
end_tagFormGroup = b'''</div>'''
def FormGroup(*args, **params):
	self = Template(*(("FormGroup",) + args), **params)

	def get_begin(self):
		global beg_tagFormGroup
		return beg_tagFormGroup%(self.spacer)
	self.get_begin     = get_begin

	def get_end(self):
		global end_tagFormGroup
		return end_tagFormGroup
	self.get_end       = get_end

	self.content      = params.get("content", b"")
	self.spacer       = params.get("spacer", b"")
	self.end_init(**params)
	return self

# <div class="form-group %(spacer)s">
# <label class="form-check-label">%(text)s</label>
# <input type="%(type)s" class="form-control form-label %(class_)s" style="%(style)s" id="%(id)s" pattern="%(pattern)s" placeholder="%(placeholder)s" type="%(type)s" value="%(value)s" name="%(name)s" step="%(step)s" %(disabled)s %(required)s %(event)s/>
# </div>
beg_tagEdit = b'''<div class="form-group %s"><label class="form-check-label">%s</label><input type="%s" class="form-control form-label %s" style="%s" id="%s" pattern="%s" placeholder="%s" type="%s" value="%s" name="%s" step="%s" %s %s %s/></div>'''
def Edit(*args, **params):
	self = Template(*(("Edit",) + args), **params)

	def get_begin(self):
		global beg_tagEdit
		return beg_tagEdit%(self.spacer,self.text,self.type,self.class_,self.style,self.id,self.pattern,self.placeholder,self.type,self.value,self.name,self.step, b'disabled' if self.disabled else b'', b'required' if self.required else b'',self.event)
	self.get_begin     = get_begin

	def get_end(self):
		return b''
	self.get_end       = get_end

	self.placeholder  = params.get("placeholder", b"")
	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.name         = params.get("name", b"%d"%id(self))
	self.pattern      = params.get("pattern", b"*")
	self.type         = params.get("type", b"")
	self.event        = params.get("event", b"")
	self.disabled     = params.get("disabled", False)
	self.spacer       = params.get("spacer", b"")
	self.step         = params.get("step", b"")
	self.required     = params.get("required", False)
	self.value        = params.get("value", b"")
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <div class="form-check form-switch %(spacer)s">
# <input type="hidden" value="0" name="%(name)s" />
# <input type="checkbox" class="form-check-input %(class_)s" style="%(style)s" id="%(id)s" value="%(value)s" name="%(name)s" %(checked)s %(disabled)s onchange="%(onchange)s" />
# <label class="form-check-label" for="%(id)s">%(text)s</label>
# </div>
beg_tagSwitch = b'''<div class="form-check form-switch %s"><input type="hidden" value="0" name="%s" /><input type="checkbox" class="form-check-input %s" style="%s" id="%s" value="%s" name="%s" %s %s onchange="%s" /><label class="form-check-label" for="%s">%s</label></div>'''
def Switch(*args, **params):
	self = Template(*(("Switch",) + args), **params)

	def get_begin(self):
		global beg_tagSwitch
		return beg_tagSwitch%(self.spacer,self.name,self.class_,self.style,self.id,self.value,self.name, b'checked' if self.checked else b'', b'disabled' if self.disabled else b'',self.onchange,self.id,self.text)
	self.get_begin     = get_begin

	def get_end(self):
		return b''
	self.get_end       = get_end

	self.checked      = params.get("checked", True)
	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.name         = params.get("name", b"%d"%id(self))
	self.disabled     = params.get("disabled", False)
	self.spacer       = params.get("spacer", b"")
	self.onchange     = params.get("onchange", b"")
	self.value        = params.get("value", b"")
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <div class="form-check %(spacer)s">
# <label class="form-check-label">
# <input type="radio" class="form-check-input %(class_)s" style="%(style)s" id="%(id)s" name="%(name)s" %(checked)s %(disabled)s onchange="%(onchange)s">%(text)s</input>
# </label>
# </div>
beg_tagRadio = b'''<div class="form-check %s"><label class="form-check-label"><input type="radio" class="form-check-input %s" style="%s" id="%s" name="%s" %s %s onchange="%s">%s</input></label></div>'''
def Radio(*args, **params):
	self = Template(*(("Radio",) + args), **params)

	def get_begin(self):
		global beg_tagRadio
		return beg_tagRadio%(self.spacer,self.class_,self.style,self.id,self.name, b'checked' if self.checked else b'', b'disabled' if self.disabled else b'',self.onchange,self.text)
	self.get_begin     = get_begin

	def get_end(self):
		return b''
	self.get_end       = get_end

	self.checked      = params.get("checked", True)
	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.name         = params.get("name", b"%d"%id(self))
	self.disabled     = params.get("disabled", False)
	self.spacer       = params.get("spacer", b"")
	self.onchange     = params.get("onchange", b"")
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <div class="form-group %(spacer)s">
# <label >%(text)s</label>
# <input list="%(id)s" class="form-control %(class_)s" style="%(style)s" pattern="%(pattern)s" placeholder="%(placeholder)s" value="%(value)s" name="%(name)s" %(disabled)s>
# <datalist id="%(id)s">
# %(content)s
# </datalist>
# </input>
# </div>
beg_tagComboBox = b'''<div class="form-group %s"><label >%s</label><input list="%s" class="form-control %s" style="%s" pattern="%s" placeholder="%s" value="%s" name="%s" %s><datalist id="%s">'''
end_tagComboBox = b'''</datalist></input></div>'''
def ComboBox(*args, **params):
	self = Template(*(("ComboBox",) + args), **params)

	def get_begin(self):
		global beg_tagComboBox
		return beg_tagComboBox%(self.spacer,self.text,self.id,self.class_,self.style,self.pattern,self.placeholder,self.value,self.name, b'disabled' if self.disabled else b'',self.id)
	self.get_begin     = get_begin

	def get_end(self):
		global end_tagComboBox
		return end_tagComboBox
	self.get_end       = get_end

	self.placeholder  = params.get("placeholder", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.class_       = params.get("class_", b"")
	self.name         = params.get("name", b"%d"%id(self))
	self.pattern      = params.get("pattern", b"*")
	self.disabled     = params.get("disabled", False)
	self.spacer       = params.get("spacer", b"")
	self.content      = params.get("content", b"")
	self.value        = params.get("value", b"")
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <button class="btn btn-outline-primary %(class_)s" style="%(style)s" id="%(id)s" type="%(type)s" name="%(name)s" value="%(value)s" %(disabled)s>%(text)s</button>
beg_tagButton = b'''<button class="btn btn-outline-primary %s" style="%s" id="%s" type="%s" name="%s" value="%s" %s>%s</button>'''
def Button(*args, **params):
	self = Template(*(("Button",) + args), **params)

	def get_begin(self):
		global beg_tagButton
		return beg_tagButton%(self.class_,self.style,self.id,self.type,self.name,self.value, b'disabled' if self.disabled else b'',self.text)
	self.get_begin     = get_begin

	def get_end(self):
		return b''
	self.get_end       = get_end

	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.name         = params.get("name", b"%d"%id(self))
	self.type         = params.get("type", b"")
	self.disabled     = params.get("disabled", False)
	self.value        = params.get("value", b"")
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <input type="file" style="display:none" id="%(id)s" onchange="UploadFile_%(id)s()" name="%(name)s" accept="%(accept)s" %(disabled)s />
# <input type="button" id="label_%(id)s" value="%(text)s" onclick="document.getElementById('%(id)s').click()" class="btn btn-outline-primary " %(disabled)s />
# <script>
# function UploadFile_%(id)s()
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
beg_tagUploadFile = b'''<input type="file" style="display:none" id="%s" onchange="UploadFile_%s()" name="%s" accept="%s" %s /><input type="button" id="label_%s" value="%s" onclick="document.getElementById('%s').click()" class="btn btn-outline-primary " %s /><script>function UploadFile_%s(){let data = document.getElementById('%s').files[0];let entry = document.getElementById('%s').files[0];fetch('%s/' + encodeURIComponent(entry.name), {method:'PUT',body:data});if ("%s" != ""){alert('%s');}document.getElementById('%s').value = "";location.reload();}</script>'''
def UploadFile(*args, **params):
	self = Template(*(("UploadFile",) + args), **params)

	def get_begin(self):
		global beg_tagUploadFile
		return beg_tagUploadFile%(self.id,self.id,self.name,self.accept, b'disabled' if self.disabled else b'',self.id,self.text,self.id, b'disabled' if self.disabled else b'',self.id,self.id,self.id,self.path,self.alert,self.alert,self.id)
	self.get_begin     = get_begin

	def get_end(self):
		return b''
	self.get_end       = get_end

	self.accept       = params.get("accept", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.name         = params.get("name", b"%d"%id(self))
	self.path         = params.get("path", b"")
	self.disabled     = params.get("disabled", False)
	self.alert        = params.get("alert", b"")
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <a href="%(path)s" download="%(filename)s" class="btn btn-outline-primary " name="%(name)s" %(disabled)s>%(text)s</a>
beg_tagDownloadFile = b'''<a href="%s" download="%s" class="btn btn-outline-primary " name="%s" %s>%s</a>'''
def DownloadFile(*args, **params):
	self = Template(*(("DownloadFile",) + args), **params)

	def get_begin(self):
		global beg_tagDownloadFile
		return beg_tagDownloadFile%(self.path,self.filename,self.name, b'disabled' if self.disabled else b'',self.text)
	self.get_begin     = get_begin

	def get_end(self):
		return b''
	self.get_end       = get_end

	self.filename     = params.get("filename", b"")
	self.path         = params.get("path", b"")
	self.name         = params.get("name", b"%d"%id(self))
	self.disabled     = params.get("disabled", False)
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <form class="container %(spacer)s %(class_)s" style="%(style)s" id="%(id)s" method="%(method)s" action="%(action)s" %(novalidate)s>
# %(content)s
# </form>
beg_tagForm = b'''<form class="container %s %s" style="%s" id="%s" method="%s" action="%s" %s>'''
end_tagForm = b'''</form>'''
def Form(*args, **params):
	self = Template(*(("Form",) + args), **params)

	def get_begin(self):
		global beg_tagForm
		return beg_tagForm%(self.spacer,self.class_,self.style,self.id,self.method,self.action, b'novalidate' if self.novalidate else b'')
	self.get_begin     = get_begin

	def get_end(self):
		global end_tagForm
		return end_tagForm
	self.get_end       = get_end

	self.method       = params.get("method", b"")
	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.novalidate   = params.get("novalidate", False)
	self.spacer       = params.get("spacer", b"")
	self.action       = params.get("action", b"")
	self.content      = params.get("content", b"")
	self.end_init(**params)
	return self

# <br/>
beg_tagBr = b'''<br/>'''
def Br(*args, **params):
	self = Template(*(("Br",) + args), **params)

	def get_begin(self):
		global beg_tagBr
		return beg_tagBr
	self.get_begin     = get_begin

	def get_end(self):
		return b''
	self.get_end       = get_end

	self.end_init(**params)
	return self

# <div class="container %(class_)s" style="%(style)s" id="%(id)s">
# %(content)s
# </div>
beg_tagContainer = b'''<div class="container %s" style="%s" id="%s">'''
end_tagContainer = b'''</div>'''
def Container(*args, **params):
	self = Template(*(("Container",) + args), **params)

	def get_begin(self):
		global beg_tagContainer
		return beg_tagContainer%(self.class_,self.style,self.id)
	self.get_begin     = get_begin

	def get_end(self):
		global end_tagContainer
		return end_tagContainer
	self.get_end       = get_end

	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.content      = params.get("content", b"")
	self.end_init(**params)
	return self

# <div class="card-header %(class_)s" style="%(style)s" id="%(id)s">%(text)s %(content)s</div>
beg_tagCardHeader = b'''<div class="card-header %s" style="%s" id="%s">%s '''
end_tagCardHeader = b'''</div>'''
def CardHeader(*args, **params):
	self = Template(*(("CardHeader",) + args), **params)

	def get_begin(self):
		global beg_tagCardHeader
		return beg_tagCardHeader%(self.class_,self.style,self.id,self.text)
	self.get_begin     = get_begin

	def get_end(self):
		global end_tagCardHeader
		return end_tagCardHeader
	self.get_end       = get_end

	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.content      = params.get("content", b"")
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <div class="card-body %(class_)s" style="%(style)s" id="%(id)s">%(content)s</div>
beg_tagCardBody = b'''<div class="card-body %s" style="%s" id="%s">'''
end_tagCardBody = b'''</div>'''
def CardBody(*args, **params):
	self = Template(*(("CardBody",) + args), **params)

	def get_begin(self):
		global beg_tagCardBody
		return beg_tagCardBody%(self.class_,self.style,self.id)
	self.get_begin     = get_begin

	def get_end(self):
		global end_tagCardBody
		return end_tagCardBody
	self.get_end       = get_end

	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.content      = params.get("content", b"")
	self.end_init(**params)
	return self

# <div class="card %(spacer)s" style="%(style)s" id="%(id)s">
# %(content)s
# </div>
beg_tagCard = b'''<div class="card %s" style="%s" id="%s">'''
end_tagCard = b'''</div>'''
def Card(*args, **params):
	self = Template(*(("Card",) + args), **params)

	def get_begin(self):
		global beg_tagCard
		return beg_tagCard%(self.spacer,self.style,self.id)
	self.get_begin     = get_begin

	def get_end(self):
		global end_tagCard
		return end_tagCard
	self.get_end       = get_end

	self.id           = params.get("id", b"%d"%id(self))
	self.style        = params.get("style", b"")
	self.content      = params.get("content", b"")
	self.spacer       = params.get("spacer", b"")
	self.end_init(**params)
	return self

# <p class="%(class_)s" style="%(style)s" id="%(id)s">%(content)s%(text)s</p>
beg_tagParagraph = b'''<p class="%s" style="%s" id="%s">'''
end_tagParagraph = b'''%s</p>'''
def Paragraph(*args, **params):
	self = Template(*(("Paragraph",) + args), **params)

	def get_begin(self):
		global beg_tagParagraph
		return beg_tagParagraph%(self.class_,self.style,self.id)
	self.get_begin     = get_begin

	def get_end(self):
		global end_tagParagraph
		return end_tagParagraph%(self.text)
	self.get_end       = get_end

	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.content      = params.get("content", b"")
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <li class="list-group-item %(class_)s" style="%(style)s" id="%(id)s">%(content)s%(text)s</li>
beg_tagListItem = b'''<li class="list-group-item %s" style="%s" id="%s">'''
end_tagListItem = b'''%s</li>'''
def ListItem(*args, **params):
	self = Template(*(("ListItem",) + args), **params)

	def get_begin(self):
		global beg_tagListItem
		return beg_tagListItem%(self.class_,self.style,self.id)
	self.get_begin     = get_begin

	def get_end(self):
		global end_tagListItem
		return end_tagListItem%(self.text)
	self.get_end       = get_end

	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.content      = params.get("content", b"")
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <button class="btn %(class_)s" style="%(style)s" id="%(id)s">%(content)s%(text)s</button><br>
beg_tagButtonItem = b'''<button class="btn %s" style="%s" id="%s">'''
end_tagButtonItem = b'''%s</button><br>'''
def ButtonItem(*args, **params):
	self = Template(*(("ButtonItem",) + args), **params)

	def get_begin(self):
		global beg_tagButtonItem
		return beg_tagButtonItem%(self.class_,self.style,self.id)
	self.get_begin     = get_begin

	def get_end(self):
		global end_tagButtonItem
		return end_tagButtonItem%(self.text)
	self.get_end       = get_end

	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.content      = params.get("content", b"")
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <ul class="list-group %(class_)s" style="%(style)s" id="%(id)s">
# %(content)s
# </ul>
beg_tagList = b'''<ul class="list-group %s" style="%s" id="%s">'''
end_tagList = b'''</ul>'''
def List(*args, **params):
	self = Template(*(("List",) + args), **params)

	def get_begin(self):
		global beg_tagList
		return beg_tagList%(self.class_,self.style,self.id)
	self.get_begin     = get_begin

	def get_end(self):
		global end_tagList
		return end_tagList
	self.get_end       = get_end

	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.content      = params.get("content", b"")
	self.end_init(**params)
	return self

# <button class="btn btn-outline-primary %(class_)s" style="%(style)s" id="%(id)s" type="submit" name="%(name)s" value="%(value)s" onclick="%(onclick)s">%(content)s%(text)s</button>
beg_tagSubmit = b'''<button class="btn btn-outline-primary %s" style="%s" id="%s" type="submit" name="%s" value="%s" onclick="%s">'''
end_tagSubmit = b'''%s</button>'''
def Submit(*args, **params):
	self = Template(*(("Submit",) + args), **params)

	def get_begin(self):
		global beg_tagSubmit
		return beg_tagSubmit%(self.class_,self.style,self.id,self.name,self.value,self.onclick)
	self.get_begin     = get_begin

	def get_end(self):
		global end_tagSubmit
		return end_tagSubmit%(self.text)
	self.get_end       = get_end

	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.name         = params.get("name", b"%d"%id(self))
	self.onclick      = params.get("onclick", b"")
	self.content      = params.get("content", b"")
	self.value        = params.get("value", b"")
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <a class="btn btn-outline-primary %(class_)s" style="%(style)s" id="%(id)s" href="%(href)s">%(content)s%(text)s</a>
beg_tagCancel = b'''<a class="btn btn-outline-primary %s" style="%s" id="%s" href="%s">'''
end_tagCancel = b'''%s</a>'''
def Cancel(*args, **params):
	self = Template(*(("Cancel",) + args), **params)

	def get_begin(self):
		global beg_tagCancel
		return beg_tagCancel%(self.class_,self.style,self.id,self.href)
	self.get_begin     = get_begin

	def get_end(self):
		global end_tagCancel
		return end_tagCancel%(self.text)
	self.get_end       = get_end

	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.href         = params.get("href", b"")
	self.content      = params.get("content", b"")
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <a class="%(class_)s" style="%(style)s" id="%(id)s" href="%(href)s" onclick="%(onclick)s">%(content)s%(text)s</a>
beg_tagLink = b'''<a class="%s" style="%s" id="%s" href="%s" onclick="%s">'''
end_tagLink = b'''%s</a>'''
def Link(*args, **params):
	self = Template(*(("Link",) + args), **params)

	def get_begin(self):
		global beg_tagLink
		return beg_tagLink%(self.class_,self.style,self.id,self.href,self.onclick)
	self.get_begin     = get_begin

	def get_end(self):
		global end_tagLink
		return end_tagLink%(self.text)
	self.get_end       = get_end

	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.href         = params.get("href", b"")
	self.onclick      = params.get("onclick", b"")
	self.content      = params.get("content", b"")
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <li>
# <a class="dropdown-item %(active)s %(class_)s" style="%(style)s" id="%(id)s" href="%(href)s" %(disabled)s>%(text)s</a>
# </li>
beg_tagMenuItem = b'''<li><a class="dropdown-item %s %s" style="%s" id="%s" href="%s" %s>%s</a></li>'''
def MenuItem(*args, **params):
	self = Template(*(("MenuItem",) + args), **params)

	def get_begin(self):
		global beg_tagMenuItem
		return beg_tagMenuItem%( b'active' if self.active else b'',self.class_,self.style,self.id,self.href, b'disabled' if self.disabled else b'',self.text)
	self.get_begin     = get_begin

	def get_end(self):
		return b''
	self.get_end       = get_end

	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.href         = params.get("href", b"")
	self.active       = params.get("active", False)
	self.disabled     = params.get("disabled", False)
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <li class="nav-item dropdown">
# <a class="nav-link dropdown-toggle" href="#" id="dropdown10" data-bs-toggle="dropdown" aria-expanded=" false" %(disabled)s>%(text)s</a>
# <ul class="dropdown-menu " aria-labelledby="dropdown10">
# %(content)s
# </ul>
# </li>
beg_tagMenu = b'''<li class="nav-item dropdown"><a class="nav-link dropdown-toggle" href="#" id="dropdown10" data-bs-toggle="dropdown" aria-expanded=" false" %s>%s</a><ul class="dropdown-menu " aria-labelledby="dropdown10">'''
end_tagMenu = b'''</ul></li>'''
def Menu(*args, **params):
	self = Template(*(("Menu",) + args), **params)

	def get_begin(self):
		global beg_tagMenu
		return beg_tagMenu%( b'disabled' if self.disabled else b'',self.text)
	self.get_begin     = get_begin

	def get_end(self):
		global end_tagMenu
		return end_tagMenu
	self.get_end       = get_end

	self.content      = params.get("content", b"")
	self.disabled     = params.get("disabled", False)
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <nav class="navbar navbar-expand-lg fixed-top navbar-light bg-light " style="%(style)s">
# <div class="container-fluid">
# <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarCollapse" aria-controls="navbarCollapse" aria-expanded="false" aria-label="Toggle navigation">
# <span class="navbar-toggler-icon"></span>
# </button>
# <div class="collapse navbar-collapse" id="navbarCollapse">
# <ul class="navbar-nav me-auto mb-2 mb-md-0">
# %(content)s
# </ul>
# </div>
# </div>
# </nav>
beg_tagMenuBar = b'''<nav class="navbar navbar-expand-lg fixed-top navbar-light bg-light " style="%s"><div class="container-fluid"><button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarCollapse" aria-controls="navbarCollapse" aria-expanded="false" aria-label="Toggle navigation"><span class="navbar-toggler-icon"></span></button><div class="collapse navbar-collapse" id="navbarCollapse"><ul class="navbar-nav me-auto mb-2 mb-md-0">'''
end_tagMenuBar = b'''</ul></div></div></nav>'''
def MenuBar(*args, **params):
	self = Template(*(("MenuBar",) + args), **params)

	def get_begin(self):
		global beg_tagMenuBar
		return beg_tagMenuBar%(self.style)
	self.get_begin     = get_begin

	def get_end(self):
		global end_tagMenuBar
		return end_tagMenuBar
	self.get_end       = get_end

	self.style        = params.get("style", b"")
	self.content      = params.get("content", b"")
	self.end_init(**params)
	return self

# <img src="%(src)s" class="%(class_)s" style="%(style)s" id="%(id)s" alt="%(alt)s">
beg_tagImage = b'''<img src="%s" class="%s" style="%s" id="%s" alt="%s">'''
def Image(*args, **params):
	self = Template(*(("Image",) + args), **params)

	def get_begin(self):
		global beg_tagImage
		return beg_tagImage%(self.src,self.class_,self.style,self.id,self.alt)
	self.get_begin     = get_begin

	def get_end(self):
		return b''
	self.get_end       = get_end

	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.src          = params.get("src", b"")
	self.alt          = params.get("alt", b"")
	self.end_init(**params)
	return self

# <div class="alert alert-success alert-dismissible fade show">
# <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
# %(content)s%(text)s
# </div>
beg_tagAlertSuccess = b'''<div class="alert alert-success alert-dismissible fade show"><button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>'''
end_tagAlertSuccess = b'''%s</div>'''
def AlertSuccess(*args, **params):
	self = Template(*(("AlertSuccess",) + args), **params)

	def get_begin(self):
		global beg_tagAlertSuccess
		return beg_tagAlertSuccess
	self.get_begin     = get_begin

	def get_end(self):
		global end_tagAlertSuccess
		return end_tagAlertSuccess%(self.text)
	self.get_end       = get_end

	self.content      = params.get("content", b"")
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <div class="alert alert-warning alert-dismissible fade show">
# <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
# %(content)s%(text)s
# </div>
beg_tagAlertWarning = b'''<div class="alert alert-warning alert-dismissible fade show"><button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>'''
end_tagAlertWarning = b'''%s</div>'''
def AlertWarning(*args, **params):
	self = Template(*(("AlertWarning",) + args), **params)

	def get_begin(self):
		global beg_tagAlertWarning
		return beg_tagAlertWarning
	self.get_begin     = get_begin

	def get_end(self):
		global end_tagAlertWarning
		return end_tagAlertWarning%(self.text)
	self.get_end       = get_end

	self.content      = params.get("content", b"")
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <div class="alert alert-danger alert-dismissible fade show">
# <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
# %(content)s%(text)s
# </div>
beg_tagAlertError = b'''<div class="alert alert-danger alert-dismissible fade show"><button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>'''
end_tagAlertError = b'''%s</div>'''
def AlertError(*args, **params):
	self = Template(*(("AlertError",) + args), **params)

	def get_begin(self):
		global beg_tagAlertError
		return beg_tagAlertError
	self.get_begin     = get_begin

	def get_end(self):
		global end_tagAlertError
		return end_tagAlertError%(self.text)
	self.get_end       = get_end

	self.content      = params.get("content", b"")
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# %(content)s
def Tag(*args, **params):
	self = Template(*(("Tag",) + args), **params)

	def get_begin(self):
		return b''
	self.get_begin     = get_begin

	def get_end(self):
		return b''
	self.get_end       = get_end

	self.content      = params.get("content", b"")
	self.end_init(**params)
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
beg_tagButtonCmd = b'''<button type="button" class="btn btn-outline-primary %s" style="%s" id="%s" name="%s" %s onclick="oncommand_%s()" >%s</button><script type="text/javascript">function oncommand_%s(){var confirmMessage = "%s";var execute = true;if (confirmMessage != ""){execute = confirm(confirmMessage);}if (execute){var xhttp = new XMLHttpRequest();xhttp.open("GET","%s?name="+document.getElementById("%s").name,true);xhttp.send();}}</script>'''
def ButtonCmd(*args, **params):
	self = Template(*(("ButtonCmd",) + args), **params)

	def get_begin(self):
		global beg_tagButtonCmd
		return beg_tagButtonCmd%(self.class_,self.style,self.id,self.name, b'disabled' if self.disabled else b'',self.id,self.text,self.id,self.confirm,self.path,self.id)
	self.get_begin     = get_begin

	def get_end(self):
		return b''
	self.get_end       = get_end

	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.name         = params.get("name", b"%d"%id(self))
	self.path         = params.get("path", b"")
	self.disabled     = params.get("disabled", False)
	self.confirm      = params.get("confirm", b"")
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <div class="form-group %(spacer)s">
# <label >%(text)s</label>
# <div style="display: flex;">
# <input type="range" class="form-range %(class_)s" style="%(style)s" id="slider_%(id)s" name="%(name)s" min="%(min)s" max="%(max)s" step="%(step)s" value="%(value)s" %(disabled)s oninput="onchange_%(id)s()" onmouseup="oncommand_%(id)s()" />
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
# </div>
beg_tagSliderCmd = b'''<div class="form-group %s"><label >%s</label><div style="display: flex;"><input type="range" class="form-range %s" style="%s" id="slider_%s" name="%s" min="%s" max="%s" step="%s" value="%s" %s oninput="onchange_%s()" onmouseup="oncommand_%s()" /><span id="value_%s"/></div><script type="text/javascript">function onchange_%s(){document.getElementById("value_%s").innerHTML = "&nbsp;" + document.getElementById("slider_%s").value;}onchange_%s();function oncommand_%s(){var xhttp = new XMLHttpRequest();xhttp.open("GET","%s?name="+document.getElementById("slider_%s").name+"&value="+document.getElementById("slider_%s").value,true);xhttp.send();}</script></div>'''
def SliderCmd(*args, **params):
	self = Template(*(("SliderCmd",) + args), **params)

	def get_begin(self):
		global beg_tagSliderCmd
		return beg_tagSliderCmd%(self.spacer,self.text,self.class_,self.style,self.id,self.name,self.min,self.max,self.step,self.value, b'disabled' if self.disabled else b'',self.id,self.id,self.id,self.id,self.id,self.id,self.id,self.id,self.path,self.id,self.id)
	self.get_begin     = get_begin

	def get_end(self):
		return b''
	self.get_end       = get_end

	self.max          = params.get("max", b"")
	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.name         = params.get("name", b"%d"%id(self))
	self.path         = params.get("path", b"")
	self.min          = params.get("min", b"")
	self.disabled     = params.get("disabled", False)
	self.spacer       = params.get("spacer", b"")
	self.step         = params.get("step", b"")
	self.value        = params.get("value", b"")
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <div class="form-group %(spacer)s">
# <label >%(text)s</label>
# <select class="btn btn-outline-primary form-select %(class_)s" style="%(style)s" id="%(id)s" name="%(name)s" %(disabled)s oninput="oncommand_%(id)s()">
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
# </div>
beg_tagComboCmd = b'''<div class="form-group %s"><label >%s</label><select class="btn btn-outline-primary form-select %s" style="%s" id="%s" name="%s" %s oninput="oncommand_%s()">'''
end_tagComboCmd = b'''</select><script type="text/javascript">function oncommand_%s(){var xhttp = new XMLHttpRequest();xhttp.open("GET","%s?name="+document.getElementById("%s").name+"&value="+document.getElementById("%s").value,true);xhttp.send();}</script></div>'''
def ComboCmd(*args, **params):
	self = Template(*(("ComboCmd",) + args), **params)

	def get_begin(self):
		global beg_tagComboCmd
		return beg_tagComboCmd%(self.spacer,self.text,self.class_,self.style,self.id,self.name, b'disabled' if self.disabled else b'',self.id)
	self.get_begin     = get_begin

	def get_end(self):
		global end_tagComboCmd
		return end_tagComboCmd%(self.id,self.path,self.id,self.id)
	self.get_end       = get_end

	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.name         = params.get("name", b"%d"%id(self))
	self.path         = params.get("path", b"")
	self.disabled     = params.get("disabled", False)
	self.spacer       = params.get("spacer", b"")
	self.content      = params.get("content", b"")
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <div class="form-group %(spacer)s">
# <div class="form-check form-switch" style="height: 1.5em;">
# <input type="checkbox" class="form-check-input %(class_)s" style="%(style)s" id="%(id)s" value="%(value)s" name="%(name)s" %(checked)s %(disabled)s oninput="oncommand_%(id)s()" />
# <label class="form-check-label" for="%(id)s">%(text)s</label>
# </div>
# <script type="text/javascript">
# function oncommand_%(id)s() 
# {
# var xhttp = new XMLHttpRequest();
# xhttp.open("GET","%(path)s?name="+document.getElementById("%(id)s").name+"&value="+document.getElementById("%(id)s").checked,true);
# xhttp.send();
# }
# </script>
# </div>
beg_tagSwitchCmd = b'''<div class="form-group %s"><div class="form-check form-switch" style="height: 1.5em;"><input type="checkbox" class="form-check-input %s" style="%s" id="%s" value="%s" name="%s" %s %s oninput="oncommand_%s()" /><label class="form-check-label" for="%s">%s</label></div><script type="text/javascript">function oncommand_%s(){var xhttp = new XMLHttpRequest();xhttp.open("GET","%s?name="+document.getElementById("%s").name+"&value="+document.getElementById("%s").checked,true);xhttp.send();}</script></div>'''
def SwitchCmd(*args, **params):
	self = Template(*(("SwitchCmd",) + args), **params)

	def get_begin(self):
		global beg_tagSwitchCmd
		return beg_tagSwitchCmd%(self.spacer,self.class_,self.style,self.id,self.value,self.name, b'checked' if self.checked else b'', b'disabled' if self.disabled else b'',self.id,self.id,self.text,self.id,self.path,self.id,self.id)
	self.get_begin     = get_begin

	def get_end(self):
		return b''
	self.get_end       = get_end

	self.checked      = params.get("checked", True)
	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.name         = params.get("name", b"%d"%id(self))
	self.path         = params.get("path", b"")
	self.disabled     = params.get("disabled", False)
	self.spacer       = params.get("spacer", b"")
	self.value        = params.get("value", b"")
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <main class="form-signin">
# <div class="modal-dialog modal-dialog-centered %(class_)s" style="align-items:center;min-height:100vh; %(style)s" id="%(id)s">
# <div class="modal-content shadow-lg p-3 mb-5 bg-white rounded">
# <div class="modal-body" style="padding:10px 10px;">
# %(content)s
# </div>
# </div>
# </div>
# </main>
beg_tagModal = b'''<main class="form-signin"><div class="modal-dialog modal-dialog-centered %s" style="align-items:center;min-height:100vh; %s" id="%s"><div class="modal-content shadow-lg p-3 mb-5 bg-white rounded"><div class="modal-body" style="padding:10px 10px;">'''
end_tagModal = b'''</div></div></div></main>'''
def Modal(*args, **params):
	self = Template(*(("Modal",) + args), **params)

	def get_begin(self):
		global beg_tagModal
		return beg_tagModal%(self.class_,self.style,self.id)
	self.get_begin     = get_begin

	def get_end(self):
		global end_tagModal
		return end_tagModal
	self.get_end       = get_end

	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.content      = params.get("content", b"")
	self.end_init(**params)
	return self

# <span class="%(class_)s" style="%(style)s" id="%(id)s">&nbsp;</span>
beg_tagSpace = b'''<span class="%s" style="%s" id="%s">&nbsp;</span>'''
def Space(*args, **params):
	self = Template(*(("Space",) + args), **params)

	def get_begin(self):
		global beg_tagSpace
		return beg_tagSpace%(self.class_,self.style,self.id)
	self.get_begin     = get_begin

	def get_end(self):
		return b''
	self.get_end       = get_end

	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.end_init(**params)
	return self

# <li class="page-item"><a class="page-link %(active)s %(class_)s" style="%(style)s" id="%(id)s" href="%(href)s" %(disabled)s>%(text)s</a></li>
beg_tagPageItem = b'''<li class="page-item"><a class="page-link %s %s" style="%s" id="%s" href="%s" %s>%s</a></li>'''
def PageItem(*args, **params):
	self = Template(*(("PageItem",) + args), **params)

	def get_begin(self):
		global beg_tagPageItem
		return beg_tagPageItem%( b'active' if self.active else b'',self.class_,self.style,self.id,self.href, b'disabled' if self.disabled else b'',self.text)
	self.get_begin     = get_begin

	def get_end(self):
		return b''
	self.get_end       = get_end

	self.class_       = params.get("class_", b"")
	self.style        = params.get("style", b"")
	self.id           = params.get("id", b"%d"%id(self))
	self.href         = params.get("href", b"")
	self.active       = params.get("active", False)
	self.disabled     = params.get("disabled", False)
	self.text         = params.get("text", b"")
	self.end_init(**params)
	return self

# <ul class="pagination" id="%(id)s" class="%(class_)s">
# %(content)s
# </ul>
beg_tagPagination = b'''<ul class="pagination" id="%s" class="%s">'''
end_tagPagination = b'''</ul>'''
def Pagination(*args, **params):
	self = Template(*(("Pagination",) + args), **params)

	def get_begin(self):
		global beg_tagPagination
		return beg_tagPagination%(self.id,self.class_)
	self.get_begin     = get_begin

	def get_end(self):
		global end_tagPagination
		return end_tagPagination
	self.get_end       = get_end

	self.id           = params.get("id", b"%d"%id(self))
	self.content      = params.get("content", b"")
	self.class_       = params.get("class_", b"")
	self.end_init(**params)
	return self

# <html lang="fr" charset="utf-8">
# <head>
# <title>%(title)s</title>
# <meta name="viewport" content="width=device-width, initial-scale=1" charset="UTF-8"/>
# <link rel="icon" href="data:,">
# </head>
# <body class="%(class_)s" style="%(style)s"> 
# %(content)s
# </body>
# </html>
beg_tagPage = b'''<html lang="fr" charset="utf-8"><head><title>%s</title><meta name="viewport" content="width=device-width, initial-scale=1" charset="UTF-8"/><link rel="icon" href="data:,"></head><body class="%s" style="%s">'''
end_tagPage = b'''</body></html>'''
def Page(*args, **params):
	self = Template(*(("Page",) + args), **params)

	def get_begin(self):
		global beg_tagPage
		return beg_tagPage%(self.title,self.class_,self.style)
	self.get_begin     = get_begin

	def get_end(self):
		global end_tagPage
		return end_tagPage
	self.get_end       = get_end

	self.class_       = params.get("class_", b"")
	self.title        = params.get("title", b"")
	self.style        = params.get("style", b"")
	self.content      = params.get("content", b"")
	self.end_init(**params)
	return self
