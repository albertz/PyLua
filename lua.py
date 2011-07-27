#!/usr/bin/python
# PyCPython - interpret CPython in Python
# by Albert Zeyer, 2011
# code under GPL

import better_exchook
better_exchook.install()

import sys, os, os.path
if __name__ == '__main__':
	MyDir = os.path.dirname(sys.argv[0]) or "."
else:
	MyDir = "."

LuaDir = MyDir + "/lua-5.1.4"

import cparser

def prepareState():
	state = cparser.State()
	state.autoSetupSystemMacros()
	
	def findIncludeFullFilename(filename, local):
		fullfn = LuaDir + "/src/" + filename
		if os.path.exists(fullfn): return fullfn
		fullfn = MyDir + "/" + filename
		if os.path.exists(fullfn): return fullfn	
		return filename
	
	state.findIncludeFullFilename = findIncludeFullFilename
	
	def readLocalInclude(state, filename):
		if filename == "pyconfig.h":
			def reader():
				import ctypes
				sizeofMacro = lambda t: cparser.Macro(rightside=str(ctypes.sizeof(t)))
				state.macros["SIZEOF_SHORT"] = sizeofMacro(ctypes.c_short)
				state.macros["SIZEOF_INT"] = sizeofMacro(ctypes.c_int)
				state.macros["SIZEOF_LONG"] = sizeofMacro(ctypes.c_long)
				state.macros["SIZEOF_LONG_LONG"] = sizeofMacro(ctypes.c_longlong)
				state.macros["SIZEOF_DOUBLE"] = sizeofMacro(ctypes.c_double)
				state.macros["SIZEOF_FLOAT"] = sizeofMacro(ctypes.c_float)
				state.macros["SIZEOF_VOID_P"] = sizeofMacro(ctypes.c_void_p)
				state.macros["SIZEOF_SIZE_T"] = sizeofMacro(ctypes.c_size_t)
				state.macros["SIZEOF_UINTPTR_T"] = sizeofMacro(ctypes.POINTER(ctypes.c_uint))
				state.macros["SIZEOF_PTHREAD_T"] = state.macros["SIZEOF_LONG"]
				state.macros["SIZEOF_PID_T"] = state.macros["SIZEOF_INT"]
				state.macros["SIZEOF_TIME_T"] = state.macros["SIZEOF_LONG"]
				state.macros["SIZEOF__BOOL"] = cparser.Macro(rightside="1")
				return
				yield None # make it a generator
			return reader(), None
		return cparser.State.readLocalInclude(state, filename)
	
	state.readLocalInclude = lambda fn: readLocalInclude(state, fn)
	
	state.autoSetupGlobalIncludeWrappers()
	
	return state

state = prepareState()
cparser.parse(LuaDir + "/src/lua.c", state) # main

import cparser.interpreter

interpreter = cparser.interpreter.Interpreter()
interpreter.register(state)
interpreter.registerFinalize()

if __name__ == '__main__':
	print "erros so far:"
	for m in state._errors:
		print m
	
	print
	print "PyAST of main:"
	interpreter.dumpFunc("main")
	
	args = ("main", len(sys.argv), sys.argv + [None])
	print "Run", args, ":"
	interpreter.runFunc(*args)

