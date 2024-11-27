from app import app
from flask import Flask, request, jsonify, render_template
import os


def is_allowed_path(file_path):
    """
    检查文件路径是否在允许的目录中。
    """
    # 合法路径和映射目录
    if os.path.basename(file_path) == "test.cons.bam":
        return True
    ALLOWED_DIRECTORIES = ["/"] # 如果需要限制目录，更改为本地项目路径，例如 /path/to/projects
    for allowed_dir in ALLOWED_DIRECTORIES:
        if file_path.startswith(allowed_dir) and os.path.exists(file_path):
            return True
    return False

def create_symlink(file_path):
    """
    为合法路径创建软链接，并返回映射路径。
    """
    if not is_allowed_path(file_path):
        return None

    print("app.root_path", app.root_path)
    SYMLINK_DIR = app.root_path + "/static/dynamic_bam/"
    print("app.root_path", SYMLINK_DIR)
    # 初始化动态 BAM 文件目录    

    os.makedirs(SYMLINK_DIR, exist_ok=True)

    file_name = os.path.basename(file_path)
    symlink_path = os.path.join(SYMLINK_DIR, file_name)

    # 如果软链接已经存在，先删除
    if os.path.islink(symlink_path) or os.path.exists(symlink_path):
        os.remove(symlink_path)
    os.symlink(file_path, symlink_path)
    # flask 应用只能访问app.root_path下路径， 相当于app.root_path为'/'
    return f"/static/dynamic_bam/{file_name}"

@app.route("/")
def index():
    """
    渲染前端页面
    """
    return render_template("index.html")

@app.route("/api/check-bam", methods=["POST"])
def check_bam():
    """
    检查 BAM 文件路径，并返回映射的静态路径。
    """
    data = request.json
    bam_path = data.get("bam_path")
    print(f"bam_path:{bam_path}")

    if not bam_path:
        return jsonify({"error": "BAM path is required."}), 400

    symlink = create_symlink(bam_path)
    if not symlink:
        return jsonify({"error": "File not found or not allowed."}), 404

    bam_index_symlink = create_symlink(bam_path + ".bai")
    if not bam_index_symlink:
        return jsonify({"error": "Index file not found."}), 404

    return jsonify({"bam_url": symlink, "bam_index_url": bam_index_symlink})



