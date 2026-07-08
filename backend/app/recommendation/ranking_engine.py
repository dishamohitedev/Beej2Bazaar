from typing import List
from app.recommendation.models import ScoredCrop

class RankingEngine:
    @staticmethod
    def rank_crops(scored_candidates: List[ScoredCrop], min_threshold: float = 40.0) -> List[ScoredCrop]:
        """
        Sorts crops in descending order of their final score.
        Filters out any crops scoring below a minimum compatibility threshold.
        Returns the Top 5 candidate crops.
        """
        # 1. Filter out crops with low final compatibility score
        viable_crops = [sc for sc in scored_candidates if sc.final_score >= min_threshold]

        # 2. Sort candidates by:
        #    - final_score in descending order (primary)
        #    - crop_name alphabetically in ascending order (secondary, to ensure deterministic ordering for equal scores)
        sorted_crops = sorted(
            viable_crops,
            key=lambda sc: (-sc.final_score, sc.crop.crop_name)
        )

        # 3. Slice and return the Top 5 recommendations
        return sorted_crops[:5]
