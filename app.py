from flask import Flask, request, Response, render_template_string
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

HOME_HTML = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>Web Proxy Saya</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background: #f4f4f4; }
        input { width: 70%; max-width: 600px; padding: 15px; font-size: 18px; border: 2px solid #ccc; border-radius: 8px; }
        button { padding: 15px 30px; font-size: 18px; background: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <h1>🌐 Web Proxy Sendiri</h1>
    <form action="/proxy" method="GET">
        <input type="text" name="url" placeholder="https://www.google.com" required autofocus>
        <br><br>
        <button type="submit">🚀 Buka Situs</button>
    </form>
    <p><small>Contoh: youtube.com, twitter.com, atau https://example.com</small></p>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HOME_HTML)

@app.route('/proxy')
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        return "Masukkan URL yang valid!", 400
    
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(target_url, headers=headers, timeout=20, allow_redirects=True)
        
        content = resp.content
        content_type = resp.headers.get('content-type', 'text/html')

        if 'text/html' in content_type or 'application/xhtml' in content_type:
            soup = BeautifulSoup(content, 'html.parser')
            
            for tag in soup.find_all(['a', 'link', 'form'], href=True):
                if tag['href'].startswith(('http', '//')):
                    tag['href'] = f"/proxy?url={tag['href']}"
            for tag in soup.find_all(['img', 'script'], src=True):
                if tag['src'].startswith(('http', '//')):
                    tag['src'] = f"/proxy?url={tag['src']}"
            
            content = str(soup).encode('utf-8')

        return Response(content, status=resp.status_code, mimetype=content_type)

    except Exception as e:
        return f"Error: {str(e)}<br><a href='/'>Kembali</a>", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
