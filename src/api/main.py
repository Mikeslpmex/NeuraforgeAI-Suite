import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
import requests
from datetime import datetime

# Importar el cliente del tesorero (asumiendo que está en ../tesorero)
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tesorero'))
try:
    from orion_treasury import OrionTreasury
    tesorero_disponible = True
except ImportError:
    tesorero_disponible = False
    logging.warning("Tesoro no disponible, modo simulado")

# Configuración
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="NeuraforgeAI Unified API")

# Simulación de base de datos de afiliados (reemplazar con DB real)
referrals_db = {}
clicks_db = {}

# ========== Endpoints W3C Proxy ==========
@app.get("/v1/w3c/standards")
async def get_ai_standards():
    try:
        response = requests.get("https://api.w3.org/specifications?tag=ai", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "message": "W3C API no disponible"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/v1/agents/validate")
async def validate_agent(agent_code: str):
    return {
        "valid": True,
        "compliance_score": 95,
        "recommendations": ["Implementar WebAuthn"]
    }

@app.get("/v1/agents/reputation/{agent_id}")
async def get_reputation(agent_id: str):
    return {
        "agent_id": agent_id,
        "reputation": 85,
        "standards_compliant": ["ethical-web-principles", "webcrypto"],
        "last_verified": datetime.utcnow().isoformat()
    }

# ========== Endpoints de Afiliados ==========
class ReferralCreate(BaseModel):
    user_id: str
    user_name: str

class ClickRegister(BaseModel):
    referral_code: str
    target_url: str

@app.post("/api/referral/create")
async def create_referral(data: ReferralCreate):
    import secrets
    code = secrets.token_urlsafe(8)
    referrals_db[code] = {
        "user_id": data.user_id,
        "user_name": data.user_name,
        "created_at": datetime.utcnow(),
        "total_clicks": 0,
        "total_earned_fc": 0.0
    }
    return {"code": code}

@app.get("/api/referral/info/{code}")
async def get_referral_info(code: str):
    ref = referrals_db.get(code)
    if not ref:
        raise HTTPException(404, "Código no encontrado")
    return ref

@app.post("/api/referral/click")
async def register_click(data: ClickRegister):
    ref = referrals_db.get(data.referral_code)
    if not ref:
        raise HTTPException(400, "Código inválido")
    
    earning = 0.001  # ForgeCoins por clic
    ref["total_clicks"] += 1
    ref["total_earned_fc"] += earning
    
    # Registrar clic en histórico
    if data.referral_code not in clicks_db:
        clicks_db[data.referral_code] = []
    clicks_db[data.referral_code].append({
        "target_url": data.target_url,
        "timestamp": datetime.utcnow(),
        "earned_fc": earning
    })
    
    # Transferir ForgeCoins usando el tesorero real (si está disponible)
    if tesorero_disponible:
        try:
            treasury = OrionTreasury()
            # Ajusta el método según tu clase (puede ser transfer, send, etc.)
            treasury.transfer(
                from_wallet="tesorero_orion",
                to_wallet=ref["user_id"],
                amount=earning,
                concept=f"Click en enlace de afiliado: {data.target_url}"
            )
        except Exception as e:
            logger.error(f"Error en transferencia: {e}")
    else:
        logger.info(f"Simulando transferencia de {earning} FC a {ref['user_id']}")
    
    return {"status": "ok", "earned_fc": earning, "total_earned": ref["total_earned_fc"]}

# ========== Endpoint de Redirección con Tracking ==========
@app.get("/click")
async def redirect_with_tracking(ref: str, dest: str):
    """
    Registra un clic y redirige a la URL correspondiente.
    Uso: /click?ref=CODIGO&dest=err_timeout
    """
    # Registrar clic
    ref_data = referrals_db.get(ref)
    if not ref_data:
        raise HTTPException(400, "Código de referido inválido")
    
    earning = 0.001
    ref_data["total_clicks"] += 1
    ref_data["total_earned_fc"] += earning
    
    if tesorero_disponible:
        try:
            treasury = OrionTreasury()
            treasury.transfer(
                from_wallet="tesorero_orion",
                to_wallet=ref_data["user_id"],
                amount=earning,
                concept=f"Click en enlace de afiliado: {dest}"
            )
        except Exception as e:
            logger.error(f"Error en transferencia: {e}")
    else:
        logger.info(f"Simulando transferencia de {earning} FC a {ref_data['user_id']} por clic en {dest}")
    
    # Mapeo de destinos a URLs reales (acortadores)
    url_map = {
        "err_timeout": "https://acortador.tu/err_timeout",
        "err_name": "https://acortador.tu/err_name",
        # Agrega más según tu tabla
    }
    target = url_map.get(dest, "https://tusitio.com/errores.html")
    return RedirectResponse(url=target)

# ========== Root ==========
@app.get("/")
async def root():
    return {"message": "NeuraforgeAI Unified API is alive"}
