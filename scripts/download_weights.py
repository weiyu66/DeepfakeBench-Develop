# -*- coding: utf-8 -*-
"""
下载 DeepfakeBench 官方预训练权重
用法: python scripts/download_weights.py
"""
import os
import sys
import io
import json
import urllib.request

# 修复 Windows 控制台编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

API_URL = "https://api.github.com/repos/SCLBD/DeepfakeBench/releases"


def fetch_releases():
    print("[INFO] 正在查询 GitHub Releases: {}".format(API_URL))
    req = urllib.request.Request(API_URL, headers={
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/vnd.github.v3+json'
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        return data
    except Exception as e:
        print("[ERROR] 查询失败: {}".format(e))
        return []


def list_assets(releases):
    print("\n========== 可用权重下载列表 ==========\n")
    for rel in releases:
        tag = rel.get('tag_name', 'N/A')
        name = rel.get('name', 'N/A')
        assets = rel.get('assets', [])
        if not assets:
            continue
        print("Release: {} -- {}".format(tag, name))
        for asset in assets:
            fname = asset['name']
            fsize = asset['size'] / (1024 * 1024)
            url = asset['browser_download_url']
            print("  - {:40s} ({:.1f} MB)".format(fname, fsize))
            print("    URL: {}".format(url))
        print()


def download_file(url: str, dest_path: str):
    print("[DOWNLOAD] {}".format(url))
    print("[DEST]     {}".format(dest_path))
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=120) as resp:
        total = int(resp.headers.get('Content-Length', 0))
        downloaded = 0
        chunk_size = 1024 * 1024
        with open(dest_path, 'wb') as f:
            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if total > 0:
                    pct = downloaded / total * 100
                    print("\r  Progress: {:.1f}% ({:.1f}/{:.1f} MB)".format(
                        pct, downloaded/(1024*1024), total/(1024*1024)), end='')
    print("\n[DONE]")


def main():
    releases = fetch_releases()
    if not releases:
        print("[ERROR] 无法获取 Releases 信息，请检查网络连接或稍后重试。")
        sys.exit(1)

    list_assets(releases)

    print("提示: 如需下载特定权重，请复制上方 URL 并用浏览器或 wget/curl 下载。")
    print("      下载完成后将 .pth 文件放入 models/ 目录即可。\n")

    # 尝试下载 v1.0.1 中的所有权重
    target_tag = 'v1.0.1'
    for rel in releases:
        if rel.get('tag_name') == target_tag:
            assets = rel.get('assets', [])
            if not assets:
                print("[WARN] {} 下没有可下载的文件。".format(target_tag))
                return
            print("[INFO] 自动下载 {} 下的所有权重到 {} ...".format(target_tag, MODELS_DIR))
            for asset in assets:
                fname = asset['name']
                url = asset['browser_download_url']
                dest = os.path.join(MODELS_DIR, fname)
                if os.path.exists(dest):
                    print("[SKIP] 已存在: {}".format(fname))
                    continue
                try:
                    download_file(url, dest)
                except Exception as e:
                    print("[ERROR] 下载失败 {}: {}".format(fname, e))
            break
    else:
        print("[WARN] 未找到 {} Release，已列出所有可用资源。".format(target_tag))


if __name__ == '__main__':
    main()
