import subprocess
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    text = ""
    output = ""  # Variabile per memorizzare l'output dello script
    show_box = False  

    if request.method == "POST":
        if "clear" in request.form:
            text = ""
            output = ""
            show_box = False  
        else:
            text = request.form.get("input_text", "")
            show_box = True  

            # Eseguire subito-searcher.py con il testo come argomento
            try:
                result = subprocess.run(["python", "subito-searcher.py", text],
                                        capture_output=True,
                                        text=True,
                                        check=True)
                                        #encoding="utf-8",  # Aggiunto encoding UTF-8
                                        #errors="ignore")  # Ignora caratteri non supportati
                
                output = result.stdout  # Output dello script
                
            except subprocess.CalledProcessError as e:
                 output = f"Errore nell'esecuzione: {e}\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}"

    return render_template("index.html", text=text, output=output, show_box=show_box)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
