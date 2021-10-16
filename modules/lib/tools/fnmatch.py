"""  Unix filename pattern matching.
Extracted from cpython fnmatch.py """
import re

previous_pat = [None, None]
def fnmatch(name, pat):
	""" Compare filenames """
	if pat == "*":
		return True
	elif pat == "*.*":
		if name.find(".") != -1:
			return True
		else:
			return False
	else:
		global previous_pat
		if previous_pat[0] == pat:
			res = previous_pat[1]
		else:
			res = translate(pat)
			previous_pat =[pat, res]
		return re.compile(res).match(name) is not None

def escape(pattern):
	""" Manage escape in pattern """
	result = ""
	for char in pattern:
		if char in '()[]{}?*+-|^$\\.&~# \t\n\r\v\f':
			result += "\\"
		result += char
	return result

def translate(pat):
	""" Translate pattern """
	i, n = 0, len(pat)
	res = ''
	while i < n:
		c = pat[i]
		i = i+1
		if c == '*':
			res = res + '.*'
		elif c == '?':
			res = res + '.'
		elif c == '[':
			j = i
			if j < n and pat[j] == '!':
				j = j+1
			if j < n and pat[j] == ']':
				j = j+1
			while j < n and pat[j] != ']':
				j = j+1
			if j >= n:
				res = res + '\\['
			else:
				stuff = pat[i:j]
				if '--' not in stuff:
					stuff = stuff.replace('\\', r'\\')
				else:
					chunks = []
					k = i+2 if pat[i] == '!' else i+1
					while True:
						k = pat.find('-', k, j)
						if k < 0:
							break
						chunks.append(pat[i:k])
						i = k+1
						k = k+3
					chunks.append(pat[i:j])
					# Escape backslashes and hyphens for set difference (--).
					# Hyphens that create ranges shouldn't be escaped.
					stuff = '-'.join(s.replace('\\', r'\\').replace('-', r'\-')
									 for s in chunks)
				# Escape set operations (&&, ~~ and ||).
				stuff = re.sub(r'([&~|])', r'\\\1', stuff)
				i = j+1
				if stuff[0] == '!':
					stuff = '^' + stuff[1:]
				elif stuff[0] in ('^', '['):
					stuff = '\\' + stuff
				res = '%s[%s]' % (res, stuff)
		else:
			res = res + escape(c)
	return r'^%s$' % res
