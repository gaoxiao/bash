import gscommon as gs, margo, gsq
import sublime, sublime_plugin
import os, re

DOMAIN = 'GsDoc'

GOOS_PAT = re.compile(r'_(%s)' % '|'.join(gs.GOOSES))
GOARCH_PAT = re.compile(r'_(%s)' % '|'.join(gs.GOARCHES))
PKGFILE_EXTENSIONS = ['go', 'goc', 'c', 'h', 'cc', 'hh', 'hpp', 'asm', 'cpp', 's', 'i']

class GsDocCommand(sublime_plugin.TextCommand):
	def is_enabled(self):
		return gs.is_go_source_view(self.view)

	def show_output(self, s):
		gs.show_output(DOMAIN+'-output', s, False, 'GsDoc')

	def run(self, _, mode=''):
		view = self.view
		if (not gs.is_go_source_view(view)) or (mode not in ['goto', 'hint']):
			return

		pt = view.sel()[0].begin()
		src = view.substr(sublime.Region(0, view.size()))
		def f(docs, err):
			doc = ''
			if err:
				self.show_output('// Error: %s' % err)
			elif docs:
				if mode == "goto":
					fn = ''
					flags = 0
					if len(docs) > 0:
						d = docs[0]
						fn = d.get('fn', '')
						row = d.get('row', 0)
						col = d.get('col', 0)
						if fn:
							gs.println('opening %s:%s:%s' % (fn, row, col))
							gs.focus(fn, row, col)
							return
					self.show_output("%s: cannot find definition" % DOMAIN)
				elif mode == "hint":
					s = []
					for d in docs:
						name = d.get('name', '')
						if name:
							kind = d.get('kind', '')
							pkg = d.get('pkg', '')
							if pkg:
								name = '%s.%s' % (pkg, name)
							src = d.get('src', '')
							if src:
								src = '\n//\n%s' % src
							doc = '// %s %s%s' % (name, kind, src)

						s.append(doc)
					doc = '\n\n\n'.join(s).strip()
			self.show_output(doc or "// %s: no docs found" % DOMAIN)

		margo.call(
			path='/doc',
			args={
				'fn': view.file_name(),
				'src': src,
				'offset': pt,
			},
			default=[],
			cb=f,
			message='fetching docs'
		)


class GsBrowseDeclarationsCommand(sublime_plugin.WindowCommand):
	def run(self, dir=''):
		if dir == '.':
			self.present_current()
		elif dir:
			self.present('', '', dir)
		else:
			def f(res, err):
				if err:
					gs.notice(DOMAIN, err)
					return

				ents, m = handle_pkgdirs_res(res)
				if ents:
					ents.insert(0, "Current Package")

					def cb(i, win):
						if i == 0:
							self.present_current()
						elif i >= 1:
							self.present('', '', os.path.dirname(m[ents[i]]))

					gs.show_quick_panel(ents, cb)
				else:
					gs.show_quick_panel([['', 'No source directories found']])

			margo.call(
				path='/pkgdirs',
				args={},
				default={},
				cb=f,
				message='fetching pkg dirs'
			)

	def present_current(self):
		pkg_dir = ''
		view = gs.active_valid_go_view(win=self.window, strict=False)
		if view:
			if view.file_name():
				pkg_dir = os.path.dirname(view.file_name())
			vfn = gs.view_fn(view)
			src = gs.view_src(view)
		else:
			vfn = ''
			src = ''
		self.present(vfn, src, pkg_dir)

	def present(self, vfn, src, pkg_dir):
		win = self.window
		if win is None:
			return

		def f(res, err):
			if err:
				gs.notice(DOMAIN, err)
				return

			decls = res.get('file_decls', [])
			for d in res.get('pkg_decls', []):
				if not vfn or d['fn'] != vfn:
					decls.append(d)

			for d in decls:
				dname = (d['repr'] or d['name'])
				trailer = []
				trailer.extend(GOOS_PAT.findall(d['fn']))
				trailer.extend(GOARCH_PAT.findall(d['fn']))
				if trailer:
					trailer = ' (%s)' % ', '.join(trailer)
				else:
					trailer = ''
				d['ent'] = '%s %s%s' % (d['kind'], dname, trailer)

			ents = []
			decls.sort(key=lambda d: d['ent'])
			for d in decls:
				ents.append(d['ent'])

			def cb(i):
				if i >= 0:
					d = decls[i]
					gs.focus(d['fn'], d['row'], d['col'], win)

			if ents:
				win.show_quick_panel(ents, cb)
			else:
				win.show_quick_panel([['', 'No declarations found']], lambda x: None)

		margo.call(
			path='/declarations',
			args={
				'fn': vfn,
				'src': src,
				'pkg_dir': pkg_dir,
			},
			default={},
			cb=f,
			message='fetching pkg declarations'
		)

def handle_pkgdirs_res(res):
	m = {}
	for root, dirs in res.iteritems():
		for dir, fn in dirs.iteritems():
			if not m.get(dir):
				m[dir] = fn
	ents = m.keys()
	ents.sort(key = lambda a: a.lower())
	return (ents, m)

class GsBrowsePackagesCommand(sublime_plugin.WindowCommand):
	def run(self):
		def f(res, err):
			if err:
				gs.notice(DOMAIN, err)
				return

			ents, m = handle_pkgdirs_res(res)
			if ents:
				def cb(i, win):
					if i >= 0:
						dirname = gs.basedir_or_cwd(m[ents[i]])
						win.run_command('gs_browse_files', {'dir': dirname})
				gs.show_quick_panel(ents, cb)
			else:
				gs.show_quick_panel([['', 'No source directories found']])

		margo.call(
			path='/pkgdirs',
			args={},
			default={},
			cb=f,
			message='fetching pkg dirs'
		)

def show_pkgfiles(dirname):
	dirname = os.path.abspath(dirname)
	ents = []
	m = {}

	for fn in gs.list_dir_tree(dirname, PKGFILE_EXTENSIONS):
		name = os.path.relpath(fn, dirname).replace('\\', '/')
		m[name] = fn
		ents.append(name)
	ents.sort(key = lambda a: a.lower())

	if ents:
		def cb(i, win):
			if i >= 0:
				gs.focus(m[ents[i]], 0, 0, win)
		gs.show_quick_panel(ents, cb)
	else:
		gs.show_quick_panel([['', 'No files found']])

class GsBrowseFilesCommand(sublime_plugin.WindowCommand):
	def run(self, dir=''):
		if not dir:
			view = self.window.active_view()
			dir = gs.basedir_or_cwd(view.file_name() if view is not None else None)
		gsq.dispatch('*', lambda: show_pkgfiles(dir), 'scanning directory for package files')


