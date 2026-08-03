import os
import base64
import requests
from typing import Tuple
from PIL import Image
import io

class VisionProcessor:
    def __init__(self, model: str = "qwen2.5vl:7b"):
        self.model = model
        self.api_url = "http://localhost:11434/api/generate"
        self.available = self._check_ollama()
        
    def _check_ollama(self) -> bool:
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                print("✅ Ollama is running")
                return True
            return False
        except Exception as e:
            print(f"⚠️ Ollama not running: {e}")
            return False
    
    def _encode_image(self, image_path: str) -> str:
        with Image.open(image_path) as img:
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            buffer.seek(0)
            return base64.b64encode(buffer.read()).decode('utf-8')
    
    def identify_image_type(self, image_path: str) -> Tuple[str, str]:
        """Identify if image is car damage, injury, or other"""
        prompt = """You are an insurance AI classifier. Determine what this image shows.

Answer with ONE word:
- "CAR_DAMAGE" if image shows a vehicle with visible damage (dent, scratch, crack, broken parts, collision damage)
- "INJURY" if image shows a person with visible injury (cut, bruise, burn, wound, bleeding, broken bone, bandage, medical situation)
- "OTHER" for anything else (animals, food, landscapes, logos, etc.)

Answer:"""
        
        try:
            image_base64 = self._encode_image(image_path)
            
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "images": [image_base64],
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json().get("response", "").strip().upper()
                if result == "CAR_DAMAGE":
                    return "car_damage", "Image classified as vehicle damage."
                elif result == "INJURY":
                    return "injury", "Image classified as personal injury."
                else:
                    return "other", "❌ This image does not show car damage or personal injury. Please upload a relevant photo."
            return "other", "Could not classify image."
            
        except Exception as e:
            return "other", f"Error: {e}"
    
    def analyze_injury(self, image_path: str, health_policy_context: str = "") -> str:
        """Analyze injury image and provide health insurance recommendations"""
        if not self.available:
            return "⚠️ Ollama is not running. Please start Ollama first."
        
        prompt = f"""You are an expert medical claims adjuster. Analyze this injury photo using the health insurance policy below.

{health_policy_context}

Based on the image and the policy above, provide a response with:

1. **🩺 INJURY ASSESSMENT:**
   - What type of injury do you see? (cut, burn, bruise, swelling, fracture, etc.)
   - Severity (minor/moderate/severe)
   - Likely cause (accident, fall, burn, etc.)
   - Body part(s) affected

2. **📋 COVERAGE APPLIES:**
   - This falls under your Health Policy (HEALTH-2024-002)
   - Emergency room vs urgent care vs doctor visit recommendation
   - Applicable copay or deductible

3. **💰 YOUR OUT-OF-POCKET COST:**
   - ER copay: $150 (waived if admitted)
   - Annual deductible: $1,500 (you pay until reached)
   - After deductible: 80% coverage, you pay 20%
   - Out-of-pocket maximum: $5,000

4. **📝 IMMEDIATE NEXT STEPS:**
   - Seek medical attention if severe
   - Document the injury with photos
   - Keep all medical receipts
   - File claim with Lemonade Health

5. **⚠️ IMPORTANT NOTES:**
   - Pre-existing conditions: first 12 months not covered
   - Waiting periods: Maternity (9 months), Mental health therapy (3 months)
   - Dental and vision require separate plans

Be specific, helpful, and reference the policy details."""
        
        try:
            image_base64 = self._encode_image(image_path)
            
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "images": [image_base64],
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get("response", "No analysis generated.")
            else:
                return f"❌ Error: API returned {response.status_code}"
                
        except requests.exceptions.Timeout:
            return "❌ Timeout: Ollama took too long to respond."
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def analyze_damage(self, image_path: str, policy_context: str = "") -> str:
        """Analyze car damage and provide auto insurance recommendations"""
        if not self.available:
            return "⚠️ Ollama is not running. Please start Ollama first."
        
        prompt = f"""You are an expert auto insurance adjuster. Analyze this car damage photo using the policy information below.

{policy_context}

Based on the image and the policy above, provide a response with:

1. **🔍 DAMAGE ASSESSMENT:**
   - What part(s) of the vehicle are damaged?
   - Type of damage (dent, scratch, crack, broken, shattered)
   - Severity (minor/moderate/severe)
   - Likely cause of damage

2. **📋 WHICH COVERAGE APPLIES:**
   - State specifically: Collision, Comprehensive, or Glass
   - Explain WHY this coverage applies based on the damage
   - Reference the policy deductible amount

3. **💰 YOUR OUT-OF-POCKET COST:**
   - The deductible you must pay
   - Example: "You pay the first $XXX, insurance pays the rest"

4. **📝 IMMEDIATE NEXT STEPS:**
   - Claim hotline number: 1-800-555-0123
   - What photos/documentation to prepare
   - Timeline for repair estimate

5. **⚠️ IMPORTANT NOTES:**
   - Any exclusions that might apply
   - Whether this claim might affect premiums
   - Glass claims ($0 deductible) generally don't increase rates

Be specific, helpful, and reference the actual policy numbers and deductibles."""
        
        try:
            image_base64 = self._encode_image(image_path)
            
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "images": [image_base64],
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get("response", "No analysis generated.")
            else:
                return f"❌ Error: API returned {response.status_code}"
                
        except requests.exceptions.Timeout:
            return "❌ Timeout: Ollama took too long to respond."
        except Exception as e:
            return f"❌ Error: {str(e)}"

_vision_instance = None

def get_vision_processor():
    global _vision_instance
    if _vision_instance is None:
        _vision_instance = VisionProcessor()
    return _vision_instance