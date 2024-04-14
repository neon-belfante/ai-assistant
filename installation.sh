#!/bin/bash

# Clone the GitHub repository (replace <username> and <repository> with your GitHub username and repository name)
sudo apt install git -y &&\
git clone https://github.com/neon-belfante/ai-assistant.git
cd ai-assistant

sudo apt install python3.10-venv -y &&\
#Check if virtual environment exists
venv_name="ai-environment"
if [ ! -d "$venv_name" ]; then
    python3 -m venv $venv_name
fi

source $venv_name/bin/activate

#Install GTK
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 -y &&\
sudo apt install libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-4.0 -y &&\


#Install required packages from requirements.txt
pip install -r requirements.txt


#Install Ollama
if ! command -v ollama &> /dev/null; then
    echo "OLLAMA is not installed."
    read -p "Would you like to install it now? (y/n) " install_choice
    if [[ $install_choice == "y" ]]; then
      curl -fsSL https://ollama.com/install.sh | sh
      echo "OLLAMA should now be installed."
    else
      echo "OLLAMA is required to run this script. Please install it and try again."
      exit 1
    fi
  fi
ollama serve
ollama pull llama2 &&\
ollama pull llava &&\
ollama pull gemma:2b &&\
ollama pull nomic-embed-text

# Make run_app.sh executable
chmod +x run_app.sh

echo "Installation complete. You can now run the application using cd ai-assistant && run_app.sh"

echo "[Desktop Entry]
Name=My Application
Exec=~/ai-assistant/run_app.sh
Icon=~/ella/ella_icon.png
Path=~/ai-assistant/
Type=Application
Terminal=true" > aiAssistant.desktop

sudo cp aiAssistant.desktop ~/.local/share/applications/

#Deactivate venv
deactivate