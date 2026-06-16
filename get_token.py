"""Скрипт для получения USER_TOKEN через браузер."""
import webbrowser
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import threading


class TokenHandler(BaseHTTPRequestHandler):
    """HTTP-сервер для перехвата токена."""
    
    def do_GET(self):
        """Получаем токен из URL."""
        parsed = urllib.parse.urlparse(self.path)
        
        if parsed.path == '/callback':
            fragment = urllib.parse.parse_qs(parsed.fragment)
            access_token = fragment.get('access_token', [None])[0]
            
            if access_token:
                print("\n" + "="*50)
                print("TOKEN RECEIVED!")
                print("="*50)
                print(f"\nUSER_TOKEN={access_token}\n")
                print("="*50)
                print("Copy the token above and paste it into .env file!")
                print("="*50)
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                response = """
                <html>
                <head><title>Token received!</title></head>
                <body style="font-family: Arial; padding: 50px; text-align: center;">
                    <h1 style="color: green;">Token received!</h1>
                    <p>Go back to terminal and copy the token.</p>
                    <p>Then paste it into .env file</p>
                </body>
                </html>
                """
                self.wfile.write(response.encode('utf-8'))
                
                threading.Timer(2.0, lambda: self.server.shutdown()).start()
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Token not found in URL')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass


def get_token():
    """Получает токен через браузер."""
    print("Starting server for token...")
    
    server = HTTPServer(('localhost', 8080), TokenHandler)
    
    auth_url = (
        "https://oauth.vk.com/authorize?"
        "client_id=2685278&"
        "scope=4194304,262144,131072,8192,4096&"
        "redirect_uri=http://localhost:8080/callback&"
        "response_type=token&"
        "display=page&"
        "v=5.199"
    )
    
    print(f"\nOpening browser for authorization...")
    print(f"If browser didn't open, copy this URL:\n{auth_url}\n")
    
    webbrowser.open(auth_url)
    
    print("Waiting for authorization in browser...")
    print("Click 'Allow' in the browser window.\n")
    
    server.serve_forever()


if __name__ == '__main__':
    get_token()