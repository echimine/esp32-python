# FunctionGemma - Function Calling avec llama.cpp

Ce projet démontre l'utilisation de **FunctionGemma** (modèle Google optimisé pour le function calling) via un serveur llama.cpp local.

## 📋 Prérequis

- Python 3.10+
- [llama.cpp](https://github.com/ggerganov/llama.cpp) compilé
- Le modèle quantisé [functiongemma-270m-it-Q4_K_M.gguf](https://huggingface.co/unsloth/functiongemma-270m-it-GGUF)

### Installation des dépendances Python

```bash
pip install "openai>=1.3"
```

## 🚀 Lancement

### 1. Démarrer le serveur llama.cpp

```bash
# Depuis le dossier llama.cpp
./build/bin/llama-server \
  -m /chemin/vers/functiongemma-270m-it-Q4_K_M.gguf \
  --host 127.0.0.1 \
  --port 8080 \
  --ctx-size 4096 \
  --threads 6
```

> **Mac Apple Silicon** : Ajouter `--gpu-layers 99` pour utiliser le GPU Metal.

### 2. Exécuter le script

```bash
python function_gemma_llamacpp.py "Convertis 42 EUR en USD."
```

## 💡 Exemples d'utilisation

```bash
# Conversion de devises
python function_gemma_llamacpp.py "Combien vaut 100 dollars en euros ?"

# Calcul de date
python function_gemma_llamacpp.py "Quelle date sera 30 jours après le 2026-01-15 ?"
```

## 🔧 Fonctions disponibles

| Fonction | Description | Paramètres |
|----------|-------------|------------|
| `convert_currency` | Convertit un montant entre EUR et USD | `amount`, `currency_from`, `currency_to` |
| `add_days` | Ajoute des jours à une date | `start_date` (YYYY-MM-DD), `days` |

## ⚙️ Configuration

Variables d'environnement optionnelles :

```bash
export LLAMA_CPP_BASE_URL="http://127.0.0.1:8080/v1"
export LLAMA_CPP_API_KEY="devkey"
export LLAMA_CPP_MODEL="functiongemma-270m-it-Q4_K_M.gguf"
```

## 📁 Structure du projet

```
.
├── function_gemma_llamacpp.py   # Script principal (llama.cpp)
├── function_gemma_runner.py     # Alternative via Transformers/HuggingFace
├── functiongemma-270m-it-Q4_K_M.gguf  # Modèle quantisé
└── README.md
```

## 🧠 Comment ça marche

1. **Prompt structuré** : Le script envoie un prompt avec les déclarations de fonctions au format JSON Schema
2. **Génération contrainte** : Le modèle génère un appel de fonction `{"name": "...", "parameters": {...}}`
3. **Exécution locale** : Le script parse le JSON et exécute la fonction Python correspondante
4. **Réponse formatée** : Le résultat est affiché à l'utilisateur

## ⚠️ Notes importantes

- **FunctionGemma 270M** est optimisé pour le function calling, pas pour la génération de texte libre
- Le script utilise l'API `/completions` (pas `/chat/completions`) pour un meilleur contrôle du format
- Les taux de change sont fictifs (démo uniquement)

## 📚 Ressources

- [FunctionGemma sur HuggingFace](https://huggingface.co/google/functiongemma-270m-it)
- [llama.cpp](https://github.com/ggerganov/llama.cpp)
- [Documentation Gemma](https://ai.google.dev/gemma)
