import os,sys
os.chdir(sys.path[0])
with open("authorized_keys", "w") as authfile:
	for fn in os.listdir("individual_keys"):
		with open("individual_keys/"+fn) as file:
			authfile.write(file.read())
