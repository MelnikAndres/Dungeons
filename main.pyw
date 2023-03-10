import os

def main():
	with open("pings.txt") as f:
		for line in f:
			line = line.rstrip().split(",")[0]
			print(os.system("ping " + line))

main()