"""
=============
GENERAL USAGE
1. place module directory to your project
2. add code in your project without comment mark
# import import_checker
# import_checker.frame.start_test(__file__)
===============
WHAT IT WILL DO
By importing it will execute all processes.
1. find all python text-code files in the directory
2. find all module names imported in them
3. open its gui with results
4. if all modules installed in actual python version - close green gui after 2seconds and finish working.
if not - stay red gui, offer installations.
"""

from . import frame
#frame.start_test(...)     # use it in source project!