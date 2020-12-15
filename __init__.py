"""
=============
GENERAL USAGE
1. place module directory to your project
2. just import it
3. that's all!
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
frame.main()