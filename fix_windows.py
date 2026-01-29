import os
import subprocess
import re

# Windows 文件名非法字符集合
INVALID_CHARS = r'[<>:"/\\|?*]'

def sanitize_filename(name):
    # 将非法字符替换为全角字符或下划线，避免冲突
    # 这里简单地替换为下划线
    return re.sub(INVALID_CHARS, '_', name)

def get_git_files():
    # 获取 Git 版本库中的所有文件列表
    result = subprocess.run(['git', 'ls-files'], stdout=subprocess.PIPE, text=True, encoding='utf-8')
    return result.stdout.splitlines()

def save_file_content(original_path):
    # 如果文件在 Windows 上不存在（说明包含了非法字符），我们需要从 Git 提取内容
    if os.path.exists(original_path):
        return # 文件存在，无需处理

    print(f"检测到无法创建的文件: {original_path}，正在尝试提取...")

    # 从 git show 读取内容
    # 注意：路径如果包含空格需要小心，git show 接受相对路径
    try:
        content = subprocess.check_output(['git', 'show', f'HEAD:{original_path}'], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        print(f"无法读取: {original_path}")
        return

    # 构建新的合法路径
    dir_name, file_name = os.path.split(original_path)
    safe_file_name = sanitize_filename(file_name)
    
    # 保持目录结构，但如果目录名也有非法字符，这里只是简单处理文件名
    # 为简单起见，我们把这些抢救出来的文件放到一个专门的文件夹 '_Recovered_Docs'
    save_dir = os.path.join('_Recovered_Docs', dir_name)
    os.makedirs(save_dir, exist_ok=True)
    
    safe_path = os.path.join(save_dir, safe_file_name)

    with open(safe_path, 'wb') as f:
        f.write(content)
    print(f"已保存为: {safe_path}")

def main():
    print("开始扫描并恢复非法文件名文件...")
    files = get_git_files()
    for file_path in files:
        # 处理路径分隔符，Git 输出的是 /，Windows 需要兼容
        file_path_os = file_path.replace('/', os.sep)
        save_file_content(file_path) # 传入原始 Git 路径给 git show，传入 OS 路径做检查
    print("处理完成。请查看 '_Recovered_Docs' 文件夹。")

if __name__ == "__main__":
    main()