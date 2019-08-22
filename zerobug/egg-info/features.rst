* Test execution log
* Autodiscovery test modules and functions
* Python 2.7 and 3.5+
* coverage integration
* travis integration


*zerobug* makes avaiable following functions to test:

`Z0BUG.build_os_tree(ctx, list_of_paths)` (python)
`Z0BUG_build_os_tree list_of_paths` (bash)
Build a full os tree from supplied list.
If python, list of paths is a list of strings.
If bash, list is a string of paths separated by spaces.
Function reads list of paths and create all directories.
If directory is an absolute path, the supplied path is created.
If directory is a relative path, the directory is created under tests/res directory.

Warning!
To check is made is parent dir does not exit. Please, supply path from parent
to children, if you want to build a nested tree.


`Z0BUG.remove_os_tree(ctx, list_of_paths)` (python)
`Z0BUG_remove_os_tree list_of_paths` (bash)
Remove a full os tree created by `build_os_tree`
If python, list of paths is a list of strings.
If bash, list is a string of paths separated by spaces.
Function reads list of paths and remove all directories.
If directory is an absolute path, the supplied path is dropped.
If directory is a relative path, the directory is dropped from tests/res directory.

Warning!
Function remove directory and all sub-directories without any control.
Order of directories should be inverse of build_os_tree function.
