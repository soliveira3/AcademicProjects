import requests
import time
import json
import re
from collections import defaultdict
from typing import List, Set, Dict, Tuple
from urllib.parse import urlencode



class USDAIngredientScraper:
    def __init__(self, api_key: str = "DEMO_KEY", delay: float = 0.1):
        self.api_key = api_key
        self.base_url = "https://api.nal.usda.gov/fdc/v1"
        self.delay = delay
        self.adjacency_list: Dict[str, Set[str]] = defaultdict(set)
        self.products_scraped = []
        self.api_calls = 0
        self.failed_products = []
        self.rate_limited = False



    def normalize_ingredient(self, ingredient: str) -> str:
        ingredient = re.sub(r'\([^)]*\)', '', ingredient)
        ingredient = re.sub(r'\[[^\]]*\]', '', ingredient)
        ingredient = re.sub(r'contains?\s+(?:less\s+than\s+)?\d+%\s*(?:or\s*)?(?:less\s*)?(?:of:?)?', '', ingredient, flags=re.IGNORECASE)
        ingredient = re.sub(r'\d+%\s*(?:or\s*)?(?:less\s*)?(?:of:?)?', '', ingredient, flags=re.IGNORECASE)
        ingredient = ingredient.strip().lower()
        ingredient = ingredient.replace('"', '')
        ingredient = ingredient.replace('(', '')
        ingredient = ingredient.replace(')', '')
        ingredient = ingredient.replace('*', '')
        ingredient = ingredient.replace('+', '')
        ingredient = ingredient.replace('.', '')
        ingredient = ingredient.replace('fried in', '')
        ingredient = ingredient.replace('&', ' and ')
        ingredient = ingredient.replace('/', ' ')
        qualifiers = ['organic', 'enriched', 'refined', 'pure', 'fresh', 'raw',
                        'whole', 'natural', 'unbleached', 'bleached', 'pasteurized',
                        'dried', 'powdered', 'ground', 'chopped', 'sliced']
        for qual in qualifiers:
            ingredient = re.sub(r'\b' + qual + r'\b', '', ingredient)
        ingredient = ingredient.rstrip('.,;:*')
        ingredient = ' '.join(ingredient.split())
        ingredient = re.sub(r'\b(and|or|with|added|including|to preserve|for|as|a)\b', '', ingredient)
        ingredient = ' '.join(ingredient.split())

        return ingredient



    def search_foods(self, query: str = "", page_size: int = 200, page_number: int = 1, data_type: List[str] = None) -> Dict:
        endpoint = f"{self.base_url}/foods/search"
        params = {
            "api_key": self.api_key,
            "pageSize": min(page_size, 200),
            "pageNumber": page_number,
        }

        if query: params["query"] = query

        if data_type: params["dataType"] = ",".join(data_type)

        try:
            time.sleep(self.delay)
            self.api_calls += 1
            response = requests.get(endpoint, params=params, timeout=30)
            if response.status_code == 429:
                print(f"RATE LIMITED!")
                self.rate_limited = True
                return {}
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return {}



    def parse_ingredients(self, ingredient_text: str, include_everything: bool = False) -> List[str]:
        if not ingredient_text:
            return []

        ingredient_text = re.sub(r'^ingredients?:\s*', '', ingredient_text, flags=re.IGNORECASE)

        parenthetical_items = []
        for match in re.finditer(r'\(([^)]+)\)', ingredient_text):
            content = match.group(1)

            items = re.split(r'[,;]', content)
            parenthetical_items.extend(items)

        text_without_parens = re.sub(r'\([^)]*\)', '', ingredient_text)

        raw_ingredients = re.split(r'[,;]', text_without_parens)

        all_raw_ingredients = raw_ingredients + parenthetical_items

        ingredients = []
        for ing in all_raw_ingredients:
            normalized = self.normalize_ingredient(ing)

            if include_everything:
                if normalized and len(normalized) > 0:
                    ingredients.append(normalized)
            else:
                # Normal filtering
                if normalized and len(normalized) > 2:
                    # Skip common non-ingredients
                    skip_terms = ['contains', 'may contain', 'ingredients', 'less than', 'made in', 'produced', 'manufactured', 'distributed']
                    if not any(term in normalized for term in skip_terms):
                        ingredients.append(normalized)

        return ingredients



    def build_adjacency_list(self, ingredients: List[str]):
        # Create edges between all pairs
        for i, ing1 in enumerate(ingredients):
            for ing2 in ingredients[i+1:]:
                if ing1 != ing2:  # Avoid self-loops
                    self.adjacency_list[ing1].add(ing2)
                    self.adjacency_list[ing2].add(ing1)



    def scrape_all_foods_with_ingredients(self, max_foods: int = 500, debug: bool = True, include_everything: bool = False):
        # General food categories that usually have ingredient lists
        # Covers a wide variety of food types for comprehensive scraping
        categories = [
            "bread", "cereal", "pasta", "rice", "oatmeal", "granola",
            "tortilla", "bagel", "muffin", "cake", "pie", "cookie", "cracker",
            "waffle", "pancake", "biscuit", "roll", "croissant",
            # Snacks & Sweets
            "chip", "pretzel", "popcorn", "snack", "candy", "chocolate",
            "gum", "bar", "trail mix", "nuts", "jerky",
            # Dairy & Alternatives
            "milk", "cheese", "yogurt", "butter", "cream", "ice cream",
            "soy milk", "almond milk", "cottage cheese",
            # Condiments & Sauces
            "sauce", "salsa", "ketchup", "mustard", "mayo", "dressing",
            "marinade", "gravy", "relish", "jam", "jelly", "honey",
            "syrup", "oil", "vinegar", "seasoning", "spice",
            # Beverages
            "soda", "juice", "tea", "coffee", "energy drink", "sports drink",
            "water", "lemonade", "smoothie",
            # Prepared Meals & Frozen Foods
            "pizza", "burger", "sandwich", "wrap", "burrito", "taco",
            "soup", "stew", "chili", "meal", "dinner", "entree",
            "frozen", "microwave", "instant",
            # Meat & Protein
            "chicken", "beef", "pork", "turkey", "bacon", "sausage",
            "ham", "hot dog", "deli meat", "fish", "seafood", "tofu",
            # Vegetables & Fruits (processed)
            "salad", "coleslaw", "pickles", "canned", "dried fruit",
            # Breakfast Foods
            "egg", "breakfast", "sausage", "hash brown",
            # Baby & Special Diet
            "baby food", "protein", "organic", "gluten free", "vegan"
        ]


        print(f"Scraping foods with ingredients from USDA FoodData Central")
        print(f"Target: {max_foods} total foods")
        print(f"API Key: {self.api_key}")
        print(f"Delay: {self.delay}s between requests")
        print("=" * 70)


        foods_per_category = 25
        total_processed = 0

        for idx, category in enumerate(categories, 1):
            if total_processed >= max_foods or self.rate_limited:
                break

            print(f"\n[{idx}/{len(categories)}] Category: {category}")

            result = self.search_foods(
                query=category,
                page_size=200,
                page_number=1,
                data_type=["Branded"]
            )

            if not result or 'foods' not in result:
                continue

            foods = result.get('foods', [])
            found_in_category = 0

            if debug:
                print(f"  Found {len(foods)} foods in search results (taking up to {foods_per_category})")

            for food in foods[:foods_per_category]:  # Limit to foods_per_category
                if total_processed >= max_foods:
                    break

                ingredients_text = food.get('ingredients', '')

                if not ingredients_text:
                    continue

                # Parse ingredients
                ingredients = self.parse_ingredients(ingredients_text, include_everything=include_everything)

                if ingredients and len(ingredients) >= 2:  # Need at least 2 ingredients
                    fdc_id = food.get('fdcId')
                    description = food.get('description', 'Unknown')

                    self.products_scraped.append({
                        'fdc_id': fdc_id,
                        'description': description,
                        'category': category,
                        'ingredients': ingredients,
                        'ingredient_count': len(ingredients),
                        'raw_ingredients': ingredients_text[:200]  # Store first 200 chars for debugging
                    })

                    self.build_adjacency_list(ingredients)
                    found_in_category += 1
                    total_processed += 1

                    if debug and found_in_category == 1:
                        # Show first product as example
                        print(f"  Example: {description[:50]}")
                        print(f"    Ingredients: {', '.join(ingredients[:5])}...")

            print(f"  ✓ Found {found_in_category} products with ingredients")
            print(f"  Total so far: {total_processed} products, {len(self.adjacency_list)} unique ingredients")

            if self.rate_limited:
                print("\nRate limited!")
                break

        print("\n" + "=" * 70)
        print(f"Scraping complete!")
        print(f"  Products processed: {len(self.products_scraped)}")
        print(f"  Unique ingredients: {len(self.adjacency_list)}")
        print(f"  Total edges: {sum(len(v) for v in self.adjacency_list.values()) // 2}")
        print(f"  API calls made: {self.api_calls}")

        if self.rate_limited:
            print("\nrate limited")



    def save_edge_list_with_weights(self, filename: str = 'ingredient_pairs_weighted.txt'):
        pair_counts = defaultdict(int)

        for product in self.products_scraped:
            ingredients = product['ingredients']

            for i, ing1 in enumerate(ingredients):
                for ing2 in ingredients[i+1:]:
                    pair = tuple(sorted([ing1, ing2]))
                    pair_counts[pair] += 1

        sorted_pairs = sorted(pair_counts.items(), key=lambda x: (-x[1], x[0]))

        with open(filename, 'w', encoding='utf-8') as f:
            for (ing1, ing2), count in sorted_pairs:
                f.write(f"{ing1} | {ing2} | {count}\n")

        print(f"  Total unique pairs: {len(sorted_pairs)}")



    def print_statistics(self):
        print(f"\nOverall Stats:")
        print(f"  Total Products: {len(self.products_scraped)}")
        print(f"  Unique Ingredients: {len(self.adjacency_list)}")
        print(f"  Total Connections: {sum(len(v) for v in self.adjacency_list.values()) // 2}")



# Example usage
if __name__ == "__main__":

    scraper = USDAIngredientScraper(api_key="HlP5zVShIS6aUt9EAoAWeKLvxkrbxRsSgd4IZ7qK", delay=0.1)

    print()
    print("\n" + "=" * 70)
    print("\n" + "=" * 70)
    print()

    scraper.scrape_all_foods_with_ingredients(max_foods=10000, include_everything=True)
    scraper.print_statistics()
    scraper.save_edge_list_with_weights('ingredient_pairs_weighted.txt')