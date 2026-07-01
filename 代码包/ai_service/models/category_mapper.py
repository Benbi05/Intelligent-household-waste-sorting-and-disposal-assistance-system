"""
Category Mapper
Maps detection class IDs to garbage categories with parent type classification.
Provides the 50+ → 4 category mapping described in the design document.
"""
from typing import Optional
from 代码包.ai_service.config import CATEGORY_MAP, PARENT_TYPES, PARENT_TYPE_NAMES, logger


class CategoryMapper:
    """
    Maps model output class IDs to the system's category system:
    - 50+ fine-grained categories → 4 parent types
    - Provides Chinese names for each category
    - Supports dynamic loading from database
    """

    def __init__(self, category_map: dict = None):
        self._map = category_map or CATEGORY_MAP

    def get_category(self, class_id: int) -> dict:
        """
        Get full category info for a class ID.

        Returns:
            {
                'categoryId': int,
                'categoryName': str,
                'parentType': str,      # 'recyclable' | 'kitchen' | 'hazardous' | 'other'
                'parentTypeName': str,  # Chinese name
            }
        """
        cat_info = self._map.get(class_id)
        if cat_info is None:
            # Unknown class — default to 'other'
            logger.warning(f'Unknown class_id {class_id}, defaulting to "other"')
            return {
                'categoryId': class_id,
                'categoryName': f'未知物品_{class_id}',
                'parentType': 'other',
                'parentTypeName': PARENT_TYPE_NAMES['other'],
            }

        return {
            'categoryId': class_id,
            'categoryName': cat_info['name'],
            'parentType': cat_info['parent_type'],
            'parentTypeName': PARENT_TYPE_NAMES.get(
                cat_info['parent_type'],
                cat_info['parent_type'],
            ),
        }

    def get_parent_type(self, class_id: int) -> str:
        """Get parent type key for a class ID."""
        return self.get_category(class_id)['parentType']

    def get_class_name(self, class_id: int) -> str:
        """Get Chinese category name for a class ID."""
        return self.get_category(class_id)['categoryName']

    def get_class_name_map(self) -> dict[int, str]:
        """Get full class_id -> class_name mapping (for YOLOv11 inference)."""
        return {cid: info['name'] for cid, info in self._map.items()}

    def get_categories_by_parent(self, parent_type: str) -> list[dict]:
        """Get all sub-categories under a parent type."""
        results = []
        for cid, info in self._map.items():
            if info['parent_type'] == parent_type:
                results.append({
                    'categoryId': cid,
                    'categoryName': info['name'],
                    'parentType': parent_type,
                    'parentTypeName': PARENT_TYPE_NAMES[parent_type],
                })
        return results

    def get_all_categories(self) -> list[dict]:
        """Get all categories."""
        return [self.get_category(cid) for cid in self._map]

    def update_from_database(self, db_categories: list[dict]):
        """
        Update category mapping from database records.
        Expected format: [{'id': 101, 'category_name': '...', 'parent_type': 1}, ...]
        """
        new_map = {}
        for cat in db_categories:
            cat_id = cat['id']
            parent_type_id = cat['parent_type']
            parent_type = PARENT_TYPES.get(parent_type_id, 'other')
            new_map[cat_id] = {
                'name': cat['category_name'],
                'parent_type': parent_type,
            }
        self._map = new_map
        logger.info(f'Category map updated from DB: {len(new_map)} categories loaded')


# Global singleton
_category_mapper: Optional[CategoryMapper] = None


def get_category_mapper() -> CategoryMapper:
    """Get or create the global CategoryMapper singleton."""
    global _category_mapper
    if _category_mapper is None:
        _category_mapper = CategoryMapper()
    return _category_mapper
