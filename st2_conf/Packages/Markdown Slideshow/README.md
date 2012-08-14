Markdown Slideshow
==================

A Sublime Text 2 plugin for slideshow in your web browser from markdown file.

Is a [Base example](http://ogom.github.com/sublimetext-markdown-slideshow/examples/base.html).

---

### Installation
#### Package Control
The easy to install using the [Package Control](http://wbond.net/sublime_packages/package_control).

1. Press `ctrl+shift+p` (Windows) or `cmd+shift+p` (OS X). then `Package Control: Install Package`.
2. To install at the command of `Markdown Slideshow`.


#### Github
Download is available from github, Install the folder of Sublime Text 2 Packages.

    $ git clone git://github.com/ogom/sublimetext-markdown-slideshow.git

---

#### Sample Key Bindings
Let's add key bindings - user.

    [
      { 
        "keys": ["alt+s"], "command": "markdown_slideshow",
        "args": {
          "theme": "default",
          "save": true,
          "path": "/tmp"
        }
      }
    ]

##### args
* theme : Name of the theme.
* save : If you do not want to save is false. Default is true.
* path : Path to save the file. Default is temporary file path.


---
### How to use
#### Output Hints
Separates the slide is `----` or `___` or `***` be returned to hr tab at markdown.  

#### Workflow
1. Create a contents for markdown.
2. Preview the slides in your browser.

---

### Uses
* [Python-Markdown](https://github.com/waylan/Python-Markdown)
* [A Google HTML5 slide template](http://code.google.com/p/html5slides/)


### Licence
[Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0)