from app.recommendation.models import CropRecord, RecommendationContext

class SeasonScorer:
    @staticmethod
    def score(crop: CropRecord, context: RecommendationContext) -> float:
        """
        Scores season alignment and planting timeliness between 0.0 and 100.0.
        Rewards crops planted at the absolute start of their optimal seasonal window.
        """
        crop_season = crop.season.strip().lower()
        month = context.season.current_month
        
        if crop_season in ["annual", "perennial"]:
            return 95.0  # Annuals can be planted anytime, highly versatile

        if crop_season == "kharif":
            # Optimal sowing: June (6) and July (7)
            if month in [6, 7]:
                return 100.0
            elif month == 8:
                return 80.0  # slightly late sowing
            elif month == 9:
                return 60.0  # very late sowing
            elif month == 5:
                return 75.0  # slightly early sowing
            else:
                return 30.0  # off-season

        elif crop_season == "rabi":
            # Optimal sowing: October (10) and November (11)
            if month in [10, 11]:
                return 100.0
            elif month == 12:
                return 80.0  # slightly late sowing
            elif month == 1:
                return 60.0  # very late sowing
            elif month == 9:
                return 75.0  # slightly early sowing
            else:
                return 30.0  # off-season

        elif crop_season == "zaid":
            # Optimal sowing: March (3) and April (4)
            if month in [3, 4]:
                return 100.0
            elif month == 5:
                return 80.0  # slightly late sowing
            elif month == 2:
                return 75.0  # slightly early sowing
            else:
                return 30.0  # off-season

        return 70.0  # Default safe score for other seasons
