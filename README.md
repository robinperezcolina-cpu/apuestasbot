# 🏇 DerbySignals Bot

Bot de Telegram para análisis de carreras de caballos en **Venezuela** y **USA**.

## ✨ Características

- 🇻🇪 Scraping de carreras en La Rinconada (Venezuela)
- 🇺🇸 Scraping de carreras principales de USA (Churchill Downs, Santa Anita, Gulfstream, etc.)
- 📊 Motor de predicción con análisis multi-factor
- 📡 Broadcasting automático al canal de Telegram
- 🎰 Integración de links de afiliado para monetización
- 🚀 Listo para deploy en Railway

## 📋 Comandos del Bot

| Comando | Descripción |
|---------|-------------|
| `/start` | Bienvenida + menú |
| `/carreras` | Ver próximas carreras |
| `/predicciones` | Ver predicciones activas |
| `/predicciones_ve` | Predicciones solo Venezuela |
| `/predicciones_usa` | Predicciones solo USA |
| `/resultados` | Últimos resultados |
| `/help` | Ayuda |
| `/scan` | (Admin) Escaneo manual |
| `/broadcast` | (Admin) Enviar señales al canal |

## 🛠️ Instalación Local

```bash
# Crear entorno virtual
python -m venv venv

# Activar (Windows)
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
copy .env.example .env
# Editar .env con tu token y configuración

# Ejecutar
python main.py
```

## 🚀 Deploy en Railway

1. **Instalar Git**: https://git-scm.com/download/win
2. **Crear repo en GitHub**: https://github.com/new
3. **Subir código**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: DerbySignals bot"
   git remote add origin https://github.com/TU_USUARIO/DerbySignals.git
   git push -u origin main
   ```
4. **Conectar Railway**:
   - Ve a https://railway.app
   - Click "New Project" → "Deploy from GitHub repo"
   - Selecciona tu repo `DerbySignals`
   - En "Variables", agrega las mismas de tu `.env`
   - Railway detectará el `Dockerfile` y desplegará automáticamente

## 📁 Estructura

```
Apuestas/
├── main.py              # Entry point
├── bot.py               # Telegram bot commands
├── broadcaster.py       # Auto-broadcasting
├── config.py            # Configuration
├── models.py            # Data models
├── predictor.py         # Prediction engine
├── strategy.py          # Signal filtering + formatting
├── scraper_venezuela.py # Venezuela racing scraper
├── scraper_usa.py       # USA racing scraper
├── requirements.txt     # Dependencies
├── Dockerfile           # Docker config
├── railway.toml         # Railway config
├── Procfile             # Process definition
├── .env                 # Environment variables (local)
├── .env.example         # Example env file
└── .gitignore           # Git ignore rules
```

## ⚠️ Disclaimer

Las predicciones son análisis estadístico basado en datos públicos. No son garantía de resultados. Apuesta responsablemente.
