from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import requests
from pathlib import Path
from typing import List, Optional

# Import your NLP modules (keep same names/locations as before)
from nlp.template_generator import TemplateReviewGenerator
from nlp.food_aware_generator import FoodAwareReviewGenerator
from nlp.food_extractor import FoodItemExtractor

app = FastAPI(title="Review Generator API with Food Items")

class GenerateRequest(BaseModel):
    business: Optional[str] = None
    level: str = "medium"
    food_items: Optional[List[str]] = None

class GenerateReviewRequest(BaseModel):
    restaurant: Optional[str] = None
    level: str = "medium"

class MenuItem(BaseModel):
    name: str
    rank: int = 0  # Default rank is 0 (will be sorted last)

class AddMenuRequest(BaseModel):
    restaurant: str
    menu_items: List[MenuItem]

class RestaurantProfileRequest(BaseModel):
    restaurant: str
    city: str
    lat: float
    lng: float
    seo_keywords: List[str] = []

# PROJECT ROOT (one level up from this file if this file is api/main.py)
ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_PATH = ROOT / "data" / "templates.json"
BUCKETS_PATH = ROOT / "data" / "buckets.json"
FOOD_DB_PATH = ROOT / "data" / "food_items.json"
PROFILES_PATH = ROOT / "data" / "restaurant_profiles.json"
FRONTEND_DIR = ROOT / "frontend"
API_DIR = ROOT / "api"  # your images are inside the api folder per your message

# mount frontend (if exists) at /static
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# mount api folder (so images placed in api/ can be served) at /static-api
if API_DIR.exists():
    app.mount("/static-api", StaticFiles(directory=str(API_DIR)), name="static_api")


def _load_generator():
    if TEMPLATES_PATH.exists() and BUCKETS_PATH.exists():
        try:
            return TemplateReviewGenerator(str(TEMPLATES_PATH), str(BUCKETS_PATH))
        except Exception as e:
            print(f"Warning: Could not load generator: {e}")
            return None
    print("Templates or buckets not found; generator not initialized.")
    return None

def _load_food_aware_generator():
    if TEMPLATES_PATH.exists() and BUCKETS_PATH.exists():
        try:
            return FoodAwareReviewGenerator(
                str(TEMPLATES_PATH), str(BUCKETS_PATH), str(FOOD_DB_PATH)
            )
        except Exception as e:
            print(f"Warning: Could not load food-aware generator: {e}")
            return None
    print("Templates or buckets not found; food-aware generator not initialized.")
    return None

# Initialize generators/extractor (graceful if files not present)
GENERATOR = _load_generator()
FOOD_GENERATOR = _load_food_aware_generator()

try:
    FOOD_EXTRACTOR = FoodItemExtractor(str(FOOD_DB_PATH))
except Exception as e:
    print(f"Warning: Could not initialize FoodItemExtractor: {e}")
    FOOD_EXTRACTOR = None

# ===================== UPDATED UI PAGE (logo image centered) =========================
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>AIRAA - AI Review Card</title>
      <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">

      <style>
        :root{
          --accent:#E4A636;
          --accent-dark:#B07B13;
          --muted:#6F665C;
        }
        *{box-sizing:border-box}
        html,body{height:100%;margin:0;font-family:'Outfit',sans-serif;background:#f7f5f2;}

        /* layout container */
        .layout{
          display:flex;
          align-items:center;             /* center vertically so card lines up with plates */
          justify-content:flex-start;
          height:100vh;
          padding:48px;
          gap:28px;
        }

        /* LEFT CARD - moved close to the images and vertically centered with them */
        .card{
          width:420px;
          background:white;
          border-radius:22px;
          padding:36px;
          box-shadow:0 12px 40px rgba(0,0,0,0.12);
          z-index:5;
          transform: translateX(220px);   /* move card closer to the centered plates */
        }

        /* Center the logo image inside its bordered container */
        .logo{
          border:3px solid var(--accent);
          padding:10px 22px;
          font-size:2rem;
          font-family:'Playfair Display',serif;
          text-align:center;
          display:flex;                 /* center the image horizontally and vertically */
          align-items:center;
          justify-content:center;
          border-radius:8px;
          background:transparent;
        }

        /* Ensure the image is centered and sized nicely */
        .logo img{
          width:140px;
          height:auto;
          display:block;
          object-fit:contain;
        }

        h1{margin-top:18px;font-family:'Playfair Display',serif;color:var(--accent-dark);text-align:center;}
        h2{font-size:0.9rem;text-align:center;color:var(--muted);letter-spacing:2px;margin-bottom:24px;}
        .step{border:1px solid #E6D9B4;border-radius:14px;padding:10px 14px;display:flex;gap:12px;margin-bottom:12px;align-items:center}
        .num{width:28px;height:28px;border-radius:50%;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700}
        .buttons{display:flex;gap:12px;margin-top:18px}
        .btn{flex:1;border-radius:26px;padding:12px;text-align:center;text-decoration:none;font-weight:600;font-size:0.95rem;display:inline-block}
        .btn-primary{background:linear-gradient(90deg,var(--accent),var(--accent-dark));color:white}
        .btn-secondary{background:white;border:2px solid var(--accent);color:var(--accent-dark)}

        /* RIGHT: full cover background and translucent center panel */
        .right-container{
          flex:1;
          height:100%;
          display:flex;
          align-items:center;
          justify-content:center;
          position:relative;
          overflow:visible;
        }

        /* make the background cover all visible area */
        .bg-decor {
          position:fixed;
          inset:0;
          background-image: url('https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&w=2000&q=60');
          background-size:cover;
          background-position:center;
          filter: blur(3px) saturate(0.95);
          opacity:0.62;
          z-index:0;
        }

        /* center translucent strip - keep dishes in the same place (no change to plates) */
        .center-strip {
          position:relative;
          z-index:2;
          width:520px;
          height:78%;
          border-radius:20px;
          display:flex;
          align-items:center;
          justify-content:center;
          background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.04));
          box-shadow: 0 18px 60px rgba(0,0,0,0.08);
          overflow:visible;
          transform: translateX(90px); /* keep the plates in the same visual position */
        }

        /* container for stacked floating squares */
        .plates {
          position:relative;
          width:86%;
          height:100%;
          display:flex;
          flex-direction:column;
          align-items:center;
          justify-content:center;
          gap:22px;
        }

        /* larger rectangular 'plates' */
        .plate {
          width:340px;
          height:200px;
          border-radius:12px;
          overflow:hidden;
          background:#fff;
          display:flex;
          align-items:center;
          justify-content:center;
          border:6px solid rgba(255,255,255,0.08);
          box-shadow: 0 18px 48px rgba(0,0,0,0.16);
          transform-origin:center;
          transition: transform .28s ease, box-shadow .28s ease;
        }

        .plate img{
          width:100%;
          height:100%;
          object-fit:cover;
          display:block;
        }

        .plate.small { width:280px; height:160px; border-width:5px; box-shadow:0 12px 32px rgba(0,0,0,0.12); }

        /* floating animations (unchanged) */
        .plate.top { animation:floatTop 6.4s ease-in-out infinite; }
        .plate.mid { animation:floatMid 5.8s ease-in-out infinite; }
        .plate.bot { animation:floatBot 7s ease-in-out infinite; }

        @keyframes floatTop {
          0% { transform: translateY(0px); }
          25% { transform: translateY(-20px); }
          50% { transform: translateY(0px); }
          75% { transform: translateY(-10px); }
          100% { transform: translateY(0px); }
        }
        @keyframes floatMid {
          0% { transform: translateY(0px); }
          20% { transform: translateY(-12px); }
          40% { transform: translateY(-24px); }
          60% { transform: translateY(-8px); }
          100% { transform: translateY(0px); }
        }
        @keyframes floatBot {
          0% { transform: translateY(0px); }
          30% { transform: translateY(-16px); }
          60% { transform: translateY(-6px); }
          100% { transform: translateY(0px); }
        }

        .badge {
          position:absolute;
          top:10px;
          left:12px;
          background:var(--accent);
          color:white;
          padding:6px 10px;
          border-radius:10px;
          font-weight:700;
          font-size:0.82rem;
          box-shadow:0 6px 14px rgba(0,0,0,0.12);
        }

        .plate:hover { transform: translateY(-10px) scale(1.03); box-shadow:0 30px 80px rgba(0,0,0,0.22); cursor:pointer; }

        /* responsive tweaks */
        @media (max-width:1200px){
          .layout{flex-direction:column;gap:18px;padding:18px;align-items:center;justify-content:flex-start}
          .card{width:92%;transform:translateX(0)}
          .right-container{width:100%;height:420px}
          .center-strip{width:92%;height:320px;transform:translateX(0)}
          .plates{flex-direction:row;gap:14px}
          .plate{width:120px;height:80px}
          .plate.small{width:90px;height:60px}
        }
      </style>
    </head>

    <body>
      <div class="layout">
        <div class="card">
          <div class="logo">
            <img src="/static-api/WhatsApp%20Image%202025-12-19%20at%205.07.31%20PM.jpeg" alt="AIRAA">
          </div>
          <h1>How To Use</h1>
          <h2>AI REVIEW CARD</h2>

          <div class="step"><div class="num">1</div>Get Your Card</div>
          <div class="step"><div class="num">2</div>Showcase</div>
          <div class="step"><div class="num">3</div>Scan QR Code</div>
          <div class="step"><div class="num">4</div>Customer Reviews</div>

          <div class="buttons">
            <a class="btn btn-primary" href="/onboarding">Get Started</a>
          </div>
        </div>

        <div class="right-container" aria-hidden="true">
          <div class="bg-decor"></div>

          <div class="center-strip" role="presentation">
            <div class="plates">
              <div class="plate top" title="Spicy Pav Bhaji">
                <div class="badge">Spicy Pick</div>
                <img src="/static-api/WhatsApp%20Image%202025-12-19%20at%203.08.30%20PM%20%281%29.jpeg" alt="Pav Bhaji">
              </div>

              <div class="plate mid small" title="Crispy Masala Dosa">
                <div class="badge" style="left:auto;right:12px;background:#FFB84D">Crispy</div>
                <img src="/static-api/WhatsApp%20Image%202025-12-19%20at%203.08.30%20PM%20%282%29.jpeg" alt="Masala Dosa">
              </div>

              <div class="plate bot" title="Tasty Manchurian">
                <div class="badge" style="left:12px;background:#F2A43A">Chef's</div>
                <img src="/static-api/WhatsApp%20Image%202025-12-19%20at%203.08.30%20PM.jpeg" alt="Manchurian">
              </div>
            </div>
          </div>
        </div>
      </div>
    </body>
    </html>
    """


@app.get("/onboarding")
async def onboarding_form():
    path = FRONTEND_DIR / "onboarding.html"
    if path.exists():
        return FileResponse(path, media_type="text/html")
    return HTMLResponse("<html><body><h1>Onboarding page not found</h1></body></html>")


@app.get("/menu", response_class=HTMLResponse)
async def menu_form():
    return HTMLResponse("<html><body><h1>Not Found</h1></body></html>", status_code=404)


@app.get("/test")
async def test_form():
    review_path = FRONTEND_DIR / "review.html"
    if review_path.exists():
        return FileResponse(review_path, media_type="text/html")
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path, media_type="text/html")
    select_path = FRONTEND_DIR / "select.html"
    if select_path.exists():
        return FileResponse(select_path, media_type="text/html")
    return HTMLResponse("<html><body><h1>Frontend not found</h1></body></html>")


@app.get("/review")
async def review_form(request: Request):
    target = "/test"
    if request.url.query:
        target = f"{target}?{request.url.query}"
    return RedirectResponse(url=target, status_code=307)


@app.post("/api/generate")
async def generate(req: GenerateRequest):
    if not GENERATOR:
        raise HTTPException(status_code=400, detail="Generator not initialized.")
    business_name = req.business or "this restaurant"
    level = req.level if req.level in ["easy", "medium", "detailed"] else "medium"
    review_text = GENERATOR.generate_review(business_name, level)
    return {"review": review_text}


@app.post("/api/generate-review")
async def generate_review(req: GenerateReviewRequest):
    business_name = (req.restaurant or "").strip() or "this restaurant"
    level = req.level if req.level in ["easy", "medium", "detailed"] else "medium"

    # Try to load saved menu items for this restaurant (Option A: use only saved menu)
    menu_items = []
    if FOOD_EXTRACTOR:
        try:
            menu_items = FOOD_EXTRACTOR.get_restaurant_foods(business_name, include_ranks=False)
        except Exception:
            menu_items = []

    # If we have saved menu items, use FoodAwareGenerator with only those items
    if FOOD_GENERATOR and menu_items:
        review_text = FOOD_GENERATOR.generate_review(business_name, level, food_items=menu_items)
        return {"review": review_text}

    # If no menu or generator unavailable, fall back to generic sentences (no specific food names)
    if GENERATOR:
        review_text = GENERATOR.generate_review(business_name, level)
        return {"review": review_text}

    raise HTTPException(status_code=400, detail="Generator not initialized.")


@app.post("/api/generate-with-food")
async def generate_with_food(req: GenerateRequest):
    if not FOOD_GENERATOR:
        raise HTTPException(status_code=400, detail="Food-aware generator not initialized.")
    business_name = req.business or "this restaurant"
    level = req.level if req.level in ["easy", "medium", "detailed"] else "medium"
    review_text = FOOD_GENERATOR.generate_review(business_name, level, req.food_items)
    return {"review": review_text}


@app.post("/api/add-menu")
async def add_menu(req: AddMenuRequest):
    if not FOOD_EXTRACTOR:
        raise HTTPException(status_code=500, detail="Food extractor not available.")
    
    # Convert menu items to the format expected by the extractor
    menu_items = [{"name": item.name, "rank": item.rank} for item in req.menu_items]
    
    FOOD_EXTRACTOR.add_restaurant_foods(req.restaurant, menu_items)
    return {"message": "Menu added"}


@app.post("/api/restaurant-profile")
async def save_restaurant_profile(req: RestaurantProfileRequest):
    restaurant = (req.restaurant or "").strip()
    if not restaurant:
        raise HTTPException(status_code=400, detail="Restaurant name is required")

    try:
        PROFILES_PATH.parent.mkdir(parents=True, exist_ok=True)
        profiles = {}
        if PROFILES_PATH.exists():
            with open(PROFILES_PATH, "r", encoding="utf-8") as f:
                profiles = json.load(f) or {}
        profiles[str(restaurant).lower()] = {
            "restaurant": restaurant,
            "city": (req.city or "").strip(),
            "lat": float(req.lat),
            "lng": float(req.lng),
            "seo_keywords": [str(k).strip().lower() for k in (req.seo_keywords or []) if str(k).strip()],
        }
        with open(PROFILES_PATH, "w", encoding="utf-8") as f:
            json.dump(profiles, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save profile: {e}")

    return {"message": "Profile saved"}


@app.get("/api/geocode")
async def geocode(q: str):
    query = (q or "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")

    candidates = [query]
    parts = [p.strip() for p in query.split(",") if p.strip()]
    if len(parts) >= 4:
        candidates.append(", ".join(parts[-4:]))
    if len(parts) >= 3:
        candidates.append(", ".join(parts[-3:]))
    if len(parts) >= 2:
        candidates.append(", ".join(parts[-2:]))

    headers = {
        "Accept": "application/json",
        "User-Agent": "AIRAA-Review-Generator/1.0 (local dev)",
    }

    last_err = None
    for cand in candidates:
        try:
            resp = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={"format": "json", "q": cand, "limit": 1},
                headers=headers,
                timeout=10,
            )
            if resp.status_code != 200:
                last_err = f"HTTP {resp.status_code}"
                continue
            data = resp.json() if resp.content else []
            if not isinstance(data, list) or not data:
                continue
            item = data[0] or {}
            lat = float(item.get("lat"))
            lng = float(item.get("lon"))
            return {"lat": lat, "lng": lng}
        except requests.exceptions.RequestException as e:
            last_err = f"Request error: {e}"
        except json.JSONDecodeError as e:
            last_err = f"JSON decode error: {e}"
        except Exception as e:
            last_err = str(e)

    if last_err:
        raise HTTPException(status_code=400, detail=f"Geocoding failed: {last_err}")
    raise HTTPException(status_code=400, detail="No results found")


@app.get("/api/restaurant-foods/{restaurant_name}")
async def get_restaurant_foods(restaurant_name: str, include_ranks: bool = False):
    if not FOOD_EXTRACTOR:
        raise HTTPException(status_code=500, detail="Food extractor not available.")
    
    foods = FOOD_EXTRACTOR.get_restaurant_foods(restaurant_name, include_ranks=include_ranks)
    return {
        "restaurant": restaurant_name, 
        "food_items": foods if include_ranks else [item['name'] if isinstance(item, dict) else item for item in foods]
    }


@app.get("/api/all-restaurants")
async def get_all_restaurants():
    if not FOOD_EXTRACTOR:
        raise HTTPException(status_code=500, detail="Food extractor not available.")
    
    # Get all restaurants with their menu items (including ranks)
    restaurants = {}
    for name in FOOD_EXTRACTOR.get_all_restaurants():
        items = FOOD_EXTRACTOR.get_restaurant_foods(name, include_ranks=True)
        restaurants[name] = items
    
    stats = FOOD_EXTRACTOR.get_stats()
    return {
        "restaurants": list(restaurants.keys()),
        "menus": restaurants,
        "stats": stats
    }


@app.delete("/api/delete-restaurant/{restaurant_name}")
async def delete_restaurant(restaurant_name: str):
    if not FOOD_EXTRACTOR:
        raise HTTPException(status_code=500, detail="Food extractor not available.")
    FOOD_EXTRACTOR.delete_restaurant(restaurant_name)
    return {"message": "Restaurant deleted"}

if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=False)