"""
Chronicling America Newspaper Scraper
Scrapes search results from the Library of Congress Chronicling America website
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from urllib.parse import urljoin, quote
import time


class ChroniclingAmericaScraper:
    """Scraper for Library of Congress Chronicling America newspaper archives"""
    
    BASE_URL = "https://www.loc.gov"
    SEARCH_URL = "https://www.loc.gov/search/"
    
    def __init__(self, output_dir="newspaper_results"):
        """
        Initialize the scraper
        
        Args:
            output_dir: Directory to save newspaper results
        """
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def search_newspapers(self, search_terms, max_results=100, date_from='1806', date_to='1865'):
        """
        Search for newspapers with given terms
        
        Args:
            search_terms: List of terms to search for (e.g., ['union', 'petigru'])
            max_results: Maximum number of results to retrieve
            date_from: Start date (year) for search range
            date_to: End date (year) for search range
            
        Returns:
            List of newspaper result dictionaries
        """
        # Build search query
        query = ' AND '.join([f'"{term}"' if ' ' in term else term for term in search_terms])
        
        print(f"Searching for: {query}")
        print(f"Date range: {date_from}-{date_to}")
        print(f"Maximum results: {max_results}")
        
        results = []
        page = 1
        
        while len(results) < max_results:
            # LOC API parameters
            params = {
                'q': query,
                'dates': f'{date_from}/{date_to}',
                'fa': 'partof:chronicling america',
                'sp': page,
                'fo': 'json'
            }
            
            try:
                print(f"\nFetching page {page}...")
                response = self.session.get(self.SEARCH_URL, params=params, timeout=30)
                response.raise_for_status()
                
                # Check if response is JSON
                content_type = response.headers.get('Content-Type', '')
                if 'application/json' not in content_type:
                    print(f"Warning: Response is not JSON. Got: {content_type}")
                    break
                
                data = response.json()
                
                # Check for results in the response
                # LOC API uses 'results' not 'items'
                if 'results' not in data or len(data['results']) == 0:
                    print("No more results found.")
                    break
                
                items = data['results']
                print(f"Found {len(items)} results on this page")
                
                # Process each result
                for item in items:
                    if len(results) >= max_results:
                        break
                    
                    result = self._parse_result(item)
                    results.append(result)
                    print(f"  - {result['title']} ({result['date']})")
                
                # Check if there are more pages
                if len(items) < 20:  # Typically 20 results per page
                    break
                
                page += 1
                time.sleep(1)  # Be respectful to the server
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching page {page}: {e}")
                break
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {e}")
                break
        
        print(f"\nTotal results retrieved: {len(results)}")
        return results
    
    def _parse_result(self, item):
        """Parse a single search result item from LOC API"""
        result = {
            'id': item.get('id', ''),
            'title': item.get('title', ''),
            'date': item.get('date', ''),
            'description': item.get('description', []),
            'url': item.get('url', ''),
            'image_url': item.get('image_url', []),
            'original_format': item.get('original_format', []),
            'subjects': item.get('subject', []),
            'location': item.get('location', []),
            'timestamp': datetime.now().isoformat()
        }
        return result
    
    def save_results(self, results, prefix="newspaper"):
        """
        Save results to individual JSON files
        
        Args:
            results: List of result dictionaries
            prefix: Prefix for output filenames
            
        Returns:
            List of saved filenames
        """
        saved_files = []
        
        print(f"\nSaving {len(results)} results to {self.output_dir}/")
        
        for idx, result in enumerate(results, 1):
            # Create a safe filename from date and title
            date_str = result['date'].replace('-', '')
            title_safe = "".join(c for c in result['title'][:30] if c.isalnum() or c in (' ', '-', '_')).strip()
            title_safe = title_safe.replace(' ', '_')
            
            filename = f"{prefix}_{date_str}_{title_safe}_{idx}.json"
            filepath = os.path.join(self.output_dir, filename)
            
            # Save to JSON file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            saved_files.append(filepath)
        
        print(f"Saved {len(saved_files)} files")
        return saved_files
    
    def save_summary(self, results, filename="search_summary.json"):
        """Save a summary of all results to a single file"""
        filepath = os.path.join(self.output_dir, filename)
        
        summary = {
            'search_date': datetime.now().isoformat(),
            'total_results': len(results),
            'results': results
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"Saved summary to {filepath}")
        return filepath
    
    def download_newspaper_page(self, result, format='pdf'):
        """
        Download the actual newspaper page
        
        Args:
            result: Result dictionary containing newspaper metadata
            format: Format to download ('pdf', 'jp2', 'txt')
        """
        # Extract LCCN and date information to construct download URL
        url = result.get('url', '')
        if not url:
            print("No URL found for this result")
            return None
        
        # The URL typically looks like: /lccn/sn84026897/1862-08-23/ed-1/seq-1/
        # We can append the format extension
        download_url = f"{url}{format}/"
        
        try:
            response = self.session.get(download_url, timeout=30)
            response.raise_for_status()
            
            # Create filename
            date_str = result['date'].replace('-', '')
            title_safe = "".join(c for c in result['title'][:30] if c.isalnum() or c in (' ', '-', '_')).strip()
            title_safe = title_safe.replace(' ', '_')
            
            filename = f"page_{date_str}_{title_safe}.{format}"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"Downloaded: {filename}")
            return filepath
            
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {format} for {result['title']}: {e}")
            return None


def main():
    """Main function to run the scraper"""
    
    print("=" * 60)
    print("Chronicling America Newspaper Scraper")
    print("=" * 60)
    
    # Initialize scraper
    scraper = ChroniclingAmericaScraper(output_dir="newspaper_results")
    
    # Search for newspapers with 'union' and 'petigru'
    search_terms = ['union', 'petigru']
    results = scraper.search_newspapers(search_terms, max_results=50)
    
    if results:
        # Save individual results
        saved_files = scraper.save_results(results, prefix="union_petigru")
        
        # Save summary
        scraper.save_summary(results, filename="union_petigru_summary.json")
        
        print("\n" + "=" * 60)
        print(f"Successfully scraped {len(results)} newspaper results!")
        print(f"Files saved to: {scraper.output_dir}/")
        print("=" * 60)
        
        # Ask if user wants to download actual newspaper pages
        print("\nTo download actual newspaper pages (PDF/images), you can:")
        print("1. Use scraper.download_newspaper_page(result, format='pdf')")
        print("2. Modify this script to download automatically")
    else:
        print("\nNo results found.")


if __name__ == "__main__":
    main()
