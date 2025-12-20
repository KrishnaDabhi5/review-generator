from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
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

class AddMenuRequest(BaseModel):
    restaurant: str
    food_items: List[str]

class ExtractFoodRequest(BaseModel):
    menu_text: str
    cuisine_type: Optional[str] = None

# PROJECT ROOT (one level up from this file if this file is api/main.py)
ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_PATH = ROOT / "data" / "templates.json"
BUCKETS_PATH = ROOT / "data" / "buckets.json"
FOOD_DB_PATH = ROOT / "data" / "food_items.json"
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
          <!-- Centered image logo inside the bordered container -->
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
            <a class="btn btn-primary" href="/test">Generate Reviews</a>
            <a class="btn btn-secondary" href="/menu">Add Menu</a>
          </div>
        </div>

        <div class="right-container" aria-hidden="true">
          <div class="bg-decor"></div>

          <div class="center-strip" role="presentation">
            <div class="plates">
              <!-- Top plate -->
              <div class="plate top" title="Spicy Pav Bhaji">
                <div class="badge">Spicy Pick</div>
                <img src="/static-api/WhatsApp%20Image%202025-12-19%20at%203.08.30%20PM%20%281%29.jpeg" alt="Pav Bhaji">
              </div>

              <!-- Middle plate -->
              <div class="plate mid small" title="Crispy Masala Dosa">
                <div class="badge" style="left:auto;right:12px;background:#FFB84D">Crispy</div>
                <img src="/static-api/WhatsApp%20Image%202025-12-19%20at%203.08.30%20PM%20%282%29.jpeg" alt="Masala Dosa">
              </div>

              <!-- Bottom plate -->
              <div class="plate bot" title="Tasty Manchurian">
                <div class="badge" style="left:12px;background:#F2A43A">Chef's</div>
                <img src="/static-api/WhatsApp%20Image%202025-12-19%20at%203.08.30%20PM.jpeg" alt="Manchurian">
              </div>
            </div>
          </div>
        </div>
      </div>
      <h1>How To Use</h1>
      <h2>AI REVIEW CARD</h2>

      <div class="step"><div class="num">1</div>Get Your Card</div>
      <div class="step"><div class="num">2</div>Showcase</div>
      <div class="step"><div class="num">3</div>Scan QR Code</div>
      <div class="step"><div class="num">4</div>Customer Reviews</div>

      <div class="buttons">
        <a class="btn btn-primary" href="/test">Generate Reviews</a>
        <a class="btn btn-secondary" href="/menu">Add Menu</a>
      </div>
    </div>

    <div class="right-container" aria-hidden="true">
      <div class="bg-decor"></div>

      <div class="center-strip" role="presentation">
        <div class="plates">
          <!-- Top plate -->
          <div class="plate top" title="Spicy Pav Bhaji">
            <div class="badge">Spicy Pick</div>
            <img src="/static-api/WhatsApp%20Image%202025-12-19%20at%203.08.30%20PM%20%281%29.jpeg" alt="Pav Bhaji">
          </div>

          <!-- Middle plate -->
          <div class="plate mid small" title="Crispy Masala Dosa">
            <div class="badge" style="left:auto;right:12px;background:#FFB84D">Crispy</div>
            <img src="/static-api/WhatsApp%20Image%202025-12-19%20at%203.08.30%20PM%20%282%29.jpeg" alt="Masala Dosa">
          </div>

          <!-- Bottom plate -->
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

@app.get("/menu", response_class=HTMLResponse)
async def menu_form():
    return """
<html>
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Add Menu Items</title>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">
  <style>
    :root{
      --bg1:#FFF7E8;
      --bg2:#FCE9C7;
      --accent:#F4A629;
      --accent2:#E59A18;
      --text:#2A251E;
      --muted:#6F665C;
      --card:#FFFFFF;
      --border:#F0E3C5;
      --danger:#FF3B30;
    }
    *{box-sizing:border-box}
    html,body{height:100%;margin:0;font-family:'Outfit',sans-serif;color:var(--text)}
    body{
      background: radial-gradient(1200px 900px at 10% 10%, var(--bg1), transparent),
                radial-gradient(1100px 900px at 90% 20%, var(--bg2), transparent),
                linear-gradient(180deg, #FFF3DC, #FCE9C7);
      padding:32px 16px 60px;
    }
    .wrap{max-width:860px;margin:0 auto;display:flex;flex-direction:column;gap:26px}
    .topbar{display:flex;justify-content:center;align-items:center;position:relative}
    .back{
      position:absolute;left:0;top:0;
      text-decoration:none;color:var(--accent2);
      font-weight:600;font-size:0.95rem;
      padding:10px 12px;border-radius:999px;
      background:rgba(255,255,255,0.55);
      border:1px solid rgba(240,227,197,0.8);
      box-shadow:0 8px 20px rgba(0,0,0,0.06);
    }
    .back:hover{background:rgba(255,255,255,0.75)}
    .card{
      background:var(--card);
      border-radius:18px;
      padding:26px;
      border:1px solid rgba(240,227,197,0.9);
      box-shadow:0 18px 50px rgba(0,0,0,0.10);
    }
    h1{margin:6px 0 0;text-align:center;font-family:'Playfair Display',serif;color:var(--accent2);font-size:2.1rem;}
    .label{font-weight:700;font-size:0.85rem;margin:14px 0 8px;display:block}
    .input, .textarea{width:100%;border:1px solid #E9E9E9;border-radius:10px;padding:12px;font-size:0.95rem;outline:none;background:#fff;}
    .textarea{min-height:150px;resize:vertical;line-height:1.35}
    .input:focus,.textarea:focus{border-color:rgba(244,166,41,0.65);box-shadow:0 0 0 4px rgba(244,166,41,0.18)}
    .hint{font-size:0.78rem;color:var(--muted);margin-top:8px}
    .actions{margin-top:18px;display:flex;justify-content:center}
    .primary{width:min(520px, 100%);border:none;color:#fff;font-weight:700;padding:12px 16px;border-radius:999px;cursor:pointer;background:linear-gradient(90deg, var(--accent), var(--accent2));}
    .primary:disabled{opacity:0.65;cursor:not-allowed}
    .section-title{text-align:center;font-family:'Playfair Display',serif;color:var(--accent2);margin:0 0 14px;}
    .outline{width:100%;border-radius:999px;padding:10px 14px;background:#fff;border:1.5px solid rgba(244,166,41,0.85);color:var(--accent2);font-weight:700;cursor:pointer;}
    .list{margin-top:14px;display:flex;flex-direction:column;gap:10px}
    .row{display:flex;align-items:center;justify-content:space-between;padding:12px;border-radius:12px;border:1px solid rgba(0,0,0,0.06);background:rgba(255,255,255,0.9);}
    .name{font-weight:700}
    .danger{border:none;background:var(--danger);color:#fff;font-weight:700;padding:8px 12px;border-radius:999px;cursor:pointer;}
    .empty{text-align:center;color:var(--muted);padding:14px 0 2px;font-size:0.92rem;}
    .toast{position:fixed;left:50%;bottom:18px;transform:translateX(-50%);background:rgba(42,37,30,0.92);color:#fff;padding:10px 14px;border-radius:12px;font-size:0.9rem;display:none;max-width:min(520px, calc(100% - 28px));}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="topbar"><a class="back" href="/">&larr; Back to Home</a></div>
    <div class="card">
      <h1>Add Menu Items</h1>
      <form id="menuForm">
        <label class="label" for="restaurant">Restaurant Name</label>
        <input class="input" id="restaurant" name="restaurant" placeholder="e.g. My Fine Dining" autocomplete="off" required />
        <label class="label" for="items">Menu Items</label>
        <textarea class="textarea" id="items" name="items" placeholder="Enter food items (one per line)" required></textarea>
        <div class="hint">List your signature dishes for better AI suggestions.</div>
        <div class="actions"><button class="primary" id="submitBtn" type="submit">Add to Menu Library</button></div>
      </form>
    </div>
    <div class="card">
      <h2 class="section-title">Registered Restaurants</h2>
      <button class="outline" id="refreshBtn" type="button">Refresh List</button>
      <div class="list" id="restaurants"></div>
      <div class="empty" id="emptyState" style="display:none;">No restaurants added yet.</div>
    </div>
  </div>
  <div class="toast" id="toast"></div>
  <script>
    const restaurantsEl = document.getElementById('restaurants');
    const emptyStateEl = document.getElementById('emptyState');
    const refreshBtn = document.getElementById('refreshBtn');
    const form = document.getElementById('menuForm');
    const submitBtn = document.getElementById('submitBtn');
    const toastEl = document.getElementById('toast');

    function showToast(msg) {
      toastEl.textContent = msg;
      toastEl.style.display = 'block';
      window.clearTimeout(showToast._t);
      showToast._t = window.setTimeout(() => { toastEl.style.display = 'none'; }, 2400);
    }

    function normalizeLines(text) {
      return text.split(/\\r?\\n/).map(s => s.trim()).filter(Boolean);
    }

    async function loadRestaurants() {
      restaurantsEl.innerHTML = '';
      emptyStateEl.style.display = 'none';
      try {
        const res = await fetch('/api/all-restaurants');
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(data.detail || 'Failed to load restaurants');
        const list = Array.isArray(data.restaurants) ? data.restaurants : [];
        if (list.length === 0) {
          emptyStateEl.style.display = 'block';
          return;
        }
        list.forEach((name) => {
          const row = document.createElement('div');
          row.className = 'row';
          const left = document.createElement('div');
          left.className = 'name';
          left.textContent = name;
          const del = document.createElement('button');
          del.className = 'danger';
          del.type = 'button';
          del.textContent = 'Delete';
          del.addEventListener('click', async () => {
            const ok = confirm(`Delete restaurant "${name}"?`);
            if (!ok) return;
            try {
              const r = await fetch(`/api/delete-restaurant/${encodeURIComponent(name)}`, { method: 'DELETE' });
              const payload = await r.json().catch(() => ({}));
              if (!r.ok) throw new Error(payload.detail || 'Delete failed');
              showToast('Deleted');
              await loadRestaurants();
            } catch (e) {
              showToast(e?.message || 'Delete failed');
            }
          });
          row.appendChild(left);
          row.appendChild(del);
          restaurantsEl.appendChild(row);
        });
      } catch (e) {
        emptyStateEl.style.display = 'block';
        showToast(e?.message || 'Could not load list');
      }
    }

    refreshBtn.addEventListener('click', loadRestaurants);

    form.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      const restaurant = document.getElementById('restaurant').value.trim();
      const itemsText = document.getElementById('items').value;
      const food_items = normalizeLines(itemsText);
      if (!restaurant) return showToast('Enter restaurant name');
      if (food_items.length === 0) return showToast('Enter at least 1 menu item');
      submitBtn.disabled = true;
      try {
        const res = await fetch('/api/add-menu', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ restaurant, food_items })
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(data.detail || 'Failed to add menu');
        showToast('Menu added');
        document.getElementById('items').value = '';
        await loadRestaurants();
      } catch (e) {
        showToast(e?.message || 'Failed to add menu');
      } finally {
        submitBtn.disabled = false;
      }
    });

    loadRestaurants();
  </script>
</body>
</html>
"""


@app.get("/test")
async def test_form():
    select_path = FRONTEND_DIR / "select.html"
    if select_path.exists():
        return FileResponse(select_path, media_type="text/html")
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path, media_type="text/html")
    return HTMLResponse("<html><body><h1>Select page not found at frontend/select.html</h1></body></html>")


@app.get("/review")
async def review_form():
    review_path = FRONTEND_DIR / "review.html"
    if review_path.exists():
        return FileResponse(review_path, media_type="text/html")
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path, media_type="text/html")
    return HTMLResponse("<html><body><h1>Review page not found at frontend/review.html</h1></body></html>")


@app.post("/api/generate")
async def generate(req: GenerateRequest):
    if not GENERATOR:
        raise HTTPException(status_code=400, detail="Generator not initialized.")
    business_name = req.business or "this restaurant"
    level = req.level if req.level in ["easy", "medium", "detailed"] else "medium"
    review_text = GENERATOR.generate_review(business_name, level)
    return {"review": review_text}


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
    FOOD_EXTRACTOR.add_restaurant_foods(req.restaurant, req.food_items)
    return {"message": "Menu added"}

@app.get("/api/restaurant-foods/{restaurant_name}")
async def get_restaurant_foods(restaurant_name: str):
    if not FOOD_EXTRACTOR:
        raise HTTPException(status_code=500, detail="Food extractor not available.")
    foods = FOOD_EXTRACTOR.get_restaurant_foods(restaurant_name)
    return {"restaurant": restaurant_name, "food_items": foods}

@app.get("/api/all-restaurants")
async def get_all_restaurants():
    if not FOOD_EXTRACTOR:
        raise HTTPException(status_code=500, detail="Food extractor not available.")
    restaurants = FOOD_EXTRACTOR.get_all_restaurants()
    stats = FOOD_EXTRACTOR.get_stats()
    return {"restaurants": restaurants, "stats": stats}

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