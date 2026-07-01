"""
Disposal Guide Service
Generates user-friendly disposal guidance text based on recognition results.
"""
from typing import Optional
from 代码包.ai_service.config import DISPOSAL_GUIDES, CATEGORY_SPECIFIC_GUIDES, logger


class GuideService:
    """
    Generates disposal guidance text for recognized garbage items.
    Each category can have a generic guide and an optional specific guide.
    """

    def __init__(self):
        self._generic_guides = DISPOSAL_GUIDES
        self._specific_guides = CATEGORY_SPECIFIC_GUIDES

    def get_guide(self, category_id: int, parent_type: str) -> str:
        """
        Get disposal guide text for a recognized item.

        Priority:
        1. Category-specific guide (if exists)
        2. Parent type generic guide
        3. Default message

        Args:
            category_id: The recognized category ID
            parent_type: The parent type key (recyclable/kitchen/hazardous/other)

        Returns:
            Guide text string
        """
        # 1. Check for category-specific guide
        if category_id in self._specific_guides:
            return self._specific_guides[category_id]

        # 2. Use parent type generic guide
        if parent_type in self._generic_guides:
            return self._generic_guides[parent_type]

        # 3. Default
        return '请根据分类投入对应垃圾桶'

    def get_guide_for_error(self, actual_type: str, expected_type: str) -> str:
        """
        Generate corrective guidance when user puts garbage in wrong bin.

        Args:
            actual_type: The recognized garbage type
            expected_type: The bin type where it was deposited

        Returns:
            Corrective guide text
        """
        actual_name = {
            'recyclable': '可回收物',
            'kitchen': '厨余垃圾',
            'hazardous': '有害垃圾',
            'other': '其他垃圾',
        }.get(actual_type, actual_type)

        expected_name = {
            'recyclable': '可回收物桶',
            'kitchen': '厨余垃圾桶',
            'hazardous': '有害垃圾桶',
            'other': '其他垃圾桶',
        }.get(expected_type, expected_type)

        return f'分类错误！{actual_name}应投入{expected_name}'

    def get_voice_text(self, is_correct: bool, point_change: int,
                       garbage_category: str, correct_category: str = '') -> str:
        """
        Generate voice feedback text for the smart bin terminal.

        Args:
            is_correct: Whether the classification was correct
            point_change: Points awarded or deducted
            garbage_category: Recognized category name
            correct_category: Correct bin category (if wrong)

        Returns:
            Voice text for terminal TTS
        """
        if is_correct:
            if point_change > 0:
                return f'分类正确，+{point_change}积分已到账'
            return '分类正确'
        else:
            if point_change < 0:
                return f'分类错误，{point_change}积分。{garbage_category}应投入{correct_category}'
            return f'分类错误，{garbage_category}应投入{correct_category}'


# Singleton
_guide_service: Optional[GuideService] = None


def get_guide_service() -> GuideService:
    global _guide_service
    if _guide_service is None:
        _guide_service = GuideService()
    return _guide_service
