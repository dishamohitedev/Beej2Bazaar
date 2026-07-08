import httpx
import logging
from typing import List

from app.core.config import settings
from app.recommendation.models import ScoredCrop, RecommendationContext

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self):
        # We use gemini-1.5-flash which is fast, lightweight and has a robust free tier
        self.model_name = "gemini-1.5-flash"
        self.api_url = f"https://generativelanguage.googleapis.com/v1/models/{self.model_name}:generateContent"

    def generate_explanations(self, recommendations: List[ScoredCrop], context: RecommendationContext) -> str:
        """
        Generates a natural language explanation of why the recommended crops are suitable.
        Asks Gemini to output the explanation in the farmer's preferred language.
        Falls back to a clean programmatic local explanation if the API key is missing or calls fail.
        """
        api_key = settings.GEMINI_API_KEY
        
        # If API key is missing, fall back immediately to programmatic generator
        if not api_key:
            logger.info("GEMINI_API_KEY is not configured. Using programmatic local fallback.")
            return self._generate_local_fallback(recommendations, context)

        # 1. Build the list of crops and scores for the prompt
        crops_details = []
        for idx, rec in enumerate(recommendations):
            crops_details.append(
                f"{idx+1}. {rec.crop.crop_name} ({rec.crop.scientific_name}) - Final Score: {rec.final_score}/100\n"
                f"   - Soil Matching Score: {rec.scores.soil_score}/100\n"
                f"   - Weather Suitability Score: {rec.scores.weather_score}/100\n"
                f"   - Water/Irrigation Score: {rec.scores.water_score}/100\n"
                f"   - Market Price Score: {rec.scores.market_score}/100\n"
                f"   - Season Alignment Score: {rec.scores.season_score}/100\n"
                f"   - Risk Susceptibility Score: {rec.scores.risk_score}/100"
            )
        crops_text = "\n".join(crops_details)

        # 2. Get local mandi prices for the prompt context
        mandi_prices = []
        for price in context.market:
            mandi_prices.append(f"{price.commodity}: Rs. {price.modal_price}/quintal (Mandi: {price.market})")
        mandi_text = "\n".join(mandi_prices)

        # 3. Formulate the prompt
        target_lang = context.profile.language.strip()
        prompt = (
            "You are a professional, expert agricultural scientist and agronomist in India.\n"
            "Your task is to explain in a warm, friendly, and practical tone why these Top 5 crops are highly recommended for the farmer's land.\n\n"
            f"--- FARMER PROFILE ---\n"
            f"Farmer Name: {context.profile.full_name}\n"
            f"Location: Village {context.profile.village}, Taluka {context.profile.taluka}, District {context.profile.district}, State {context.profile.state}\n"
            f"Soil Type: {context.profile.soil_type}\n"
            f"Irrigation Source: {context.profile.irrigation}\n"
            f"Farm Size: {context.profile.farm_size} {context.profile.farm_unit}\n\n"
            f"--- ENVIRONMENTAL CONTEXT ---\n"
            f"Current Season: {context.season.current_season} (Month: {context.season.current_month})\n"
            f"Weather Forecast: Average Min Temp {context.weather.temp_min}°C, Max Temp {context.weather.temp_max}°C, Expected Season Rainfall {context.weather.rainfall_mm} mm\n\n"
            f"--- mandi market prices ---\n"
            f"{mandi_text}\n\n"
            f"--- RECOMMENDED CROPS & SCORES ---\n"
            f"{crops_text}\n\n"
            f"--- INSTRUCTIONS ---\n"
            f"1. Explain why each recommended crop fits the farmer's specific farm parameters. Focus on the alignment of their Soil Type, Current Season, Weather, Water/Irrigation capacity, and Market/Mandi price advantage.\n"
            f"2. Keep the explanation for each crop under 3 sentences. Be scientific but simple.\n"
            f"3. Add a single helpful 'Seasonal Tip' at the very end.\n"
            f"4. IMPORTANT: Write the ENTIRE response in the farmer's preferred language: {target_lang}. If {target_lang} is English, write it in English. If it is Hindi, Telugu, Marathi, or another Indian language, write it entirely in that local language. If the language is not recognized or not supported, default to English.\n"
            f"5. Format the output cleanly in markdown. Do not include device frames or metadata."
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        # 4. Make HTTP Post Request to Gemini API
        try:
            url = f"{self.api_url}?key={api_key}"
            response = httpx.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=8.0)
            
            if response.status_code == 200:
                resp_json = response.json()
                candidates = resp_json.get("candidates", [])
                if candidates:
                    text_content = candidates[0].get("content", {}).get("parts", [])[0].get("text", "")
                    if text_content:
                        return text_content.strip()
            else:
                logger.warning(f"Gemini API returned error code {response.status_code}: {response.text}")
        except Exception as e:
            logger.warning(f"Failed to fetch explanation from Gemini API: {e}. Falling back to local generation.")

        # Fallback to local generator on network/API failure
        return self._generate_local_fallback(recommendations, context)

    def _generate_local_fallback(self, recommendations: List[ScoredCrop], context: RecommendationContext) -> str:
        """Generates a structured programmatic fallback text explaining the top crops."""
        lang = context.profile.language.strip().lower()
        
        # Simple bilingual localized dictionary for fallback structures
        if lang in ["hindi", "hi"]:
            intro = f"नमस्ते {context.profile.full_name}, आपके खेत (मिट्टी: {context.profile.soil_type}, सिंचाई: {context.profile.irrigation}) के लिए हमारे कृषि निर्णय इंजन द्वारा शीर्ष 5 फसलें चुनी गई हैं:\n\n"
            crop_template = (
                "**{name}** (वैज्ञानिक नाम: {sci_name})\n"
                "- **उपयुक्तता स्कोर**: {score}/100\n"
                "- **कारण**: यह फसल इस मौसम ({season}) के लिए बिल्कुल उपयुक्त है। पानी की आवश्यकता ({water_req}) आपकी सिंचाई पद्धति से मेल खाती है और यह {soil} मिट्टी के अनुकूल है।\n"
            )
            tip = "\n**सामयिक कृषि सलाह**: वर्तमान सीजन में उचित जल निकासी बनाए रखें और स्थानीय मंडी दरों की निगरानी करते रहें।"
            
        elif lang in ["marathi", "mr"]:
            intro = f"नमस्कार {context.profile.full_name}, तुमच्या शेतासाठी (माती: {context.profile.soil_type}, सिंचन: {context.profile.irrigation}) आमच्या निर्णय प्रणालीद्वारे निवडलेल्या सर्वोच्च ५ पिके खालीलप्रमाणे आहेत:\n\n"
            crop_template = (
                "**{name}** (वैज्ञानिक नाव: {sci_name})\n"
                "- **एकूण गुण**: {score}/100\n"
                "- **कारण**: हे पीक या हंगामासाठी ({season}) उत्तम आहे. तुमच्या {soil} मातीमध्ये आणि उपलब्ध सिंचन पद्धतीमध्ये हे पीक चांगल्या प्रकारे वाढू शकते.\n"
            )
            tip = "\n**हंगामी सल्ला**: पिकांची लागवड योग्य अंतरावर करा आणि खतांचा वेळेवर वापर करा."
            
        else:  # Default to English
            intro = f"Hello {context.profile.full_name},\n\nBased on your farm details (Soil: {context.profile.soil_type}, Irrigation: {context.profile.irrigation}) and current weather forecast, here are the Top 5 recommended crops:\n\n"
            crop_template = (
                "**{name}** ({sci_name})\n"
                "- **Compatibility Score**: {score}/100\n"
                "- **Why it fits**: Fits perfectly for the {season} season. It performs exceptionally well in {soil} soil with a {water_req} water requirement that aligns with your {irrigation} system.\n"
            )
            tip = "\n**Seasonal Tip**: Focus on timely weeding and monitor local market prices to optimize harvesting schedules."

        # Compile crop items
        lines = [intro]
        for rec in recommendations:
            lines.append(crop_template.format(
                name=rec.crop.crop_name,
                sci_name=rec.crop.scientific_name,
                score=rec.final_score,
                season=context.season.current_season,
                soil=context.profile.soil_type,
                water_req=rec.crop.water_requirement,
                irrigation=context.profile.irrigation
            ))
            
        lines.append(tip)
        return "\n".join(lines)
