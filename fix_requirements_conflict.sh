#!/bin/bash

echo "=== Checking for merge conflict in backend/requirements.txt ==="

if grep -q "<<<<<<<" backend/requirements.txt; then
    echo "[+] Conflict detected. Fixing..."

    # создаём временный файл
    cat << 'EOT' > backend/requirements.txt
fastapi==0.119.1
uvicorn==0.38.0

sqlalchemy>=2.0.0
aiosqlite>=0.19.0
python-dotenv>=1.0.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
pyotp>=2.9.0
httpx>=0.27.0

pydantic>=2.0.0
pydantic-settings>=2.0.0
email-validator>=2.0.0

python-docx>=1.1.0
reportlab>=4.0.0
pytest
EOT

    echo "[+] Conflict removed and requirements.txt restored."

    echo "[+] Adding file to git..."
    git add backend/requirements.txt

    echo "[+] Continuing rebase..."
    git rebase --continue || { echo "[!] REBASE ERROR! Fix manually."; exit 1; }

    echo "[+] Rebase completed."

    echo "[+] Pushing changes..."
    git push || { 
        echo "[!] Push failed. Trying to pull first...";
        git pull --rebase origin main && git push || {
            echo "[!!!] Still failing. Manual intervention required."
            exit 1
        }
    }

    echo "=== DONE ==="
    exit 0
else
    echo "[+] No conflict found. Nothing to fix."
    git status
    exit 0
fi
