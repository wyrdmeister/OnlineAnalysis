Option Explicit

Dim result
result = Msgbox("Do you want to install the OACommon package?", vbYesNo+vbInformation, "")

if result = vbYes then

	'Create shell
	Dim shell
	Set shell = CreateObject("WScript.Shell")

	Dim oExec, retval

	'Check for numpy
	Set oExec = shell.Exec("python -c ""import numpy""")
	retval = oExec.StdErr.ReadAll
	if inStr(retval, "ImportError") then
		wscript.echo "The numpy library is missing. Install it and try again."
		wscript.quit
	end if

	'Check for h5py
	Set oExec = shell.Exec("python -c ""import h5py""")
	retval = oExec.StdErr.ReadAll
	if inStr(retval, "ImportError") then
		wscript.echo "The h5py library is missing. Install it and try again."
		wscript.quit
	end if

	'Running python setup script
	shell.Run("python setup.py install")
end if