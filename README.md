# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your actual tokens and IDs

# 1. Analyze current permissions
python permission_analyzer.py

# 2. Test role escalation
python role_escalation.py

# 3. Test webhook vulnerabilities
python webhook_exploit.py

# 4. Test channel manipulation
python channel_permission_test.py

# 5. Run all
python run_all.py
