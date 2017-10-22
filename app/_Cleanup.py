from auxly.filesys import delete

delete("__pycache__")
delete("__output__")
delete("poppage.egg-info")
delete("dist")
delete("build")
delete(".", "\.log$")
delete(".", "\.pyc$")
