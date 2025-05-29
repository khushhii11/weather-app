# Weather Explorer & Favorites

A full-stack weather application featuring:

* **FastAPI backend**: Geocoding, current weather, 5-day forecasts, and a CRUD API for saved locations.
* **SQLite database**: Stores user-defined favorite locations.
* **Streamlit frontend**: Interactive UI for managing favorites and viewing weather data.

---

## 🚀 Features

* **Geocoding** using OpenStreetMap’s Nominatim API.
* **Current weather & forecasts** via Open-Meteo API.
* **CRUD operations** on saved locations (favorites).
* **Reverse geocoding** fallback to human-readable names.
* **Responsive UI** built with Streamlit.
* **Info button** linking to Product Manager Accelerator LinkedIn page.

---

## 🧰 Tech Stack

* **Python 3.10+**
* **FastAPI** for REST API
* **SQLAlchemy** with SQLite for ORM & database
* **Pydantic** for request/response models
* **Streamlit** for frontend

---

## 📁 Project Structure

```
weather-app/
├── .env                # Environment variables
├── requirements.txt    # Python dependencies
├── weather.db          # SQLite database file (ignored by Git)
├── weather/            # Backend module
│   ├── __init__.py
│   ├── api.py          # FastAPI router & endpoints
│   ├── database.py     # SQLAlchemy config & init
│   ├── geocode.py      # Nominatim geocoding
│   ├── models.py       # DB models
│   ├── schemas.py      # Pydantic schemas
│   ├── crud.py         # CRUD functions
│   ├── weather_app.py  # Open-Meteo client
│   └── main.py         # FastAPI app entrypoint
└── streamlit.py        # Streamlit frontend
```

---

## ⚙️ Setup & Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/your-username/weather-app.git
cd weather-app
```

### 2. Environment Variables

Create a `.env` file in the project root:

```dotenv
GEOCODER_EMAIL=your.email@example.com
DATABASE_URL=sqlite:///./weather.db
```

* `GEOCODER_EMAIL`: Your contact for Nominatim API.
* `DATABASE_URL`: SQLAlchemy connection string (defaults to SQLite).

### 3. Install & Run

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   .\.venv\Scripts\activate  # Windows PowerShell
   ```
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. Initialize the database and start FastAPI:

   ```bash
   uvicorn main:app --reload
   ```
4. In another terminal, launch Streamlit:

   ```bash
   streamlit run streamlit.py
   ```

---

## 🌐 Deploy on Streamlit Community Cloud

1. Push your code to a **public GitHub** repository.
2. Go to [Streamlit Community Cloud](https://share.streamlit.io) and click **New app**.
3. Select your GitHub repo and branch.
4. Set the **main file** to `streamlit.py` and **Start command** to:

   ```bash
   streamlit run streamlit.py
   ```
5. Click **Deploy**. Your app will be live—no local install needed!

---

## 🛠️ Usage

### API Endpoints

* **Health check**: `GET /` → `{ status: "ok" }`
* **Current weather**: `GET /weather?loc=<lat,lon|address>`
* **5-day forecast**: `GET /forecast?loc=<lat,lon|address>`
* **CRUD Locations**:

  * `POST /locations/` → Create favorite
  * `GET /locations/` → List favorites
  * `GET /locations/{id}` → Retrieve one
  * `PUT /locations/{id}` → Update
  * `DELETE /locations/{id}` → Delete

Docs available at: [http://localhost:8000/docs](http://localhost:8000/docs)

### Streamlit Frontend

* Add, edit, delete favorites.
* Manual lookup for any location.
* View current weather and 5-day forecast.
* Info button linking to [Product Manager Accelerator](https://www.linkedin.com/company/product-manager-accelerator).

---

## 📖 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/YourFeature`
3. Commit your changes: `git commit -m "Add some feature"`
4. Push: `git push origin feature/YourFeature`
5. Open a Pull Request

---

## 📝 License

MIT © \[Khushi]
