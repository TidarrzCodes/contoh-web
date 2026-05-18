from flask import Flask, request, Response, render_template_string
import requests
from bs4 import BeautifulSoup
import os
import re

app = Flask(__name__)

HOME_HTML = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Proxy Saya</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 60px; background: #1e1e2f; color: white; }
        input { width: 70%; max-width: 700px; padding: 15px; font-size: 18px; border-radius: 10px; border: none; }
        button { padding: 15px 35px; font-size: 18px; background: #e74c3c; color: white; border: none; border-radius: 10px; cursor: pointer; }
        button:hover { background: #c0392b; }
    </style>
</head>
<body>
    <h1>🌐 Web Proxy Sendiri</h1>
    <form action="/proxy" method="GET">
        <input type="text" name="url" placeholder="https://www.google.com" required autofocus>
        <br><br>
        <button type="submit">🚀 Buka</button>
    </form>
    <p><small>Coba dulu: wikipedia.org atau example.com</small></p>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HOME_HTML)

@app.route('/proxy')
def proxy_route():
    target_url = request.args.get('url')
    if not target_url:
        return "Masukkan URL!", 400

    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        resp = requests.get(target_url, headers=headers, timeout=20, allow_redirects=True)
        
        content = resp.content
        content_type = resp.headers.get('content-type', 'text/html')

        if 'text/html' in content_type:
            soup = BeautifulSoup(content, 'html.parser')

            # Rewrite link yang lebih agresif
            base_url = target_url.split('?')[0].rstrip('/')

            for tag in soup.find_all(['a', 'link', 'script', 'img', 'form'], href=True):
                href = tag['href']
                if href.startswith(('http', '//')) or href.startswith('/'):
                    if href.startswith('//'):
                        href = 'https:' + href
                    elif href.startswith('/'):
                        href = base_url + href
                    tag['href'] = f"/proxy?url={href}"

            for tag in soup.find_all(['img', 'script', 'source'], src=True):
                src = tag['src']
                if src.startswith(('http', '//')) or src.startswith('/'):
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = base_url + src
                    tag['src'] = f"/proxy?url={src}"

            content = str(soup).encode('utf-8')

        return Response(content, resp.status_code, mimetype=content_type)

    except Exception as e:
        return f"Error: {str(e)}<br><a href='/'>Kembali</a>", 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
