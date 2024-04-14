import subprocess

# "E:/Tycho-10.8.5Pro/Tycho.exe" 1 "E:/test_download"
solve_bin_path = r'E:/Tycho-10.8.5Pro/Tycho.exe'
solve_file_path = r'E:/test_download/tycho/'

process = subprocess.Popen([solve_bin_path, "1", solve_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print("the commandline is {}".format(process.args))
process.communicate()

# 检查wget的退出状态
if process.returncode == 0:
    print("Download was successful.")

else:
    print("Download failed.")
    print("Error message:", process.stderr)
