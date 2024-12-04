import json
import time
import sys
import requests
import os
import wget
import subprocess
import logging

# 创建log目录
os.makedirs("./log", exist_ok=True)
# 设置日志记录
logging.basicConfig(filename=f'./log/update.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    filemode='a')

# 配置文件路径
config_file_path = "update_config.json"
inst_dir = "/root/"

# 获取系统代理设置
http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
proxies = {
    "http": http_proxy,
    "https": https_proxy
}

try:
    if not os.path.exists(config_file_path):
        print(f"文件 {config_file_path} 不存在\n30s后退出...")
        logging.error(f"文件 {config_file_path} 不存在")
        time.sleep(30)
        sys.exit()

    # 加载 JSON 配置文件
    with open(config_file_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
except json.JSONDecodeError:
    print("配置文件加载错误\n30s后退出...")
    logging.error("配置文件加载错误")
    time.sleep(30)
    sys.exit()


def update_config_version(repo_owner, repo_name, new_version):
    try:
        for repo_config in config:
            if repo_config["owner"] == repo_owner and repo_config["repo"] == repo_name:
                repo_config["current_version"] = new_version
                # 保存更新后的配置文件
                with open(config_file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
                print(f"配置文件更新成功: {repo_owner}/{repo_name} 新版本为 {new_version}")
                logging.info(f"配置文件更新成功: {repo_owner}/{repo_name} 新版本为 {new_version}")
                break
    except Exception as e:
        print(f"更新配置文件失败: {e}")
        logging.error(f"更新配置文件失败: {e}")


def dl_pkg(dl_url, prog_name, pkg_name):
    try:
        inst_path = f"{inst_dir}{prog_name}"
        os.makedirs(inst_path, exist_ok=True)
        inst_path = os.path.join(inst_dir, prog_name)
        file_path = f"{inst_path}/{pkg_name}"
        if os.path.exists(file_path):
            os.remove(file_path)

        # 设置 wget 使用的代理
        if http_proxy and https_proxy:
            os.environ["http_proxy"] = http_proxy
            os.environ["https_proxy"] = https_proxy

        print(f"开始下载:{dl_url}")
        logging.info(f"开始下载:{dl_url}")
        wget.download(dl_url, inst_path)
        print(f"\n下载完成! {file_path}")
        logging.info(f"下载完成! {file_path}")
        return inst_path
    except Exception as e:
        print(f"未知错误: {e}")
        logging.error(f"下载失败: {e}")
        return False


def start_inst(inst_path, prog_name, pkg_name):
    try:
        cmds = (f"cd {inst_dir} &&"
                f"tar -xvzf {pkg_name} &&"
                f"cd {inst_path} &&"
                f"chmod +x {prog_name} &&"
                f"nohup ./{prog_name} > {prog_name}.log 2>&1 &")
        result = subprocess.run(cmds, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return True
        else:
            return False
    except Exception as e:
        print(f"未知错误: {e}")
        logging.error(f"安装失败: {e}")
        return False


def kill_prog(prog_name):
    try:
        result = subprocess.run(
            ["pgrep", prog_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.stdout:
            pids = result.stdout.strip().split("\n")  # 进程ID以行分隔
            for pid in pids:
                subprocess.run(["kill", pid])
                print(f"已关闭正在运行的{prog_name} pid:{pid}")
                logging.info(f"已关闭正在运行的{prog_name} pid:{pid}")
        else:
            print(f"{prog_name}未运行")
            logging.info(f"{prog_name}未运行")
    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"停止进程失败: {e}")


# 遍历多个仓库配置
for repo_config in config:
    print("--------------------------------------------------------------------------")
    logging.info("--------------------------------------------------------------------------")
    owner = repo_config["owner"]
    repo = repo_config["repo"]
    pkg_name = repo_config["pkg_name"]
    prog_name = repo_config["prog_name"]
    current_version = repo_config["current_version"]

    try:
        releases_check_api = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        print(f"开始更新:{owner}/{repo}")
        logging.info(f"开始更新:{owner}/{repo}")
        response = requests.get(releases_check_api, proxies=proxies)
        response.raise_for_status()

        response_info = response.json()
        version = response_info["tag_name"]
        print(f"信息获取成功!{owner}/{repo}最新版本:{version}")
        logging.info(f"信息获取成功!{owner}/{repo}最新版本:{version}")
        if current_version == version:
            print("当前已经是最新版本!无需更新")
            logging.info("当前已经是最新版本!无需更新")
            continue
        elif not current_version:
            print("本地暂无更新记录,开始更新!")
            logging.info("本地暂无更新记录,开始更新!")
        else:
            print(f"版本不一致,开始更新!\n"
                  f"本地版本{current_version},git最新版本{version}")
            logging.info(f"版本不一致,开始更新! 本地版本{current_version}, git最新版本{version}")
            kill_prog(prog_name)

        dl_url = f"https://github.com/{owner}/{repo}/releases/download/{version}/{pkg_name}"

        inst_path = dl_pkg(dl_url, prog_name, pkg_name)
        if not inst_path:
            print("下载文件失败！")
            logging.error("下载文件失败！")
            continue
        if start_inst(inst_path, prog_name, pkg_name):
            print(f"{prog_name}更新完成,并且已成功在后台运行!")
            logging.info(f"{prog_name}更新完成,并且已成功在后台运行!")
            # 更新配置文件中的版本号
            update_config_version(owner, repo, version)


    except Exception as e:
        print(f"未知错误: {e}")
        logging.error(f"未知错误: {e}")
