# Actiplanner

Sistema d'informació per al seguiment de plans d'acció derivats de processos de formació empresarial.

Requisits
Python 3.11+
Google Gemini API Key
Instal·lació

Clonar el repositori:

git clone https://github.com/ivanrpuvill/actiplanner.git
cd actiplanner
Backend

Crear l'entorn virtual:

cd backend

python -m venv venv

Activar-lo:

Linux / macOS:

source venv/bin/activate

Windows:

venv\Scripts\activate

Instal·lar dependències:

pip install -r requirements.txt

Configurar la clau de Gemini:

Linux / macOS:

export GEMINI_API_KEY=la_teva_clau

Windows:

set GEMINI_API_KEY=la_teva_clau

Executar el servidor:

uvicorn app.main:app --reload

El backend quedarà disponible a:

http://localhost:8000
Frontend

Obrir:

frontend/index.html

o servir la carpeta amb qualsevol servidor web local.

Dades de demostració

L'aplicació inclou dades d'exemple emmagatzemades als fitxers JSON de la carpeta:

backend/data/
Autor

Ivan Rodríguez Puvill